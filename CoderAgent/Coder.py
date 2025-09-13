from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Coder_State
from Prompt.Prompt import Prompt_Coder

# Create LLM with structured output
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
structured_llm = llm.with_structured_output(Coder_State)

def CoderAgent(state: dict):
    # Check if Checker_State exists and has feedback that requires code revision
    checker_message = state.get("Checker_State", {}).get("message", "")
    
    print(f"[CoderAgent] Received checker message: '{checker_message}'")
    
    # Only revise code if checker provides syntax error feedback
    # Skip revision for: "finished build", "success download lib and need to rebuild"
    needs_revision = (checker_message and 
                     checker_message not in ["finished build", "success download lib and need to rebuild"] and
                     not checker_message.startswith("Unhandled error"))
    
    # If no revision needed, proceed with normal coding
    if not needs_revision:  
        print("[CoderAgent] Processing developer tasks...")
        list_task = str(state.get("Developer_State", {}).get("Task_State", []))
        messages_user = HumanMessage(content=list_task)
        messages_system = SystemMessage(content=Prompt_Coder)
        
        # Get structured response from LLM
        Coder_state = structured_llm.invoke([messages_system, messages_user])
        print(f"[CoderAgent] Generated code successfully")
        
        # Reducer sẽ tự động append vào messages
        Coder_dict = Coder_state.model_dump()
        Coder_json = Coder_state.model_dump_json()

        # normalize existing Mess_Coder to a list of strings
        current_msgs = state.get("Mess_Coder", [])
        if current_msgs is None:
            current_msgs = []
        if not isinstance(current_msgs, list):
            current_msgs = [str(current_msgs)]
        new_messages = current_msgs + [Coder_json]

        return {"Coder_State": Coder_dict, "Mess_Coder": new_messages}
    
    else:
        # Revision mode - fix code based on checker feedback
        print(f"[CoderAgent] Revision mode: Fixing code based on feedback")
        
        feedback = checker_message
        current_code = state.get("Coder_State", {}).get("Code", "")
        
        # Create detailed prompt for code revision
        revision_prompt = f"""Checker Feedback: {feedback}

Current Code:
{current_code}

Please analyze the feedback and fix ALL the issues mentioned. The feedback may contain multiple errors - address each one carefully."""
        
        messages_user = HumanMessage(content=revision_prompt)
        messages_system = SystemMessage(content=Prompt_Coder)
        
        # Get structured response from LLM for code revision
        Coder_state = structured_llm.invoke([messages_system, messages_user])
        print(f"[CoderAgent] Code revision completed")
        
        # Reducer sẽ tự động append vào messages
        Coder_dict = Coder_state.model_dump()
        Coder_json = Coder_state.model_dump_json()

        # normalize existing Mess_Coder to a list of strings
        current_msgs = state.get("Mess_Coder", [])
        if current_msgs is None:
            current_msgs = []
        if not isinstance(current_msgs, list):
            current_msgs = [str(current_msgs)]
        new_messages = current_msgs + [Coder_json]

        return {"Coder_State": Coder_dict, "Mess_Coder": new_messages}