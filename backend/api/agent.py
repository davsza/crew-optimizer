from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .models import Message
import json
from pydantic import BaseModel
from langchain.tools import StructuredTool
from .utils.constants import USER_INIT_MSG, ADMIN_INIT_MSG, SUMMARIZATION_DESC, GET_CURRENT_DATETIME_DESCRIPTION, GET_WEEKNUMBER_DESCRIPTION, GET_APPLICATION_CHANGE_DESCRIPTION, GET_SAVE_APPLICATION_MODIFICATION_DESCRIPTION, GET_DROP_MODIFICATION_DESCRIPTION, GET_CURRENT_MODIFICATION_DESCRIPTION, GET_SCHEDULE_OPTIMIZER_DESCRIPTION
from .utils.agent_functions import get_current_week, is_weekend, get_supervisor_group, get_admin_users, user_in_group, get_roster_by_week, get_past_messages, is_empty_binary_roster, get_default_binary_roster, convert_string_to_json, convert_json_to_string, get_summary, order_json_by_days, get_roster, complement_roster, overwrite_binary, get_users_without_application, get_users_without_application
from .solver import solve

load_dotenv()

user = None
week_number = -1


class RosterUpdateInputSchema(BaseModel):
    user_input: str


class RosterUpdateOutputSchema(BaseModel):
    agent_output: str


def save_roster():
    roster = get_roster(user, week_number)
    if is_empty_binary_roster(roster.modification, 'x'):
        return f"You don't have any ongoing modifications, nothing to save!"
    else:
        roster.application = overwrite_binary(
            roster.modification, roster.application)
        roster.modification = get_default_binary_roster('x')
        roster.save()
        return "You successfully saved your application. If you have any questions or want to modify it feel free to ask!"


def drop_modification():
    roster = get_roster(user, week_number)
    if is_empty_binary_roster(roster.modification):
        return f"You don't have any ongoing modifications, nothing to drop!"
    else:
        roster.modification = get_default_binary_roster()
        roster.save()
        return "You successfully dropped your ongoing modifications. If you have any questions or want to modify it feel free to ask!"


def get_week_number_for_application():
    return get_current_week(2)


def get_current_date_time():
    import datetime

    current_date = datetime.datetime.now()
    return current_date


def get_application_summarization():
    roster = get_roster(user, week_number)
    application = roster.application
    application_json_raw = convert_string_to_json(application)
    application_json = json.loads(application_json_raw)
    summary = get_summary(application_json)
    return summary


def get_modification_summarization():
    roster = get_roster(user, week_number)
    modification = roster.modification
    modification_json_raw = convert_string_to_json(modification)
    modification_json = json.loads(modification_json_raw)
    summary = get_summary(None, None, modification_json)
    return summary


def change_schedule(user_request: str) -> RosterUpdateOutputSchema:
    roster = get_roster(user, week_number)
    binary_application = roster.application
    application_json_raw = convert_string_to_json(binary_application)
    application_json = json.loads(application_json_raw)
    # if there was any, something like "xx11x0xxxxxxxxx0xx1xx", "xxxxxxxxxxxxxxxxxxxxx" otherwise
    binary_modification = roster.modification

    input_data = {"question": user_request}
    response = agent_executor_converter.invoke(input_data)
    change_request = response["output"]
    change_request = order_json_by_days(change_request)  # order by day

    change_request_json = json.dumps(
        {"roster": change_request}, indent=4)

    full_change_request_json = complement_roster(
        change_request_json)  # true, false, null json

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


def schedule_optimizer():
    ret_val = get_users_without_application()
    warning_msg = ""
    if len(ret_val) == 2:
        warning_msg = ret_val[1]
    solve()
    return "Successful optimizing! " + warning_msg


admin_tools = [
    StructuredTool.from_function(
        func=schedule_optimizer,
        name="Schedule optimizing",
        description=GET_SCHEDULE_OPTIMIZER_DESCRIPTION,
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
        func=get_week_number_for_application,
        name="Get week number for application week",
        description=GET_WEEKNUMBER_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=get_current_date_time,
        name="Get current date/time",
        description=GET_CURRENT_DATETIME_DESCRIPTION,
    ),
]

converter_tools = []

prompt = hub.pull("davsza/crew-optimizer")
converter_prompt = hub.pull("davsza/crew-optimizer-converter")

llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0)
user_agent = create_structured_chat_agent(
    llm=llm, tools=user_tools, prompt=prompt)
admin_agent = create_structured_chat_agent(
    llm=llm, tools=admin_tools, prompt=prompt)
converter_agent = create_structured_chat_agent(
    llm=llm, tools=converter_tools, prompt=converter_prompt)


agent_executor_converter = AgentExecutor.from_agent_and_tools(
    agent=converter_agent,
    tools=converter_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
)


def call_agent(request):
    import datetime

    load_dotenv()

    global user
    global week_number

    message = request.data.get('text')
    user = request.user
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

    memory.chat_memory.add_message(HumanMessage(content=message))

    input_data = {"question": message}
    response = agent_executor.invoke(input_data)
    print("Bot:", response["output"])
    print('Response:', response)

    memory.chat_memory.add_message(AIMessage(content=response["output"]))

    msg = Message(text=response["output"], sent_by_user=False,
                  date=datetime.datetime.now(), owner=request.user)
    msg.save()
