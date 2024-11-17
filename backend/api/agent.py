import json
from datetime import datetime, timedelta
from typing import Any

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
    get_current_week_number,
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

USER = None
YEAR = -1
WEEK_NUMBER = -1


def save_roster() -> SaveRosterOutputSchema:
    """
    Saves the current modification to the user's schedule and resets the modification to the
    default schedule.

    This function checks if there are any modifications in the user's schedule. If modifications
    exist, it applies the modifications to the application and then resets the modification to the
    default state.
    If there are no modifications, it returns a message indicating there are no ongoing
    modifications.

    Args:
        None: This function does not take any external input parameters.

    Returns:
        SaveRosterOutputSchema: A schema containing a message indicating whether the modifications
        were successfully saved or if there were no ongoing modifications to save.

    Process:
        1. Retrieves the roster for the given user and week number.
        2. Checks if the current modification is uniform with a specified character (`CHAR_X`).
        3. If no modifications are present (uniform with `CHAR_X`), returns a message indicating no
           ongoing modifications.
        4. If there are modifications, applies the modification to the application, resets the
           modification to the default state, and saves the roster.
        5. Returns a success message after saving the roster.
    """
    roster = get_roster_by_user_and_week_number(USER, WEEK_NUMBER)
    if is_uniform_with_char(roster.modification, CHAR_X):
        return SaveRosterOutputSchema(agent_output=NO_ONGOINT_MODIFICATIONS)

    roster.application = overwrite_str_with_value(
        roster.modification, roster.application)
    roster.modification = get_default_schedule_str(CHAR_X)
    roster.save()
    return SaveRosterOutputSchema(agent_output=SUCCESSFUL_SAVE_MSG)


def drop_modification() -> DropModificationsOutputSchema:
    """
    Drops any modifications to a user's schedule, restoring the default schedule.

    This function checks if there are any modifications in the user's schedule for the specified
    week.
    If modifications exist, it restores the schedule to its default state, otherwise, it returns
    a message indicating there are no ongoing modifications.

    Args:
        None: This function does not take any external input parameters.

    Returns:
        DropModificationsOutputSchema: A schema containing a message indicating whether the
        modifications were dropped or if there were no ongoing modifications.

    Process:
        1. Retrieves the roster for the given user and week number.
        2. Checks if the current modification is uniform with a specified character (`CHAR_X`).
        3. If the modification is uniform (i.e., no active changes), returns a message indicating
           no ongoing modifications.
        4. If there are modifications, resets the modification to the default schedule and saves
           the roster.
        5. Returns a message indicating the successful drop of modifications.
    """
    roster = get_roster_by_user_and_week_number(USER, WEEK_NUMBER)
    if is_uniform_with_char(roster.modification, CHAR_X):
        return DropModificationsOutputSchema(agent_output=NO_ONGOINT_MODIFICATIONS)

    roster.modification = get_default_schedule_str(CHAR_X)
    roster.save()
    return DropModificationsOutputSchema(agent_output=SUCCESSFUL_DROP_MSG)


def get_application_summarization() -> SummaryOutputSchema:
    """
    Retrieves and summarizes the application data for a user's schedule.

    This function fetches the current application data for a user's schedule, processes it
    to generate a summary of the application, and returns the summary in a structured schema.

    Args:
        None: This function does not take any external input parameters.

    Returns:
        SummaryOutputSchema: A schema containing a summary of the schedule application.

    Process:
        1. Retrieves the roster for the given user and week number.
        2. Extracts the application data from the roster.
        3. Converts the application data from binary format to JSON.
        4. Generates a summary of the application.
        5. Returns the summary in a structured format (SummaryOutputSchema).
    """
    roster = get_roster_by_user_and_week_number(USER, WEEK_NUMBER)
    application = roster.application
    application_json_raw = convert_roster_string_to_json(application)
    application_json = json.loads(application_json_raw)
    msg = get_summary(application_json)
    return SummaryOutputSchema(agent_output=msg)


def get_modification_summarization() -> SummaryOutputSchema:
    """
    Retrieves and summarizes the modifications made to a user's schedule.

    This function fetches the current modification to the user's schedule and generates
    a summary of the changes made. The summary is then returned in a structured schema.

    Args:
        None: This function does not take any external input parameters.

    Returns:
        SummaryOutputSchema: A schema containing a summary of the schedule modifications.

    Process:
        1. Retrieves the roster for the user and week number.
        2. Extracts the modification from the roster.
        3. Converts the modification from binary format to JSON.
        4. Generates a summary of the modifications.
        5. Returns the summary in a structured format (SummaryOutputSchema).
    """
    roster = get_roster_by_user_and_week_number(USER, WEEK_NUMBER)
    modification = roster.modification
    modification_json_raw = convert_roster_string_to_json(modification)
    modification_json = json.loads(modification_json_raw)
    msg = get_summary(None, None, modification_json)
    return SummaryOutputSchema(agent_output=msg)


def change_schedule(user_request: str) -> RosterUpdateOutputSchema:
    """
    Changes a user's schedule based on a given request.

    This function processes a user's request to modify their schedule:
    1. Retrieves the current roster for the user and week number.
    2. Parses the application data to JSON format.
    3. Sends the user's request to an external agent to get the requested changes.
    4. Orders and processes the change request.
    5. Applies the modifications to the roster and updates the record.
    6. Generates a summary of the changes and returns it.

    Args:
        user_request (str): The user's request to change their schedule, containing details of the
        desired changes.

    Returns:
        RosterUpdateOutputSchema: A schema containing a summary of the applied changes to the
        roster.

    Process:
        1. Retrieves and parses the current schedule.
        2. Sends the request to an agent for processing.
        3. Modifies the schedule based on the request.
        4. Saves the updated roster with the new modifications.
        5. Generates and returns a summary of the changes.
    """
    roster = get_roster_by_user_and_week_number(USER, WEEK_NUMBER)
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
    """
    Processes a user's vacation or sickness claim request.

    This function handles both vacation and sickness claims by:
    1. Parsing the user's request to extract vacation or sickness data.
    2. Verifying if the claim date is within the allowed range.
    3. Calculating the length of the claim and ensuring it is valid.
    4. Returning the appropriate status message for the claim.

    Args:
        user_request (str): The user's request containing the vacation or sickness claim
        information.

    Returns:
        VacationSicknessClaimOutputSchema: A schema containing the status message of the claim
        process.
    
    Process:
        1. Sends the user's request to an external agent to get details about the vacation or
           sickness.
        2. Deserializes the response and retrieves important dates and claim details.
        3. Checks if the claim date is valid based on the mode (vacation or sickness) and the start
           date.
        4. If valid, the function proceeds to process the vacation or sickness claim and returns a
           response.
        5. If invalid, it returns an appropriate warning message.
    """
    input_data = {"question": user_request}
    response = agent_executor_sickvac.invoke(input_data)
    vacation_request = response["output"]

    vacation_request_json = json.dumps(
        {"vacation_sick": vacation_request}, indent=4)

    start_date, end_date, claim, mode, _ = get_vacation_and_sick_data(
        vacation_request_json)
    first_day_for_application_week, _ = get_first_and_last_day_of_week(
        YEAR, WEEK_NUMBER)

    current_date = datetime.now().date()
    last_day_of_sick_week = start_date + timedelta(days=6 - start_date.weekday())

    if (
        (mode == "vacation" and start_date < first_day_for_application_week) or
        (mode == "sickness" and start_date < current_date)
    ):
        msg = get_vacation_and_sickess_claim_dates_wrong_warning_msg(
            mode, first_day_for_application_week, current_date, last_day_of_sick_week)
        return VacationSicknessClaimOutputSchema(agent_output=msg)

    _, week, first_day_of_week = start_date.isocalendar()
    claim_length = end_date - start_date
    claim_length = claim_length.days + 1

    msg = ""

    if mode == "vacation":
        msg = vacation_claim(USER, YEAR, week, first_day_of_week,
                             claim, claim_length, start_date, end_date)

    elif mode == "sickness":
        msg = sickness_claim(USER, YEAR, week, first_day_of_week,
                             claim_length, start_date, end_date, first_day_for_application_week)

    return VacationSicknessClaimOutputSchema(agent_output=msg)


def schedule_optimizer() -> ScheduleOptimizationOutputSchema:
    """
    Optimizes the work schedule based on certain constraints and conditions.

    This function retrieves users without shift applications, runs a schedule optimization 
    process, and returns a status message indicating whether the optimization was successful, 
    feasible, infeasible, or unresolved.

    Returns:
        ScheduleOptimizationOutputSchema: A schema object containing the optimization status
        message.

    Process:
        1. Retrieves a list of users who have not submitted shift applications.
        2. If there are exactly two users without applications, a warning message is generated.
        3. The `optimize_schedule` function is called to optimize the schedule.
        4. Based on the optimization status, the appropriate message is returned:
            - "OPTIMAL": Indicates the optimization was successful.
            - "FEASIBLE": The solution is feasible but may not be optimal.
            - "INFEASIBLE": No feasible solution was found.
            - "UNBOUNDED": The solution is unbounded (i.e., there is no upper bound to the
               solution).
            - "NOT_SOLVED": The solver was not able to solve the optimization problem.

    Returns:
        ScheduleOptimizationOutputSchema: Contains the message indicating the status of the
        optimization.
    """
    ret_val = get_users_without_application()
    warning_msg = ""

    if len(ret_val) == 2:
        warning_msg = ret_val[1]
    status, _, _ = optimize_schedule(15, 1)

    if status == pywraplp.Solver.OPTIMAL:
        msg = SOLVER_STATUS_OPTIMAL + " " + warning_msg
        return ScheduleOptimizationOutputSchema(agent_output=msg)

    if status == pywraplp.Solver.FEASIBLE:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_FEASIBLE)

    if status == pywraplp.Solver.INFEASIBLE:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_INFEASIBLE)

    if status == pywraplp.Solver.UNBOUNDED:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_UNBOUNDED)

    if status == pywraplp.Solver.NOT_SOLVED:
        return ScheduleOptimizationOutputSchema(agent_output=SOLVER_STATUS_NOT_SOLVED)


def reject_vacation(user_request: str) -> VacationRejectionOutputSchema:
    """
    Reject a vacation request for a specific user.

    This function processes a user's vacation request, determines the vacation details, and 
    rejects the request. It updates the system accordingly and provides a rejection message.

    Args:
        user_request (str): A user-provided vacation request in natural language or specific format.

    Returns:
        VacationRejectionOutputSchema: An object containing the output message for the rejection.

    Process:
        1. The user's request is sent to a vacation administration agent for processing.
        2. The response is parsed to extract vacation details (start date, end date, user, etc.).
        3. The vacation is marked as rejected in the system using the `vacation_claim` function.
        4. A rejection message is generated and returned.
    """
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

    vacation_claim(user_to_reject, YEAR, vacation_week_number,
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


def call_agent(request: Any) -> None:
    """
    Handles the incoming request, processes the message, and invokes the appropriate agent 
    to generate a response based on the user's role (Supervisor or general user).
    
    The function performs the following steps:
    1. Retrieves and processes the incoming request message.
    2. Initializes a memory buffer for the conversation history.
    3. Chooses the appropriate agent (admin or user) based on the user's role.
    4. Loads past conversation history into the memory.
    5. Sends the current message to the selected agent for a response.
    6. Saves the response and the entire conversation (including both user and system messages).
    
    Args:
        request (Any): The incoming request containing data like message text, user info, 
                        and request-specific metadata (such as date and user).
    
    Returns:
        None: This function doesn't return anything, it handles the request and 
              updates the database and conversation memory.
    """
    load_dotenv()

    global USER
    global YEAR
    global WEEK_NUMBER

    message = request.data.get('text')
    USER = request.user
    YEAR = current_year()
    WEEK_NUMBER = get_current_week_number(2)

    msg = Message(text=message, sent_by_user=True,
                  date=request.data.get('date'), owner=USER)
    msg.save()

    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)

    if is_user_in_group(USER, 'Supervisor'):
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

    past_messages = get_past_messages_by_user(USER)
    for past_message in past_messages:
        message_type = HumanMessage if past_message.sent_by_user else SystemMessage
        memory.chat_memory.add_message(message_type(content=past_message.text))

    input_data = {"question": message}
    response = agent_executor.invoke(input_data)
    print("Bot:", response["output"])
    print('Response:', response)

    memory.chat_memory.add_message(AIMessage(content=response["output"]))

    msg = Message(text=response["output"], sent_by_user=False,
                  date=datetime.datetime.now(), owner=request.user)
    msg.save()
