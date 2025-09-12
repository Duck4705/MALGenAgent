from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from State.State import MalGenAgentState, Coder_State
from Prompt.Prompt import Prompt_Coder

# Create LLM with structured output
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
structured_llm = llm.with_structured_output(Coder_State)

def CoderAgent(state: dict):
    # Check if Checker_State exists and has non-empty message (meaning feedback from checker)
    checker_message = state.get("Checker_State", {}).get("message", "")
    
    # If no checker feedback, proceed with normal coding
    if not checker_message:  
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
        feedback = checker_message
        code = state.get("Coder_State", {}).get("Code", "")
        messages_user = HumanMessage(content=f"Checker Feedback: {feedback}\nCurrent Code:\n{code}\nPlease revise the code accordingly.")
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
        return {}