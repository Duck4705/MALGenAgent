from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Planner_State
from Prompt.Prompt import Prompt_Planner

# Create LLM with structured output
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
structured_llm = llm.with_structured_output(Planner_State)

def PlannerAgent(state: dict):
    # Get user messages from state
    user_content = str(state.get("input", ""))
    messages_user = HumanMessage(content=user_content)
    messages_system = SystemMessage(content=Prompt_Planner)
    
    # Get structured response directly from LLM
    planner_state = structured_llm.invoke([messages_system, messages_user])
    
    
    # Reducer sẽ tự động append vào messages
    planner_dict = planner_state.model_dump()
    planner_json = planner_state.model_dump_json()

    # normalize existing Mess_Planner to a list of strings
    current_msgs = state.get("Mess_Planner", [])
    if current_msgs is None:
        current_msgs = []
    if not isinstance(current_msgs, list):
        current_msgs = [str(current_msgs)]
    new_messages = current_msgs + [planner_json]

    return {"Planner_State": planner_dict, "Mess_Planner": new_messages}
