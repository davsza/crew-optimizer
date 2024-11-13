import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from ortools.linear_solver import pywraplp

from .models import Message
from .solver import optimize_schedule
from .utils.common_fn import (
    complement_roster,
    convert_json_to_roster_string,
    convert_roster_string_to_json,
    get_default_schedule_str,
    is_uniform_with_char,
    order_json_by_days,
    overwrite_str_with_value,
)
from .utils.constants import (
    ADMIN_INIT_MSG,
    CHAR_X,
    GET_APPLICATION_CHANGE_DESCRIPTION,
    GET_APPLICATION_FOR_VACATION_OR_SICKNESS_DESCRIPTION,
    GET_CURRENT_MODIFICATION_DESCRIPTION,
    GET_DROP_MODIFICATION_DESCRIPTION,
    GET_REJECT_VACATION_DESCRIPTION,
    GET_SAVE_APPLICATION_MODIFICATION_DESCRIPTION,
    GET_SCHEDULE_OPTIMIZER_DESCRIPTION,
    NO_ONGOINT_MODIFICATIONS,
    SOLVER_STATUS_FEASIBLE,
    SOLVER_STATUS_INFEASIBLE,
    SOLVER_STATUS_NOT_SOLVED,
    SOLVER_STATUS_OPTIMAL,
    SOLVER_STATUS_UNBOUNDED,
    SUCCESSFUL_DROP_MSG,
    SUCCESSFUL_SAVE_MSG,
    SUMMARIZATION_DESC,
    USER_INIT_MSG,
)
from .utils.date_time_fn import (
    current_year,
    get_current_week,
    get_first_and_last_day_of_week,
)
from .utils.message_fn import (
    get_summary,
    get_vacation_and_sickess_claim_dates_wrong_warning_msg,
    get_vacation_claim_rejection_by_admin_msg,
)
from .utils.model_fn import (
    get_past_messages_by_user,
    get_roster_by_user_and_week_number,
    get_users_without_application,
    is_user_in_group,
)
from .utils.schemas import (
    DropModificationsOutputSchema,
    RosterUpdateInputSchema,
    RosterUpdateOutputSchema,
    SaveRosterOutputSchema,
    ScheduleOptimizationOutputSchema,
    SummaryOutputSchema,
    VacationClaimInputSchema,
    VacationRejectionInputSchema,
    VacationRejectionOutputSchema,
    VacationSicknessClaimOutputSchema,
)
from .utils.vacation_sick_fn import (
    get_vacation_and_sick_data,
    sickness_claim,
    vacation_claim,
)


load_dotenv()

user = None
year_number = -1
week_number = -1


def save_roster() -> SaveRosterOutputSchema:
    roster = get_roster_by_user_and_week_number(user, week_number)
    if is_uniform_with_char(roster.modification, CHAR_X):
        return SaveRosterOutputSchema(agent_output=NO_ONGOINT_MODIFICATIONS)
    else:
        roster.application = overwrite_str_with_value(
            roster.modification, roster.application)
        roster.modification = get_default_schedule_str(CHAR_X)
        roster.save()
        return SaveRosterOutputSchema(agent_output=SUCCESSFUL_SAVE_MSG)


def drop_modification() -> DropModificationsOutputSchema:
    roster = get_roster_by_user_and_week_number(user, week_number)
    if is_uniform_with_char(roster.modification, CHAR_X):
        return DropModificationsOutputSchema(agent_output=NO_ONGOINT_MODIFICATIONS)
    else:
        roster.modification = get_default_schedule_str(CHAR_X)
        roster.save()
        return DropModificationsOutputSchema(agent_output=SUCCESSFUL_DROP_MSG)


def get_application_summarization() -> SummaryOutputSchema:
    roster = get_roster_by_user_and_week_number(user, week_number)
    application = roster.application
    application_json_raw = convert_roster_string_to_json(application)
    application_json = json.loads(application_json_raw)
    summary = get_summary(application_json)
    return SummaryOutputSchema(agent_output=summary)


def get_modification_summarization() -> SummaryOutputSchema:
    roster = get_roster_by_user_and_week_number(user, week_number)
    modification = roster.modification
    modification_json_raw = convert_roster_string_to_json(modification)
    modification_json = json.loads(modification_json_raw)
    summary = get_summary(None, None, modification_json)
    return SummaryOutputSchema(agent_output=summary)


def change_schedule(user_request: str) -> RosterUpdateOutputSchema:
    roster = get_roster_by_user_and_week_number(user, week_number)
    binary_application = roster.application
    application_json_raw = convert_roster_string_to_json(binary_application)
    application_json = json.loads(application_json_raw)
    binary_modification = roster.modification

    input_data = {"question": user_request}
    response = agent_executor_converter.invoke(input_data)
    change_request = response["output"]
    change_request = order_json_by_days(change_request)

    change_request_json = json.dumps(
        {"roster": change_request}, indent=4)

    full_change_request_json = complement_roster(
        change_request_json)

    binary_change_request = convert_json_to_roster_string(
        full_change_request_json, True)

    binary_modification = overwrite_str_with_value(
        binary_change_request, binary_modification)

    current_modification_json_raw = convert_roster_string_to_json(
        binary_change_request)
    current_modification_json = json.loads(current_modification_json_raw)

    full_modification_json_raw = convert_roster_string_to_json(
        binary_modification)
    full_modification_json = json.loads(full_modification_json_raw)

    roster.modification = binary_modification
    roster.save()

    summary = get_summary(
        application_json, current_modification_json, full_modification_json)

    return RosterUpdateOutputSchema(agent_output=summary)


def vacation_sickness_claim(user_request: str) -> VacationSicknessClaimOutputSchema:
    input_data = {"question": user_request}
    response = agent_executor_sickvac.invoke(input_data)
    vacation_request = response["output"]

    vacation_request_json = json.dumps(
        {"vacation_sick": vacation_request}, indent=4)

    start_date, end_date, claim, mode, _ = get_vacation_and_sick_data(
        vacation_request_json)
    first_day_for_application_week, _ = get_first_and_last_day_of_week(
        year, week_number)

    current_date = datetime.now().date()
    last_day_of_sick_week = start_date + \
        timedelta(days=(6 - start_date.weekday()))

    if (mode == "vacation" and start_date < first_day_for_application_week) \
            or (mode == "sickness" and start_date < current_date):  # or (mode == "sickness" and end_date > last_day_of_sick_week):
        msg = get_vacation_and_sickess_claim_dates_wrong_warning_msg(
            mode, first_day_for_application_week, current_date, last_day_of_sick_week)
        return VacationSicknessClaimOutputSchema(agent_output=msg)

    _, week, first_day_of_week = start_date.isocalendar()
    claim_length = end_date - start_date
    claim_length = claim_length.days + 1

    msg = ""

    if mode == "vacation":
        msg = vacation_claim(user, year, week, first_day_of_week,
                             claim, claim_length, start_date, end_date)
    elif mode == "sickness":
        msg = sickness_claim(user, year, week, first_day_of_week,
                             claim_length, start_date, end_date, first_day_for_application_week)

    return VacationSicknessClaimOutputSchema(agent_output=msg)


def schedule_optimizer() -> ScheduleOptimizationOutputSchema:
    ret_val = get_users_without_application()
    warning_msg = ""
    if len(ret_val) == 2:
        warning_msg = ret_val[1]
    status, _, _ = optimize_schedule(15, 1)

    if status == pywraplp.Solver.OPTIMAL:
        msg = SOLVER_STATUS_OPTIMAL + " " + warning_msg
        return ScheduleOptimizationOutputSchema(agent_output=msg)

    elif status == pywraplp.Solver.FEASIBLE:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_FEASIBLE)

    elif status == pywraplp.Solver.INFEASIBLE:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_INFEASIBLE)

    elif status == pywraplp.Solver.UNBOUNDED:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_UNBOUNDED)

    elif status == pywraplp.Solver.NOT_SOLVED:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_NOT_SOLVED)


def reject_vacation(user_request: str) -> VacationRejectionOutputSchema:
    input_data = {"question": user_request}
    response = agent_executor_vacation_admin.invoke(input_data)
    vacation_request = response["output"]
    vacation_request_json = json.dumps(
        {"vacation": vacation_request}, indent=4)
    start_date, end_date, _, user_to_reject = get_vacation_and_sick_data(
        vacation_request_json)
    vacation_length = end_date - start_date
    vacation_length = vacation_length.days + 1
    _, vacation_week_number, vacation_first_day_of_week = start_date.isocalendar()
    vacation_claim(user_to_reject, year, vacation_week_number,
                   vacation_first_day_of_week, False, vacation_length, start_date, end_date)
    msg = get_vacation_claim_rejection_by_admin_msg(
        user_to_reject.username, start_date, end_date)
    return VacationRejectionOutputSchema(agent_output=msg)


admin_tools = [
    StructuredTool.from_function(
        func=schedule_optimizer,
        name="Schedule optimizing",
        description=GET_SCHEDULE_OPTIMIZER_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=reject_vacation,
        name="Reject vacation",
        description=GET_REJECT_VACATION_DESCRIPTION,
        input_schema=VacationRejectionInputSchema
    ),
]

user_tools = [
    StructuredTool.from_function(
        func=get_application_summarization,
        name="Application summarization",
        description=SUMMARIZATION_DESC,
    ),
    StructuredTool.from_function(
        func=change_schedule,
        name="Modification",
        description=GET_APPLICATION_CHANGE_DESCRIPTION,
        input_schema=RosterUpdateInputSchema
    ),
    StructuredTool.from_function(
        func=get_modification_summarization,
        name="Current modification",
        description=GET_CURRENT_MODIFICATION_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=drop_modification,
        name="Drop ongoing modification",
        description=GET_DROP_MODIFICATION_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=save_roster,
        name="Application saving",
        description=GET_SAVE_APPLICATION_MODIFICATION_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=vacation_sickness_claim,
        name="Application for vacation or sickness",
        description=GET_APPLICATION_FOR_VACATION_OR_SICKNESS_DESCRIPTION,
        input_schema=VacationClaimInputSchema
    ),
]

converter_tools = []

vacation_sickness_tools = []

vacavtion_admin_tools = []

prompt = hub.pull("davsza/crew-optimizer")
converter_prompt = hub.pull("davsza/crew-optimizer-converter")
vacation_prompt = hub.pull("davsza/crew-optimizer-vacation")
vacation_admin_prompt = hub.pull("davsza/crew-optimizer-vacation-admin")

llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0)
user_agent = create_structured_chat_agent(
    llm=llm, tools=user_tools, prompt=prompt)
admin_agent = create_structured_chat_agent(
    llm=llm, tools=admin_tools, prompt=prompt)
converter_agent = create_structured_chat_agent(
    llm=llm, tools=converter_tools, prompt=converter_prompt)
sickvac_agent = create_structured_chat_agent(
    llm=llm, tools=vacation_sickness_tools, prompt=vacation_prompt)
vacation_agent_admin = create_structured_chat_agent(
    llm=llm, tools=vacavtion_admin_tools, prompt=vacation_admin_prompt)


agent_executor_converter = AgentExecutor.from_agent_and_tools(
    agent=converter_agent,
    tools=converter_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
)

agent_executor_sickvac = AgentExecutor.from_agent_and_tools(
    agent=sickvac_agent,
    tools=vacation_sickness_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
)

agent_executor_vacation_admin = AgentExecutor.from_agent_and_tools(
    agent=vacation_agent_admin,
    tools=vacavtion_admin_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
)


def call_agent(request):
    import datetime

    load_dotenv()

    global user
    global year
    global week_number

    message = request.data.get('text')
    user = request.user
    year = current_year()
    week_number = get_current_week(2)

    msg = Message(text=message, sent_by_user=True,
                  date=request.data.get('date'), owner=user)
    msg.save()

    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)

    if is_user_in_group(user, 'Supervisor'):
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=admin_agent,
            tools=admin_tools,
            verbose=True,
            memory=memory,
            handle_parsing_errors=True,
            max_iterations=5,
        )
        initial_message = ADMIN_INIT_MSG
    else:
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=user_agent,
            tools=user_tools,
            verbose=True,
            memory=memory,
            handle_parsing_errors=True,
            max_iterations=5,
        )
        initial_message = USER_INIT_MSG

    memory.chat_memory.add_message(SystemMessage(content=initial_message))

    past_messages = get_past_messages_by_user(user)
    for past_message in past_messages:
        message_type = HumanMessage if past_message.sent_by_user else SystemMessage
        memory.chat_memory.add_message(message_type(content=past_message.text))

    # memory.chat_memory.add_message(HumanMessage(content=message))

    input_data = {"question": message}
    response = agent_executor.invoke(input_data)
    print("Bot:", response["output"])
    print('Response:', response)

    memory.chat_memory.add_message(AIMessage(content=response["output"]))

    msg = Message(text=response["output"], sent_by_user=False,
                  date=datetime.datetime.now(), owner=request.user)
    msg.save()
