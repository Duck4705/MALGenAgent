from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Coder_State
from Prompt.Prompt import Prompt_Coder
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

structured_llm = base_llm.with_structured_output(Coder_State)

def CoderAgent(state: dict):
    # CoderAgent only handles initial code generation from Developer tasks
    print("[CoderAgent] Processing developer tasks...")
    
    # Access BaseModel properly
    developer_state = state.get("Developer_State")
    list_task = str(developer_state.Task_State if developer_state else [])
    messages_user = HumanMessage(content=list_task)
    messages_system = SystemMessage(content=Prompt_Coder)
    
    # Get structured response from LLM
    Coder_state = structured_llm.invoke([messages_system, messages_user])
    print(f"[CoderAgent] Generated code successfully")
    
    # Return result - use BaseModel directly, not dict
    Coder_json = Coder_state.model_dump_json()

    # normalize existing Mess_Coder to a list of strings
    current_msgs = state.get("Mess_Coder", [])
    if current_msgs is None:
        current_msgs = []
    if not isinstance(current_msgs, list):
        current_msgs = [str(current_msgs)]
    new_messages = current_msgs + [Coder_json]

    return {"Coder_State": Coder_state, "Mess_Coder": new_messages}