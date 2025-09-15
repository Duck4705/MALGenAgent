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
    
    # Check checker state message - access BaseModel properly
    checker_state = state.get("Checker_State")
    checker_message = checker_state.message if checker_state else ""
    
    print(f"[Router] Checker message: '{checker_message}'")
    
    if checker_message == "finished build":
        print("[Router] Build successful - END")
        return "end"
    elif checker_message == "code fixed":
        print("[Router] Code fixed - rebuild")
        return "execute_builder" 
    else:
        print("[Router] Error - END")
        return "end"
