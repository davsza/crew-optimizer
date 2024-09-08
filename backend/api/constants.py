NUMBER_OF_SHIFTS = 21

NUMBER_OF_DAYS = 7

MESSAGE_MAX_LENGTH = 1024

INIT_MSG_FOR_AGENT = """You are an AI assistant that can provide helpful answers using available tools. You will have to explain the user's upcoming week's applied schedule and modify it if needed.
                        \nIf you are unable to answer, you can use the following tools:
                            'Application getter',
                            'Application converter',
                            'Json converter',
                            'Application saver',
                            'Get current date/time',
                            'Get week number for application week',
                        You don't have to use them, if it's not mandatory"""

APPLICATION_GETTER_DESCRIPTION = """Useful when you need to retrieve an application from the database for the user. It's going to be a 21-character long string containing 0 and 1 values.
                                    \nPass the return value of the function to the 'Application converter' tool to convert the schedule string into a JSON for better understanding.
                                    \nNo input is required as it uses global variables."""

APPLICATION_CONVERTER_DESCRIPTION = """Useful when you need to convert an application string into a json for better understanding. Call this function with the return value of the 'Application getter' tool.
                                       \nPlease list the days after each other followed by the applications. Example: 'Monday morning and night, Wednesday afternoon, Friday all 3 shifts, etc.'"""

JSON_CONVERTER_DESCRIPTION = """Useful when you need to convert an application json file into a string for saving into the database.
                                \nWhen the user requests to modify their application JSON, and they are finished with it, pass the modified JSON to this function which will convert it back to the string format for saving it into the database."""

APPLICATION_SAVER_DESCRIPTION = """Userful when you need to save a modified application.
                                   \nYou should only save a modified application once the user asked for it and finalized modifying the applicaiton."""

GET_CURRENT_DATETIME_DESCRIPTION = """Userful when you need to know the current date/time.
                                      \nNo input is required as it uses global variables."""

GET_WEEKNUMBER_DESCRIPTION = """Userful when you need to know for which week's application you will work with.
                                \nIt's always two weeks ahead of the current week, and for that week will the user apply for certain shifts.
                                \nNo input is required as it uses global variables."""
