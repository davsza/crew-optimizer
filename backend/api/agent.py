from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .models import Shift, Message
import json
from pydantic import BaseModel, constr, validator
from typing import Dict
from langchain.tools import StructuredTool
from .constants import INIT_MSG_FOR_AGENT, APPLICATION_GETTER_DESCRIPTION, APPLICATION_CONVERTER_DESCRIPTION, JSON_CONVERTER_DESCRIPTION, APPLICATION_SAVER_DESCRIPTION, GET_CURRENT_DATETIME_DESCRIPTION, GET_WEEKNUMBER_DESCRIPTION


load_dotenv()

user = None
week = -1


def get_past_messages(user):
    messages = Message.objects.filter(owner=user)
    return messages


def is_binary_string(schedule_string):
    return all(char in {'0', '1'} for char in schedule_string)


class ApplicationStringInput(BaseModel):
    application_string: constr(min_length=21, max_length=21)

    @validator("application_string")
    def check_binary_string(cls, value):
        if not all(char in '01' for char in value):
            raise ValueError("The string must contain only '0' and '1'.")
        return value


def convert_string_to_json(application_string: str) -> str:
    print('convert_string_to_json', application_string)
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    schedule = {}
    for i, day in enumerate(days):
        start_index = i * 3
        schedule[day] = {
            "morning": True if application_string[start_index] == "1" else False,
            "afternoon": True if application_string[start_index + 1] == "1" else False,
            "night": True if application_string[start_index + 2] == "1" else False
        }

    print('####', {"shift": schedule}, "####")

    return json.dumps({"shift": schedule}, indent=4)


class ShiftDaySchema(BaseModel):
    morning: bool = False
    afternoon: bool = False
    night: bool = False


class ShiftSchema(BaseModel):
    monday: ShiftDaySchema
    tuesday: ShiftDaySchema
    wednesday: ShiftDaySchema
    thursday: ShiftDaySchema
    friday: ShiftDaySchema
    saturday: ShiftDaySchema
    sunday: ShiftDaySchema

    @validator("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    def validate_day(cls, value):
        return value


def convert_json_to_string(shift_json: Dict[str, Dict[str, bool]]) -> str:
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    values_string = ""

    for day in days:
        shifts = shift_json["shift"].get(day, {})
        values_string += f"{shifts.get('morning', False)}{shifts.get('afternoon', False)}{shifts.get('night', False)}"

    return values_string


def get_shift():
    shift = Shift.objects.get(owner=user, week=week)
    return shift.applied_shift


def save_shift(application_string: str) -> str:
    shift = Shift.objects.get(owner=user, week=week)
    shift.applied_shift = application_string
    shift.save()


def get_week_number_for_application():
    import datetime

    today = datetime.date.today()
    start_of_current_week = today - datetime.timedelta(days=today.weekday())
    start_of_next_week = start_of_current_week + datetime.timedelta(weeks=2)
    _, next_next_week, _ = start_of_next_week.isocalendar()
    return next_next_week


def get_current_date_time():
    import datetime

    current_date = datetime.datetime.now()
    return current_date


tools = [
    StructuredTool.from_function(
        func=get_shift,
        name="Application getter",
        description=APPLICATION_GETTER_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=convert_string_to_json,
        name="Application converter",
        description=APPLICATION_CONVERTER_DESCRIPTION,
        input_schema=ApplicationStringInput,
    ),
    StructuredTool.from_function(
        func=convert_json_to_string,
        name="Json converter",
        description=JSON_CONVERTER_DESCRIPTION,
        input_schema=ShiftSchema,
    ),
    StructuredTool.from_function(
        func=save_shift,
        name="Application saver",
        description=APPLICATION_SAVER_DESCRIPTION,
        input_schema=ApplicationStringInput,
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
    )
]

prompt = hub.pull("davsza/crew-optimizer")

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)


def call_agent(request):
    import datetime

    load_dotenv()

    global user
    global week

    message = request.data.get('text')
    user = request.user
    week = get_week_number_for_application()

    msg = Message(text=message, sent_by_user=True,
                  date=request.data.get('date'), owner=user)
    msg.save()

    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True
    )

    initial_message = INIT_MSG_FOR_AGENT
    memory.chat_memory.add_message(SystemMessage(content=initial_message))

    past_messages = get_past_messages(user)
    for past_message in past_messages:
        message_type = HumanMessage if past_message.sent_by_user else SystemMessage
        memory.chat_memory.add_message(message_type(content=past_message.text))

    memory.chat_memory.add_message(HumanMessage(content=message))

    input_data = {"question": message}
    response = agent_executor.invoke(input_data)
    print("Bot:", response["output"])
    print(response)

    memory.chat_memory.add_message(AIMessage(content=response["output"]))

    msg = Message(text=response["output"], sent_by_user=False,
                  date=datetime.datetime.now(), owner=request.user)
    msg.save()
