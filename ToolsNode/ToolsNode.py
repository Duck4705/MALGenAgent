from langchain_core.messages import ToolMessage
from Tools.Tools import execute_command

def ToolsNode(state: dict):
    """
    Execute tools requested by LLM tool calls
    """
    messages = state.get("messages", [])
    
    # Get the last message (should contain tool calls)
    if not messages:
        return {"messages": []}
    
    last_message = messages[-1]
    
    # Check if there are tool calls to execute
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        print("[ToolsNode] No tool calls found")
        return {"messages": []}
    
    tool_responses = []
    
    for tool_call in last_message.tool_calls:
        print(f"[ToolsNode] Executing tool: {tool_call['name']}")
        
        if tool_call['name'] == 'execute_command':
            # Extract command from tool call args
            command = tool_call['args'].get('command', '')
            
            # Execute the command
            result = execute_command(command)
            
            # Create tool response message
            tool_msg = ToolMessage(
                content=str(result),
                tool_call_id=tool_call['id']
            )
            tool_responses.append(tool_msg)
            
            print(f"[ToolsNode] Tool executed: {result['status']}")
        else:
            # Unknown tool
            tool_msg = ToolMessage(
                content=f"Unknown tool: {tool_call['name']}",
                tool_call_id=tool_call['id']
            )
            tool_responses.append(tool_msg)
    
    return {"messages": tool_responses}
