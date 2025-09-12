from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Developer_State
from Prompt.Prompt import Prompt_Developer

# Create LLM with structured output
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
structured_llm = llm.with_structured_output(Developer_State)

def DeveloperAgent(state: dict):
    # Get user messages from state (safe access)
    list_task = state.get("Planner_State", {}).get("Subtask", [])
    language = state.get("Planner_State", {}).get("Language", "Python")
    operating_system = state.get("Planner_State", {}).get("Operating_System", "Linux")
    list_response = []
    list_response_json = []

    for task in list_task:
        messages_user = HumanMessage(content=str(task + " in " + language + " for " + operating_system))
        messages_system = SystemMessage(content=Prompt_Developer)

        # Get structured response directly from LLM
        developer_state = structured_llm.invoke([messages_system, messages_user])
        # store as dict for internal state and JSON string for message reducer
        list_response.append(developer_state.model_dump())
        list_response_json.append(developer_state.model_dump_json())

    # Normalize existing Mess_Developer to a list of strings and append new JSON messages
    current_msgs = state.get("Mess_Developer", [])
    if current_msgs is None:
        current_msgs = []
    if not isinstance(current_msgs, list):
        current_msgs = [str(current_msgs)]
    new_messages = current_msgs + list_response_json

    return {"Developer_State": {"Task_State": list_response}, "Mess_Developer": new_messages}
