def should_continue(state: dict):
    """
    Determine next node based on checker state
    """
    messages = state.get("messages", [])
    checker_state = state.get("Checker_State", {})
    
    # If there are tool calls pending, go to tools
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print("[Router] Routing to ToolsNode")
            return "tools"
    
    # Check checker state message
    checker_message = checker_state.get("message", "").lower()
    
    if checker_message == "finished build":
        print("[Router] Build finished - routing to END")
        return "end"
    elif checker_message == "success download lib and need to rebuild":
        print("[Router] Need to rebuild - routing to CoderAgent")
        return "coder"
    elif checker_message in ["error", "processing"]:
        print("[Router] Error or processing - routing to CoderAgent")
        return "coder"
    else:
        print("[Router] Default routing to CoderAgent")
        return "coder"
