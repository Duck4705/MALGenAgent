from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Planner_State
from Prompt.Prompt import Prompt_Planner
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

structured_llm = base_llm.with_structured_output(Planner_State)

def PlannerAgent(state: dict):
    # Get user messages from state
    user_content = str(state.get("input", ""))
    
    # Check if there's feedback from previous failures (installation errors, etc.)
    mess_checker = state.get("Mess_Checker", [])
    mess_coder = state.get("Mess_Coder", [])
    
    # Collect all feedback for context
    feedback_context = ""
    if mess_checker:
        latest_checker_feedback = mess_checker[-1] if mess_checker else ""
        if "Installation failed" in str(latest_checker_feedback) or "Command timed out" in str(latest_checker_feedback):
            feedback_context += f"\n\nPREVIOUS ISSUE: {latest_checker_feedback}"
            feedback_context += "\nNOTE: Previous dependency installation failed. Consider alternative approaches or simpler implementations that don't require external dependencies."
    
    # Add feedback context to user content if exists
    if feedback_context:
        user_content += feedback_context
        print(f"[PlannerAgent] Added failure feedback context: {feedback_context}")
    
    messages_user = HumanMessage(content=user_content)
    messages_system = SystemMessage(content=Prompt_Planner)
    
    # Get structured response directly from LLM
    planner_state = structured_llm.invoke([messages_system, messages_user])
    
    print(f"[PlannerAgent] Generated plan with feedback context included")
    
    # Return BaseModel directly, not dict
    planner_json = planner_state.model_dump_json()

    # normalize existing Mess_Planner to a list of strings
    current_msgs = state.get("Mess_Planner", [])
    if current_msgs is None:
        current_msgs = []
    if not isinstance(current_msgs, list):
        current_msgs = [str(current_msgs)]
    new_messages = current_msgs + [planner_json]

    return {"Planner_State": planner_state, "Mess_Planner": new_messages}
