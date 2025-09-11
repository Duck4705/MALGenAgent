from pydantic import BaseModel
from typing_extensions import TypedDict
from typing import Annotated, Optional
from langgraph.graph import add_messages

# Planner State
class Planner_State(BaseModel):
    Subtask: list[str]
    Language: str
    Operating_System: str
    Type_File: str

# Developer State
class Task_State(BaseModel):
    Task_Description: str
    Code: str
class Developer_State(BaseModel):
    Task_State: list[Task_State]
# Coder State
class Coder_State(BaseModel):
    Code: str

# Checker State
class Checker_State(BaseModel):
    message: str

    
class MalGenAgentState(TypedDict):
    input: str
    Mess_Planner: Annotated[list, add_messages]
    Mess_Coder: Annotated[list, add_messages]
    Mess_Developer: Annotated[list, add_messages]
    Mess_Checker: Annotated[list, add_messages]
    Planner_State: Planner_State
    Developer_State: Developer_State
    Coder_State: Coder_State
    Checker_State: Checker_State
