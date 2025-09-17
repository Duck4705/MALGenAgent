from langgraph.graph import START, END, StateGraph
from PlannerAgent.PlannerAgent import PlannerAgent
from DeveloperAgent.DeveloperAgent import DeveloperAgent
from State.State import MalGenAgentState
from CoderAgent.Coder import CoderAgent
from CheckerAgent.Checker import CheckerAgent
from RoutingLogic.Router import should_continue
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
    print(f"[Execute_Builder] Code length: {len(code) if code else 0} chars")
    print(f"[Execute_Builder] Code preview: {code[:100] if code else 'NO CODE'}...")
    
    result = ExecutableBuilder(type_file, language, code)
    
    return {"Executable_Builder": result}

# State Graph Builder
builder = StateGraph(MalGenAgentState)

# Build Nodes
builder.add_node("PlannerAgent", PlannerAgent)
builder.add_node("DeveloperAgent", DeveloperAgent)
builder.add_node("CoderAgent", CoderAgent)
builder.add_node("Execute_Builder", Execute_Builder)
builder.add_node("CheckerAgent", CheckerAgent)

# Build Edges
builder.add_edge(START, "PlannerAgent")
builder.add_edge("PlannerAgent", "DeveloperAgent")
builder.add_edge("DeveloperAgent", "CoderAgent")
builder.add_edge("CoderAgent", "Execute_Builder")
builder.add_edge("Execute_Builder", "CheckerAgent")

# Conditional edges from CheckerAgent
builder.add_conditional_edges(
    "CheckerAgent",
    should_continue,
    {
        "execute_builder": "Execute_Builder",
        "end": END
    }
)



# Compile graph
graph = builder.compile()