import json
from typing import Dict

from .constants import CHAR_ONE, CHAR_ZERO, CHAR_X


def is_uniform_with_char(s: str, character: str) -> bool:
    """
    Check if all characters in a string are the same as a specified character.

    Args:
        s (str): The string to check.
        character (str): The character to compare against.

    Returns:
        bool: True if all characters in the string are the same as 'character', otherwise False.
    """
    return all(char == character for char in s)


def get_default_schedule_str(char: str) -> str:
    """
    Generate a default schedule by repeating a character 21 times.

    Args:
        char (str): The character to repeat.

    Returns:
        str: A string consisting of the character repeated 21 times.
    """
    return char * 21


def get_default_days_str(char: str) -> str:
    """
    Generate a default set of days by repeating a character 7 times.

    Args:
        char (str): The character to repeat.

    Returns:
        str: A string consisting of the character repeated 7 times.
    """
    return char * 7


def convert_roster_string_to_json(roster_str: str) -> str:
    """
    Convert a roster string to a JSON representation.

    The roster string consists of 21 characters, representing the morning, afternoon, 
    and night shifts for each of the 7 days (in the order of Monday to Sunday). A '1' 
    means the shift is scheduled, 'x' means no shift, and other characters are treated as False.

    Args:
        roster_str (str): A string of length 21 representing the shifts for each day of the week.

    Returns:
        str: A JSON string representing the roster with morning, afternoon, and night shifts for
             each day.
    """
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    ret_json = {}

    for i, day in enumerate(days):
        start_index = i * 3
        ret_json[day] = {
            "morning": (
                True if roster_str[start_index] == CHAR_ONE
                else (None if roster_str[start_index] == CHAR_X else False)
            ),
            "afternoon": (
                True if roster_str[start_index + 1] == CHAR_ONE
                else (None if roster_str[start_index + 1] == CHAR_X else False)
            ),
            "night": (
                True if roster_str[start_index + 2] == CHAR_ONE
                else (None if roster_str[start_index + 2] == CHAR_X else False)
            )
        }

    return json.dumps({"roster": ret_json}, indent=4)


def convert_json_to_roster_string(roster_json: Dict, parse_none_as_x: bool = False) -> str:
    """
    Convert a roster JSON to a string representation.

    The function processes a JSON object representing a weekly roster, extracting the shifts 
    for each day and converting them into a 21-character string where each 3 characters 
    represent the morning, afternoon, and night shifts for each day. 
    '1' represents a scheduled shift, '0' represents no shift, and 'x' is used if None is
    encountered (optional).

    Args:
        roster_json (dict): A JSON object containing the roster with shifts for each day.
        parse_none_as_x (bool, optional): If True, None values are represented as 'x' instead
        of '0'. Defaults to False.

    Returns:
        str: A 21-character string representing the shifts for the entire week.
    """
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    values_string = ""

    for day in days:
        roster = roster_json["roster"].get(day, {})
        for shift in ['morning', 'afternoon', 'night']:
            value = roster.get(shift, None)

            if parse_none_as_x and value is None:
                values_string += CHAR_X
            else:
                values_string += str(int(bool(value)))

    return values_string


def order_json_by_days(roster_json: Dict[str, dict]) -> Dict[str, dict]:
    """
    Order the days in the given roster JSON by the standard week order.

    This function takes a roster JSON where the keys are days of the week and
    returns a new dictionary where the days are ordered from Monday to Sunday.
    Any day not present in the input JSON will be skipped.

    Args:
        roster_json (dict): A dictionary where the keys are days of the week and the values ar
                            shift data.

    Returns:
        dict: A new dictionary with the days ordered from Monday to Sunday.
    """
    days_of_week = ["monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday"]

    ordered_json = {day: roster_json[day] for day in days_of_week if day in roster_json}

    return ordered_json


def complement_roster(roster_json: str) -> Dict:
    """
    Complements the input roster JSON to ensure that all days of the week have entries
    for all shifts (morning, afternoon, night). Missing shifts are filled with None.

    This function takes a roster JSON string, parses it, and ensures that each day of the 
    week has an entry for morning, afternoon, and night shifts. If a day or shift is missing, 
    it will be added with a value of None.

    Args:
        roster_json (str): A JSON string representing the roster with days and shift data.

    Returns:
        dict: The updated roster JSON with all shifts for all days, including missing shifts.
    """
    days_of_week = ["monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday"]
    default_shifts = {"morning": None, "afternoon": None, "night": None}

    input_json = json.loads(roster_json)

    current_shifts = input_json.get("roster", {})

    for day in days_of_week:
        if day in current_shifts:
            for shift in default_shifts:
                if shift not in current_shifts[day]:
                    current_shifts[day][shift] = default_shifts[shift]
        else:
            current_shifts[day] = default_shifts.copy()

    input_json["roster"] = current_shifts
    return input_json


def overwrite_str_with_value(original_binary: str, replace_with: str) -> str:
    """
    Overwrite characters in the original binary string with characters from the replacement string.

    This function iterates over the original binary string, and if the character is either
    '0' or '1', it remains unchanged. Otherwise, the character from the `replace_with` string is
    used as a replacement.

    Args:
        original_binary (str): The original binary string containing '0' or '1'.
        replace_with (str): The string to use for replacement when a non-'0' or '1' character is
                            encountered.

    Returns:
        str: A new string with the replaced characters from the `replace_with` string.
    """
    application_summary_result = ""

    for i in range(len(original_binary)):
        if original_binary[i] == CHAR_ZERO or original_binary[i] == CHAR_ONE:
            application_summary_result += original_binary[i]
        else:
            application_summary_result += replace_with[i]

    return application_summary_result


def replace_string_from_to_with_char(
    binary_to_replace: str,
    from_pos: int,
    to_pos: int,
    character: str
) -> str:
    """
    Replace a portion of a binary string with a specified character.

    This function takes a binary string and replaces a segment starting from `from_pos`
    to `to_pos` with a specified character repeated over the length of the segment.

    Args:
        binary_to_replace (str): The original binary string that will be modified.
        from_pos (int): The starting position of the segment to replace.
        to_pos (int): The ending position of the segment to replace.
        character (str): The character to replace the specified segment with.

    Returns:
        str: The modified binary string with the specified segment replaced by the character.
    """
    replaced_binary = (
        binary_to_replace[:from_pos] +
        character * (to_pos - from_pos) +
        binary_to_replace[to_pos:]
    )

    return replaced_binary


def get_roster_mapping(rosters: list, start: int, end: int, offset: int = 0) -> dict:
    """
    Generate a dictionary mapping roster indices to their respective rosters.

    This function takes a list of rosters and returns a dictionary where the keys are 
    adjusted indices based on the `offset`, and the values are the corresponding rosters 
    from the `rosters` list.

    Args:
        rosters (list): A list of rosters.
        start (int): The starting index (inclusive) in the list of rosters.
        end (int): The ending index (exclusive) in the list of rosters.
        offset (int, optional): The number to subtract from the indices. Defaults to 0.

    Returns:
        dict: A dictionary where keys are adjusted indices, and values are the respective rosters.
    """
    return {i - offset: rosters[i - start] for i in range(start, end)}


def get_day_mapping(days: list, start: int, end: int) -> dict:
    """
    Generate a dictionary mapping day indices to their respective days.

    This function takes a list of days and returns a dictionary where the keys are 
    the indices in the range from `start` to `end` (exclusive), and the values are 
    the corresponding days from the `days` list.

    Args:
        days (list): A list of days.
        start (int): The starting index (inclusive) in the list of days.
        end (int): The ending index (exclusive) in the list of days.

    Returns:
        dict: A dictionary where keys are the indices in the range from `start` to `end`, 
              and values are the respective days.
    """
    return {i: days[i - start] for i in range(start, end)}


def max_consecutive_days_in_roster(
    roster_str: str,
    character_to_find: str
) -> int:
    """
    Calculates the maximum number of consecutive days in the roster with a specific character.

    This function iterates through the roster and counts the longest sequence of consecutive 
    occurrences of the specified character. It returns the maximum length of such a sequence.

    Args:
        roster (str): A string representing the roster, where each character represents a day or
                      shift.
        character_to_find (str): The character to search for in the roster(e.g., '1' for a shift
                                 or 'x' for absence).

    Returns:
        int: The maximum number of consecutive days with the specified character.
    """
    max_count = 0
    current_count = 0

    for char in roster_str:
        if char == character_to_find:
            current_count += 1
        else:
            max_count = max(max_count, current_count)
            current_count = 0

    max_count = max(max_count, current_count)

    return max_count


def contains_character_from_index(s: str, index: int, char: str) -> bool:
    """
    Checks if the string contains the specified character between the given index and the end of
    the string.

    Parameters:
        s (str): The input string.
        index (int): The starting index to check from.
        char (str): The character to search for.

    Returns:
        bool: True if the character is found between the index and the end of the string, False
              otherwise.
    """
    return char in s[index:]


def merge_roster_strings(s1: str, s2: str, s3: str) -> str:
    """
    Merges three binary strings such that the result has '1' at any index
    where either of the input strings has a '1'.

    Parameters:
        s1 (str): First binary string.
        s2 (str): Second binary string.
        s3 (str): Third binary string.

    Returns:
        str: Merged binary string.
    """
    merged = ''.join('1'
                     if char1 == '1' or char2 == '1' or char3 == '1'
                     else '0'
                     for char1, char2, char3 in zip(s1, s2, s3)
                    )
    return merged
