from Tools.Tools import ExecutableBuilder
#Execute Builder Node
def Execute_Builder(state: dict):
    # Access BaseModel attributes properly
    planner_state = state.get("Planner_State")
    coder_state = state.get("Coder_State")
    
    type_file = planner_state.Type_File if planner_state else ""
    language = planner_state.Language.lower() if planner_state else ""
    code = coder_state.Code if coder_state else ""
    
    print(f"[Execute_Builder] Building: type={type_file}, lang={language}")
    
    # Check if code is a list of strings (each line of code)
    if isinstance(code, list):
        print(f"[Execute_Builder] Code contains {len(code)} lines")
        print(f"[Execute_Builder] Code preview: {code[:3] if code else 'NO CODE'}...")
    else:
        print(f"[Execute_Builder] Code is not in expected list format")
        print(f"[Execute_Builder] Code type: {type(code)}")
        print(f"[Execute_Builder] Code preview: {str(code)[:100] if code else 'NO CODE'}...")
    
    result = ExecutableBuilder(type_file, language, code)
    
    return {"Executable_Builder": result}
