from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .models import Shift, Message
import json
from langchain.tools import StructuredTool
from .constants import INIT_MSG_FOR_AGENT, APPLICATION_GETTER_DESCRIPTION, APPLICATION_CONVERTER_DESCRIPTION, JSON_CONVERTER_DESCRIPTION, APPLICATION_SAVER_DESCRIPTION, GET_CURRENT_DATETIME_DESCRIPTION, GET_WEEKNUMBER_DESCRIPTION


load_dotenv()

user = None
week = -1


def get_past_messages(user):
    """
    Retrieves all past messages associated with a given user.

    Args:
        user (User): The user for whom the past messages are being retrieved. 
                    This is typically a User model instance that represents the owner of the messages.

    Returns:
        QuerySet: A QuerySet containing all messages that are associated with the given user. 
                  The messages are retrieved from the 'Message' model, and the 'owner' field 
                  is used to filter the messages belonging to the provided user.

    Example:
        user = User.objects.get(username="john_doe")
        past_messages = get_past_messages(user)
    """
    messages = Message.objects.filter(owner=user)
    return messages


def is_binary_string(schedule_string):
    """
    Checks whether the given string contains only '0' and '1' characters.

    Args:
        schedule_string (str): The input string to check. This string represents a 
                               sequence that is expected to contain only binary characters ('0' and '1').

    Returns:
        bool: Returns True if the string consists only of '0' and '1' characters, 
              otherwise returns False.

    Example:
        result = is_binary_string("010101")  # True
        result = is_binary_string("10201")   # False
    """
    return all(char in {'0', '1'} for char in schedule_string)


def convert_string_to_json(*args):
    """
    Converts a binary schedule string into a structured JSON object representing shifts for each day of the week.

    Args:
        *args (tuple): A variable-length tuple of strings. The function expects one of the strings to be a 21-character binary string, 
                       where each character is either '0' or '1'. This binary string represents shift availability for each day 
                       of the week (morning, afternoon, and night shifts for Monday through Sunday).

    Raises:
        ValueError: If the input is not a tuple or if no valid 21-character binary string is found in the tuple.

    Returns:
        str: A JSON string representing the schedule, with each day of the week as a key, and the values being dictionaries
             indicating availability for the morning, afternoon, and night shifts (as 0 or 1).

    Example:
        input_string = "110100111000101010111"
        result = convert_string_to_json(input_string)
        # Resulting JSON structure:
        # {
        #     "shift": {
        #         "monday": {"morning": 1, "afternoon": 1, "night": 0},
        #         "tuesday": {"morning": 1, "afternoon": 0, "night": 0},
        #         "wednesday": {"morning": 1, "afternoon": 1, "night": 1},
        #         "thursday": {"morning": 0, "afternoon": 0, "night": 0},
        #         "friday": {"morning": 1, "afternoon": 0, "night": 1},
        #         "saturday": {"morning": 0, "afternoon": 1, "night": 0},
        #         "sunday": {"morning": 1, "afternoon": 1, "night": 1}
        #     }
        # }
    """
    print("--convert_string_to_json", args)

    application_string = ""
    found = False

    if isinstance(args, tuple):
        for item in args:
            if len(item) == 21 and is_binary_string(item):
                application_string = item
                found = True

    if not found or not isinstance(args, tuple):
        raise ValueError(
            'Invalid input provided, please try again passing a tuple to the function with the application string in it')

    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    schedule = {}
    for i, day in enumerate(days):
        start_index = i * 3
        schedule[day] = {
            "morning": int(application_string[start_index]),
            "afternoon": int(application_string[start_index + 1]),
            "night": int(application_string[start_index + 2])
        }

    return json.dumps({"shift": schedule}, indent=4)


def convert_json_to_string(*args):
    """
    Converts a tuple containing a JSON string of shift schedules into a concatenated string of shift values.

    Args:
        *args: A variable-length argument list. The first element should be a JSON-formatted string
               representing shift schedules for days of the week.

    Returns:
        str: A concatenated string of shift values (morning, afternoon, night) for each day of the week.
             For example, if the shift data for Monday is morning: 1, afternoon: 2, night: 3, 
             the result will contain "123".

    Raises:
        ValueError: If the input is not a tuple or if the JSON string is invalid.

    Example:
        json_input = '{"shift": {"monday": {"morning": 1, "afternoon": 2, "night": 3}}}'
        result = convert_json_to_string((json_input,))
        print(result)  # Output: '123000000000000'
    """
    print("--convert_json_to_string", args)

    shift_json = ""
    found = False

    if type(args) == tuple:
        shift_json, *rest = args
        try:
            json.loads(shift_json)
            found = True
        except ValueError:
            raise ValueError(
                'Invalid input provided, please try again passing a tuple with a valid JSON format.')

    if not found or not type(args) == tuple:
        raise ValueError(
            'Invalid input provided, please try again passing a tuple with a valid JSON string.')

    if isinstance(shift_json, str):
        shift_json = json.loads(shift_json)

    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    values_string = ""

    for day in days:
        shifts = shift_json["shift"].get(day, {})
        values_string += f"{shifts.get('morning', 0)}{shifts.get('afternoon', 0)}{shifts.get('night', 0)}"

    return values_string


def get_shift():
    """
    Retrieves the applied shift for a specific owner and week from the database.

    This function queries the Shift model to find a record where the `owner` matches the `user`
    and the `week` matches the `week`. It then returns the `applied_shift` attribute of the
    retrieved Shift object.

    Assumptions:
        - The `user` and `week` variables should be defined in the surrounding scope or context.
        - The `Shift` model must have `owner`, `week`, and `applied_shift` fields.

    Returns:
        The `applied_shift` attribute of the Shift object, which is expected to be a value
        representing the shift applied for the specified owner and week.

    Raises:
        Shift.DoesNotExist: If no Shift record matches the specified `owner` and `week`.
        Shift.MultipleObjectsReturned: If multiple Shift records match the specified `owner` and `week`.

    Example:
        user = get_current_user()  # Assume this function provides the current user
        week = get_current_week()  # Assume this function provides the current week
        shift = get_shift()
        print(shift)  # Output will be the applied shift for the specified user and week
    """
    shift = Shift.objects.get(owner=user, week=week)
    return shift.applied_shift


def save_shift(*args):
    """
    Processes a tuple of arguments to find a valid application string and updates the `applied_shift`
    attribute of a `Shift` object in the database.

    The function expects a tuple containing one or more items. It searches for an item that is 21 characters
    long and passes the `is_binary_string` validation. If a valid application string is found, it updates
    the `applied_shift` field of a `Shift` object for the current user and week.

    Parameters:
        *args (tuple): A variable-length argument list. Each item should be checked to find a valid application string.

    Returns:
        None

    Raises:
        ValueError: If no valid application string is found or if the input is not a tuple.

    Example:
        # Assuming `user` and `week` are defined globally and `is_binary_string` is a valid function
        save_shift("some_string_with_length_21", "another_string")
    """
    print("--save_shift", args)

    application_string = ""
    found = False

    if type(args) == tuple:
        for item in args:
            if len(item) == 21 and is_binary_string(item):
                application_string = item
                found = True

    if not found or not type(args) == tuple:
        raise ValueError(
            'Invalid input provided, please try again passing a tuple to the function with the application string in it')

    shift = Shift.objects.get(owner=user, week=week)
    shift.applied_shift = application_string
    shift.save()


def get_week_number_for_application():
    """
    Calculates and returns the ISO week number for the week that starts two weeks from the current week.

    This function determines the start date of the current week, calculates the start date of the week
    that begins two weeks from now, and returns the ISO week number for that future week.

    The `datetime` module is imported within the function to perform date calculations.

    Returns:
        int: The ISO week number for the week starting two weeks from the current week.

    Example:
        week_number = get_week_number_for_application()
        print(week_number)  # Output will be the ISO week number two weeks from the current date
    """
    import datetime

    today = datetime.date.today()
    start_of_current_week = today - datetime.timedelta(days=today.weekday())
    start_of_next_week = start_of_current_week + datetime.timedelta(weeks=2)
    _, next_next_week, _ = start_of_next_week.isocalendar()
    return next_next_week


def get_current_date_time():
    """
    Retrieves and returns the current local date and time.

    This function uses the `datetime` module to get the current date and time and returns it
    as a `datetime` object.

    The `datetime` module is imported within the function to perform the date and time calculations.

    Returns:
        datetime.datetime: The current local date and time as a `datetime` object.

    Example:
        current_datetime = get_current_date_time()
        print(current_datetime)  # Output will be the current date and time, e.g., 2024-09-08 15:26:48.123456
    """
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
    ),
    StructuredTool.from_function(
        func=convert_json_to_string,
        name="Json converter",
        description=JSON_CONVERTER_DESCRIPTION,
    ),
    StructuredTool.from_function(
        func=save_shift,
        name="Application saver",
        description=APPLICATION_SAVER_DESCRIPTION,
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
    """
    Processes a user request, interacts with an agent to generate a response, and updates the conversation history.

    This function:
    1. Loads environment variables.
    2. Extracts the user's message and metadata from the request.
    3. Initializes conversation memory and agent executor.
    4. Adds the user's message and past messages to the memory.
    5. Invokes the agent with the user's input and current chat history.
    6. Saves and prints the agent's response, and updates the conversation history.

    Parameters:
        request (Request): The HTTP request containing user message data and metadata.

    Returns:
        None
    """
    import datetime

    load_dotenv()

    global user
    global week

    # Extract user message and metadata
    message = request.data.get('text')
    user = request.user
    week = get_week_number_for_application()

    # Save the user's message
    msg = Message(text=message, sent_by_user=True,
                  date=request.data.get('date'), owner=user)
    msg.save()

    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)

    # Setup agent executor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True
    )

    # Add initial message to memory
    initial_message = INIT_MSG_FOR_AGENT
    memory.chat_memory.add_message(SystemMessage(content=initial_message))

    # Retrieve and add past messages
    past_messages = get_past_messages(user)
    for past_message in past_messages:
        message_type = HumanMessage if past_message.sent_by_user else SystemMessage
        memory.chat_memory.add_message(message_type(content=past_message.text))

    # Add the user's current message to memory
    memory.chat_memory.add_message(HumanMessage(content=message))

    # Invoke the agent and process the response
    input_data = {"question": message}
    response = agent_executor.invoke(input_data)
    print("Bot:", response["output"])
    print(response)

    # Add agent's response to memory
    memory.chat_memory.add_message(AIMessage(content=response["output"]))

    # Save the agent's response
    msg = Message(text=response["output"], sent_by_user=False,
                  date=datetime.datetime.now(), owner=request.user)
    msg.save()
