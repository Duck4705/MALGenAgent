from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Developer_State, Task_State
from Prompt.Prompt import Prompt_Developer
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

OLLAMA = os.getenv("OLLAMA", "false").lower()
MODEL = os.getenv("MODEL", "Qwen2.5-coder:7b")
BASE_URL = os.getenv("BASE_URL", "")
API_KEY = os.getenv("API_KEY", "")
if OLLAMA == "true":
    base_llm = ChatOllama(model=MODEL, temperature=0.1)
else:
    if BASE_URL:
        base_llm = ChatOpenAI(model=MODEL, temperature=0.1, base_url=BASE_URL, api_key=API_KEY)
    else:
        base_llm = ChatOpenAI(model=MODEL, temperature=0.1, api_key=API_KEY)

# Bind with Task_State since we create one task per loop iteration
structured_llm = base_llm.with_structured_output(Task_State)

# Developer Agent
def DeveloperAgent(state: dict):
    # Get user messages from state (safe access)
    # Access BaseModel properly
    planner_state = state.get("Planner_State")
    list_task = planner_state.Subtask if planner_state else []
    language = planner_state.Language if planner_state else "Python"
    operating_system = planner_state.Operating_System if planner_state else "Linux"
    list_response = []
    list_response_json = []

    for task in list_task:
        messages_user = HumanMessage(content=str(task + " in " + language + " for " + operating_system))
        messages_system = SystemMessage(content=Prompt_Developer)

        # Get structured response as Task_State object
        task_state = structured_llm.invoke([messages_system, messages_user])
        # Store Task_State BaseModel object and JSON
        list_response.append(task_state)  # Task_State BaseModel
        list_response_json.append(task_state.model_dump_json())

    # Normalize existing Mess_Developer to a list of strings and append new JSON messages
    current_msgs = state.get("Mess_Developer", [])
    if current_msgs is None:
        current_msgs = []
    if not isinstance(current_msgs, list):
        current_msgs = [str(current_msgs)]
    new_messages = current_msgs + list_response_json

    # Return BaseModel properly
    dev_state = Developer_State(Tasks=list_response)
    return {"Developer_State": dev_state}
