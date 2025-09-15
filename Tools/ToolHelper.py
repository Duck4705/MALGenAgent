"""
Helper functions for tool integration with LangChain LLMs
"""

from langchain_core.tools import tool
from typing import Dict, Any
import json

@tool
def execute_command(command: str) -> Dict[str, Any]:
    """
    Execute a shell/terminal command and return the result.
    
    This tool allows you to run system commands for installing packages,
    updating system, and other shell operations.
    
    Args:
        command: The shell command to execute as a string
        
    Returns:
        dict: Contains status (success/error) and message with output
        
    Examples:
        - pip install psutil
        - sudo apt-get update && sudo apt-get install -y g++
        - npm install package-name
    """
    # Import the actual function from Tools.py
    from Tools.Tools import execute_command as _execute_command
    
    result = _execute_command(command)
    
    # Ensure result is JSON serializable
    if isinstance(result, dict):
        return result
    else:
        return {"status": "error", "message": f"Invalid result format: {result}"}

def create_llm_with_tools(base_llm):
    """
    Create an LLM instance with properly bound tools
    
    Args:
        base_llm: The base LLM instance (ChatOllama or ChatOpenAI)
        
    Returns:
        LLM instance with tools bound for function calling
    """
    
    # Bind tools to LLM
    llm_with_tools = base_llm.bind_tools([execute_command])
    
    return llm_with_tools

def format_tool_result(result: Dict[str, Any]) -> str:
    """
    Format tool execution result for LLM consumption
    
    Args:
        result: Tool execution result dictionary
        
    Returns:
        Formatted string for LLM
    """
    
    status = result.get("status", "unknown")
    message = result.get("message", "No message")
    
    return json.dumps({
        "status": status,
        "message": message,
        "formatted_for_llm": True
    })

def is_tool_call_message(message) -> bool:
    """
    Check if a message contains tool calls
    
    Args:
        message: LangChain message object
        
    Returns:
        bool: True if message has tool calls
    """
    
    return (hasattr(message, 'tool_calls') and 
            message.tool_calls and 
            len(message.tool_calls) > 0)

def extract_tool_calls(message) -> list:
    """
    Extract tool calls from a message
    
    Args:
        message: LangChain message with tool calls
        
    Returns:
        list: List of tool call dictionaries
    """
    
    if not is_tool_call_message(message):
        return []
    
    tool_calls = []
    for tool_call in message.tool_calls:
        tool_calls.append({
            "id": tool_call.get("id", "unknown"),
            "name": tool_call.get("name", "unknown"), 
            "args": tool_call.get("args", {})
        })
    
    return tool_calls