import json
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
from .utils.agent_functions import (
    complement_roster,
    convert_json_to_string,
    convert_string_to_json,
    current_year,
    first_day_of_week,
    get_claimed_vacation,
    get_current_week,
    get_dates_from_vacation_json,
    get_default_binary_roster,
    get_past_messages,
    get_roster,
    get_summary,
    get_users_without_application,
    is_empty_binary_roster,
    late_vacation_warning_msg,
    order_json_by_days,
    overwrite_binary,
    save_vacation_claim,
    too_much_claimed_vacation_warning_msg,
    user_in_group,
    vacation_claim_msg,
    vacation_claim_rejection_msg,
)
from .utils.constants import (
    ADMIN_INIT_MSG,
    CHAR_ONE,
    CHAR_X,
    CHAR_ZERO,
    GET_APPLICATION_CHANGE_DESCRIPTION,
    GET_APPLICATION_FOR_VACATION_DESCRIPTION,
    GET_CURRENT_MODIFICATION_DESCRIPTION,
    GET_DROP_MODIFICATION_DESCRIPTION,
    GET_REJECT_VACATION_DESCRIPTION,
    GET_SAVE_APPLICATION_MODIFICATION_DESCRIPTION,
    GET_SCHEDULE_OPTIMIZER_DESCRIPTION,
    MAX_VACATION_CLAM_PER_YEAR,
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
from .utils.schemas import (
    DropModificationsOutputSchema,
    RosterUpdateInputSchema,
    RosterUpdateOutputSchema,
    SaveRosterOutputSchema,
    ScheduleOptimizationOutputSchema,
    SummaryOutputSchema,
    VacationClaimInputSchema,
    VacationClaimOutputSchema,
    VacationRejectionInputSchema,
    VacationRejectionOutputSchema,
)


load_dotenv()

user = None
year_number = -1
week_number = -1


def save_roster() -> SaveRosterOutputSchema:
    roster = get_roster(user, week_number)
    if is_empty_binary_roster(roster.modification, CHAR_X):
        return SaveRosterOutputSchema(agent_output=NO_ONGOINT_MODIFICATIONS)
    else:
        roster.application = overwrite_binary(
            roster.modification, roster.application)
        roster.modification = get_default_binary_roster(CHAR_X)
        roster.save()
        return SaveRosterOutputSchema(agent_output=SUCCESSFUL_SAVE_MSG)


def drop_modification() -> DropModificationsOutputSchema:
    roster = get_roster(user, week_number)
    if is_empty_binary_roster(roster.modification, CHAR_X):
        return DropModificationsOutputSchema(agent_output=NO_ONGOINT_MODIFICATIONS)
    else:
        roster.modification = get_default_binary_roster(CHAR_X)
        roster.save()
        return DropModificationsOutputSchema(agent_output=SUCCESSFUL_DROP_MSG)


def get_application_summarization() -> SummaryOutputSchema:
    roster = get_roster(user, week_number)
    application = roster.application
    application_json_raw = convert_string_to_json(application)
    application_json = json.loads(application_json_raw)
    summary = get_summary(application_json)
    return SummaryOutputSchema(agent_output=summary)


def get_modification_summarization() -> SummaryOutputSchema:
    roster = get_roster(user, week_number)
    modification = roster.modification
    modification_json_raw = convert_string_to_json(modification)
    modification_json = json.loads(modification_json_raw)
    summary = get_summary(None, None, modification_json)
    return SummaryOutputSchema(agent_output=summary)


def change_schedule(user_request: str) -> RosterUpdateOutputSchema:
    roster = get_roster(user, week_number)
    binary_application = roster.application
    application_json_raw = convert_string_to_json(binary_application)
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

    binary_change_request = convert_json_to_string(
        full_change_request_json, True)

    binary_modification = overwrite_binary(
        binary_change_request, binary_modification)

    current_modification_json_raw = convert_string_to_json(
        binary_change_request)
    current_modification_json = json.loads(current_modification_json_raw)

    full_modification_json_raw = convert_string_to_json(binary_modification)
    full_modification_json = json.loads(full_modification_json_raw)

    roster.modification = binary_modification
    roster.save()

    summary = get_summary(
        application_json, current_modification_json, full_modification_json)

    return RosterUpdateOutputSchema(agent_output=summary)


def vacation_claim(user_request: str) -> VacationClaimOutputSchema:
    input_data = {"question": user_request}
    response = agent_executor_vacation.invoke(input_data)
    vacation_request = response["output"]

    vacation_request_json = json.dumps(
        {"vacation": vacation_request}, indent=4)

    start_date, end_date, claim, _ = get_dates_from_vacation_json(
        vacation_request_json)

    first_day_for_application_week = first_day_of_week(year, week_number)

    if start_date < first_day_for_application_week:
        msg = late_vacation_warning_msg(first_day_for_application_week)
        return VacationClaimOutputSchema(agent_output=msg)

    _, vacation_week_number, vacation_first_day_of_week = start_date.isocalendar()
    vacation_length = end_date - start_date
    vacation_length = vacation_length.days + 1
    claimed_vacation = get_claimed_vacation(user, year)

    if claim and claimed_vacation + vacation_length > MAX_VACATION_CLAM_PER_YEAR:
        msg = too_much_claimed_vacation_warning_msg(
            vacation_length, MAX_VACATION_CLAM_PER_YEAR, claimed_vacation)
        return VacationClaimOutputSchema(agent_output=msg)

    if claim:
        replace_with = CHAR_ONE
    else:
        replace_with = CHAR_ZERO

    save_vacation_claim(user, vacation_week_number,
                        vacation_first_day_of_week, vacation_length, replace_with)

    msg = vacation_claim_msg(claim, start_date, end_date)
    return VacationClaimOutputSchema(agent_output=msg)


def schedule_optimizer() -> ScheduleOptimizationOutputSchema:
    ret_val = get_users_without_application()
    warning_msg = ""
    if len(ret_val) == 2:
        warning_msg = ret_val[1]
    status, _ = optimize_schedule()

    if status == pywraplp.Solver.OPTIMAL:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_OPTIMAL + warning_msg)

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
    start_date, end_date, _, user_to_reject = get_dates_from_vacation_json(
        vacation_request_json)
    vacation_length = end_date - start_date
    vacation_length = vacation_length.days + 1
    _, vacation_week_number, vacation_first_day_of_week = start_date.isocalendar()
    replace_with = CHAR_ZERO
    save_vacation_claim(user_to_reject, vacation_week_number,
                        vacation_first_day_of_week, vacation_length, replace_with)
    msg = vacation_claim_rejection_msg(user_to_reject.username)
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
        func=vacation_claim,
        name="Application for vacation",
        description=GET_APPLICATION_FOR_VACATION_DESCRIPTION,
        input_schema=VacationClaimInputSchema
    ),
]

converter_tools = []

vacation_tools = []

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
vacation_agent = create_structured_chat_agent(
    llm=llm, tools=vacation_tools, prompt=vacation_prompt)
vacation_agent_admin = create_structured_chat_agent(
    llm=llm, tools=vacation_tools, prompt=vacation_admin_prompt)


agent_executor_converter = AgentExecutor.from_agent_and_tools(
    agent=converter_agent,
    tools=converter_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
)

agent_executor_vacation = AgentExecutor.from_agent_and_tools(
    agent=vacation_agent,
    tools=vacation_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
)

agent_executor_vacation_admin = AgentExecutor.from_agent_and_tools(
    agent=vacation_agent_admin,
    tools=vacation_tools,
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

    if user_in_group(user, 'Supervisor'):
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

    past_messages = get_past_messages(user)
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
