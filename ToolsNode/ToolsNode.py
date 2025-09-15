from langchain_core.messages import ToolMessage, AIMessage
from Tools.Tools import execute_command
import json

def ToolsNode(state: dict):
    """
    Execute tools requested by LLM tool calls and return structured responses
    """
    messages = state.get("messages", [])
    
    print(f"[ToolsNode] Processing {len(messages)} messages")
    
    # Get the last message (should contain tool calls from CheckerAgent)
    if not messages:
        print("[ToolsNode] No messages found in state")
        return {"messages": []}
    
    last_message = messages[-1]
    print(f"[ToolsNode] Last message type: {type(last_message)}")
    
    # Check if there are tool calls to execute
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        print("[ToolsNode] No tool calls found in last message")
        return {"messages": []}
    
    print(f"[ToolsNode] Found {len(last_message.tool_calls)} tool calls")
    
    tool_responses = []
    tool_results = []  # Store results for CheckerAgent analysis
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get('name', 'unknown')
        tool_id = tool_call.get('id', 'unknown_id')
        tool_args = tool_call.get('args', {})
        
        print(f"[ToolsNode] Executing tool: {tool_name} with ID: {tool_id}")
        print(f"[ToolsNode] Tool arguments: {tool_args}")
        
        if tool_name == 'execute_command':
            # Extract command from tool call args
            command = tool_args.get('command', '')
            
            if not command:
                print("[ToolsNode] ERROR: No command provided in tool call")
                error_result = {"status": "error", "message": "No command provided"}
                tool_msg = ToolMessage(
                    content=json.dumps(error_result),
                    tool_call_id=tool_id
                )
                tool_responses.append(tool_msg)
                tool_results.append(error_result)
                continue
            
            print(f"[ToolsNode] Executing command: {command}")
            
            # Execute the command using Tools.py function
            result = execute_command(command)
            tool_results.append(result)
            
            # Create structured tool response for LLM
            tool_msg = ToolMessage(
                content=json.dumps(result),
                tool_call_id=tool_id
            )
            tool_responses.append(tool_msg)
            
            print(f"[ToolsNode] Tool executed - Status: {result.get('status', 'unknown')}")
            print(f"[ToolsNode] Tool result: {result}")
            
        else:
            # Handle unknown tools
            print(f"[ToolsNode] ERROR: Unknown tool requested: {tool_name}")
            error_result = {"status": "error", "message": f"Unknown tool: {tool_name}"}
            tool_msg = ToolMessage(
                content=json.dumps(error_result),
                tool_call_id=tool_id
            )
            tool_responses.append(tool_msg)
            tool_results.append(error_result)
    
    print(f"[ToolsNode] Completed {len(tool_responses)} tool executions")
    
    # Store tool results in state for CheckerAgent to analyze
    return {
        "messages": tool_responses,
        "Tool_Results": tool_results  # Additional field for debugging/analysis
    }
