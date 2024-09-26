NUMBER_OF_SHIFTS = 21

NUMBER_OF_DAYS = 7

MESSAGE_MAX_LENGTH = 1024

INIT_MSG_FOR_AGENT = """You are an AI assistant that can provide helpful answers using available tools. You will have to explain the user's upcoming week's applied schedule and modify it if needed.
                        \nIf you are unable to answer, you can use the following tools: 'Application summarization', 'Modification', Application saving', 'Get current date/time', 'Drop ongoing modification', 'Get week number for application week',
                        You don't have to use them, if it's not mandatory"""

GET_CURRENT_DATETIME_DESCRIPTION = """Userful when you need to know the current date/time.
                                      \nNo input is required as it uses global variables."""

GET_WEEKNUMBER_DESCRIPTION = """Userful when you need to know for which week's application you will work with.
                                \nIt's always two weeks ahead of the current week, and for that week will the user apply for certain shifts.
                                \nNo input is required as it uses global variables."""
                                
SUMMARIZATION_DESC = """Useful for summarize an application for the user.
                        This function returns a summarization which can be handed over to the user. Return the output of the tool exactly as it is, without any modification.
                        No input is required."""

GET_APPLICATION_CHANGE_DESCRIPTION = """Useful when the user wants to apply or cancel shifts or modify their application.
                                        This will save the modifications, and later the user can save it.
                                        The changes can be ongoing through multiple requests, the user will ask to save when the change is finalized.
                                        Never drop the modifications until the user asks for it!
                                        This function returns a summarization which can be handed over directly to the user. Return the output of the tool exactly as it is, without any modification.
                                        The input is a single string, the user's request."""

GET_SAVE_APPLICATION_MODIFICATION_DESCRIPTION = """Useful for saving a modified application.
                                                    It will only save the modification if there was any, nothing will happen otherwise.
                                                    No input is required."""
                                                    
GET_DROP_MODIFICATION_DESCRIPTION = """Useful for dropping your ongoing modifications if you want to start over, or just don't want to modify.
                                       No input is required."""
                                       
GET_CURRENT_MODIFICATION_DESCRIPTION = """Usefor for summarizing the current state of the modifications.
                                          This function returns a summarization which can be handed over to the user. Return the output of the tool exactly as it is, without any modification.
                                          No input is required."""
