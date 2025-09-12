from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Checker_State
from Prompt.Prompt import Prompt_Checker
from Tools.Tools import execute_command 

# Create LLM with tools (for tool calling)
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
llm_with_tools = llm.bind_tools([execute_command])

def CheckerAgent(state: dict):
    # Get input from Execute_Builder result
    input_data = str(state.get("Executable_Builder", {}))
    messages_user = HumanMessage(content=input_data)
    messages_system = SystemMessage(content=Prompt_Checker)
    
    print(f"[CheckerAgent] Processing executable builder result...")
    
    # Get response from LLM with tools
    response = llm_with_tools.invoke([messages_system, messages_user])
    
    # Check if LLM wants to use tools
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"[CheckerAgent] LLM requested {len(response.tool_calls)} tool calls")
        return {
            "messages": [response],
            "Checker_State": {"message": "tool_calls_requested"}
        }
    else:
        # No tool calls, try to extract checker state from content
        try:
            # Simple parsing of response content to determine state
            content = response.content.lower()
            
            if "finished build" in content:
                checker_message = "finished build"
            elif "success download lib and need to rebuild" in content:
                checker_message = "success download lib and need to rebuild"
            elif "error" in content or "fail" in content:
                checker_message = "error"
            else:
                checker_message = "processing"
                
            print(f"[CheckerAgent] Extracted message: {checker_message}")
                
            # Create Checker_State
            checker_dict = {"message": checker_message}
            checker_json = str(checker_dict)
            
            # normalize existing Mess_Checker to a list of strings
            current_msgs = state.get("Mess_Checker", [])
            if current_msgs is None:
                current_msgs = []
            if not isinstance(current_msgs, list):
                current_msgs = [str(current_msgs)]
            new_messages = current_msgs + [checker_json]

            return {
                "Checker_State": checker_dict, 
                "Mess_Checker": new_messages,
                "messages": [response]
            }
            
        except Exception as e:
            print(f"[CheckerAgent] Error parsing response: {e}")
            return {
                "Checker_State": {"message": "error"}, 
                "Mess_Checker": state.get("Mess_Checker", []) + ["error"],
                "messages": [response]
            }