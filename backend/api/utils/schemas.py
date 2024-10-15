from pydantic import BaseModel


class RosterUpdateInputSchema(BaseModel):
    user_input: str


class RosterUpdateOutputSchema(BaseModel):
    agent_output: str


class VacationClaimInputSchema(BaseModel):
    user_input: str


class VacationClaimOutputSchema(BaseModel):
    agent_output: str


class VacationRejectionInputSchema(BaseModel):
    user_input: str


class VacationRejectionOutputSchema(BaseModel):
    agent_output: str


class ScheduleOptimizationOutputSchema(BaseModel):
    agent_output: str


class SummaryOutputSchema(BaseModel):
    agent_output: str


class DropModificationsOutputSchema(BaseModel):
    agent_output: str


class SaveRosterOutputSchema(BaseModel):
    agent_output: str
