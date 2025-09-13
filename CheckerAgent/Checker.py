from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Checker_State
from Prompt.Prompt import Prompt_Checker
from Tools.Tools import execute_command 

# Create LLM with tools (for tool calling)
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
llm_with_tools = llm.bind_tools([execute_command])

def CheckerAgent(state: dict):
    # Get input from Execute_Builder result - ensure it's properly formatted JSON
    executable_result = state.get("Executable_Builder", {})
    
    # If it's already a dict, convert to proper JSON format
    if isinstance(executable_result, dict):
        input_data = str(executable_result)
    else:
        input_data = str(executable_result)
    
    print(f"[CheckerAgent] Processing executable builder result: {input_data}")
    
    messages_user = HumanMessage(content=input_data)
    messages_system = SystemMessage(content=Prompt_Checker)
    
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
            # Parse JSON response from LLM if possible
            content = response.content.strip()
            print(f"[CheckerAgent] LLM Response: {content}")
            
            # Try to parse as JSON first
            import json
            try:
                parsed_response = json.loads(content)
                if isinstance(parsed_response, dict) and "message" in parsed_response:
                    checker_message = parsed_response["message"]
                    print(f"[CheckerAgent] Parsed JSON message: {checker_message}")
                else:
                    raise ValueError("Invalid JSON structure")
            except (json.JSONDecodeError, ValueError):
                # Fallback to simple text parsing
                content_lower = content.lower()
                if "finished build" in content_lower:
                    checker_message = "finished build"
                elif "success download lib and need to rebuild" in content_lower:
                    checker_message = "success download lib and need to rebuild"
                elif "unhandled error" in content_lower:
                    checker_message = "error"
                else:
                    # For syntax errors or detailed feedback, keep the full content
                    checker_message = content
                
                print(f"[CheckerAgent] Fallback parsed message: {checker_message}")
                
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