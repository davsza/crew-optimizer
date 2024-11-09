NUMBER_OF_SHIFTS = 21
DAYS_IN_WEEK = 7
MESSAGE_MAX_LENGTH = 1024
MAX_VACATION_CLAM_PER_YEAR = 20
CHAR_ZERO = '0'
CHAR_ONE = '1'
CHAR_X = 'x'
USER_INIT_MSG = """You are an AI assistant that can provide helpful answers using available tools. You will have to explain the user's upcoming week's application and modify it if needed.
                        \nIf you are unable to answer, you can use the following tools: 'Application summarization', 'Modification', Application saving', 'Get current date/time', 'Drop ongoing modification', 'Get week number for application week', 'Application for vacation'
                        You don't have to use them, if it's not mandatory"""
ADMIN_INIT_MSG = """You are an AI assistant that can provide helpful answers using available tools. You will help a crew control member optimize the users' application to have a perfectly arranged schedule.
                    \nIf you are unable to answer, you can use the following tools: 'Schedule optimizer', 'Reject vacation'.
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
GET_WEEKEND_VIOLATION = """You can't make any new applications after Friday!"""
GET_SCHEDULE_OPTIMIZER_DESCRIPTION = """Useful for optimizing and generating a schedule by the applications of the users.
                                        No input is required."""
GET_APPLICATION_FOR_VACATION_OR_SICKNESS_DESCRIPTION = """Useful when the user wants to apply or cancel vacation or apply for sick leave.
                                                       This function returns a summarization which can be handed over directly to the user. Return the output of the tool exactly as it is, without any modification.
                                                       The input is a single string, the user's request."""
GET_REJECT_VACATION_DESCRIPTION = """Useful for rejecting vacation claim for users. The input is the admin's requests, whose claim will be deleted, the begin and the end date of the vacation."""
NO_ONGOINT_MODIFICATIONS = """You don't have any ongoing modifications, nothing to save!"""
SUCCESSFUL_SAVE_MSG = """You successfully saved your application. If you have any questions or want to modify it feel free to ask!"""
SUCCESSFUL_DROP_MSG = """You successfully dropped your ongoing modifications. If you have any questions or want to modify it feel free to ask!"""
SOLVER_STATUS_OPTIMAL = """Successful schedule optimization!"""
SOLVER_STATUS_FEASIBLE = """Feasible solution found but not optimal."""
SOLVER_STATUS_INFEASIBLE = """The problem is infeasible. Please remove vacations if necessary"""
SOLVER_STATUS_UNBOUNDED = """The problem is unbounded!"""
SOLVER_STATUS_NOT_SOLVED = """The problem was not solved!"""
