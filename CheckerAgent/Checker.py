from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Checker_State
from Prompt.Prompt import Prompt_Checker
from Tools.Tools import execute_command 
from Tools.ToolHelper import create_llm_with_tools, is_tool_call_message, extract_tool_calls
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import re
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

# Create LLM with proper tool binding using helper
llm_with_tools = create_llm_with_tools(base_llm)

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
        from State.State import Checker_State
        return {"Checker_State": Checker_State(message="finished build")}
    
    # Error - need to fix code
    if not current_code:
        print("[CheckerAgent] No code to fix")
        from State.State import Checker_State
        return {"Checker_State": Checker_State(message="error")}
    
    print(f"[CheckerAgent] Error detected, using LLM to fix...")
    
    # Use LLM to analyze error and fix code
    prompt = f"""You are a code fixer. Fix the following code based on the error:

ERROR: {error_message}

CURRENT CODE:
{current_code}

Return ONLY the fixed code, nothing else. Fix common issues like:
- Missing semicolons
- Missing includes
- Syntax errors
- Variable declarations

FIXED CODE:"""
    
    # Get LLM response using existing base_llm
    try:
        response = base_llm.invoke([HumanMessage(content=prompt)])
        raw_code = response.content.strip()
        
        # Clean up markdown formatting if present
        fixed_code = raw_code
        if "```" in fixed_code:
            # Remove markdown code blocks
            lines = fixed_code.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                if line.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or not any(line.startswith(p) for p in ['```', '## ', '# ', '**']):
                    code_lines.append(line)
            
            fixed_code = '\n'.join(code_lines).strip()
        
        print(f"[CheckerAgent] Code fixed by LLM (cleaned)")
        print(f"[CheckerAgent] Original code length: {len(current_code)} chars")
        print(f"[CheckerAgent] Fixed code length: {len(fixed_code)} chars")
        print(f"[CheckerAgent] Fixed code preview: {fixed_code[:100]}...")
        
        # Update Coder_State with fixed code - use proper BaseModel
        from State.State import Coder_State, Checker_State
        
        return {
            "Coder_State": Coder_State(Code=fixed_code),
            "Checker_State": Checker_State(message="code fixed")
        }
        
    except Exception as e:
        print(f"[CheckerAgent] LLM error: {e}")
        from State.State import Checker_State
        return {"Checker_State": Checker_State(message="error")}