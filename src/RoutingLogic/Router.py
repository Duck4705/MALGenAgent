def should_continue(state: dict):
    """
    Determine next node based on checker state
    """
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

