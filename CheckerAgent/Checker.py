from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Checker_State, Coder_State
from Prompt.Prompt import Prompt_Checker
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

# Create structured LLM like CoderAgent
structured_llm = base_llm.with_structured_output(Coder_State)

def CheckerAgent(state: dict):
    print("[CheckerAgent] Starting analysis...")
    
    # Get build result and current code
    executable_result = state.get("Executable_Builder", {})
    coder_state = state.get("Coder_State")
    current_code = coder_state.Code if coder_state else ""
    
    # Check build status
    build_status = executable_result.get("status", "")
    error_message = executable_result.get("message", "")
    
    print(f"[CheckerAgent] Build status: {build_status}")
    
    # Success - no fix needed
    if build_status == "success":
        print("[CheckerAgent] Build successful - ending")
        checker_result = Checker_State(message="finished build", Code=current_code)
        return {
            "Checker_State": checker_result
        }
    
    # Error - need to fix code
    if not current_code:
        print("[CheckerAgent] No code to fix")
        checker_result = Checker_State(message="error")
        return {"Checker_State": checker_result }
    
    print(f"[CheckerAgent] Error detected, using structured LLM to fix...")
    
    # Prepare messages for structured LLM like CoderAgent
    system_prompt = Prompt_Checker
    user_prompt = f"""Please analyze and fix the compilation error.

ERROR: {error_message}

CURRENT CODE:
{current_code}

Provide both a message describing what was fixed and the corrected code."""
    
    messages_system = SystemMessage(content=system_prompt)
    messages_user = HumanMessage(content=user_prompt)
    
    # Get structured response from LLM like CoderAgent
    fixed_code = structured_llm.invoke([messages_system, messages_user])

    checker_result = Checker_State(message="code fixed")
    return {"Coder_State": fixed_code, "Checker_State": checker_result}
    