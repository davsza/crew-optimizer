import json

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

    return json.dumps({"shift": schedule}, indent=4)

print(convert_string_to_json("101010101010101010101"))