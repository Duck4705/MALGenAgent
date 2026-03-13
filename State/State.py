from pydantic import BaseModel
from typing_extensions import TypedDict
from typing import Annotated, Optional
from langgraph.graph import add_messages
from langgraph.graph import MessagesState
# Planner State
class Planner_State(BaseModel):
    Execution_Flow: str
    Subtask: list[str]
    Language: str
    Operating_System: str
    Type_File: str

# Developer State
class Task_State(BaseModel):
    Subtask: str   
    Task_Description: str
    Code: list[str]
    
class Developer_State(BaseModel):
    Tasks: list[Task_State]
# Coder State
class Coder_State(BaseModel):
    Code: list[str]  # Mỗi phần tử là một dòng code

# Checker State
class Checker_State(BaseModel):
    message: str
 
class MalGenAgentState(TypedDict):
    input: str
    Planner_State: Planner_State
    Developer_State: Developer_State
    Coder_State: Coder_State
    Checker_State: Checker_State
    Executable_Builder: dict  # Result from ExecutableBuilder

# Input State
class Input_State(BaseModel):
    input: str    