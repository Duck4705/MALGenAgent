from langgraph.graph import START, END, StateGraph, MessagesState
from PlannerAgent.PlannerAgent import PlannerAgent
from DeveloperAgent.DeveloperAgent import DeveloperAgent
from State.State import MalGenAgentState
from CoderAgent.Coder import CoderAgent
from CheckerAgent.Checker import CheckerAgent
from ToolsNode.ToolsNode import ToolsNode
from RoutingLogic.Router import should_continue
from Tools.Tools import execute_command, ExecutableBuilder

#Execute Builder Node
def Execute_Builder(state: dict):
    type_file = state.get("Planner_State", {}).get("Type_File", "")
    language = state.get("Planner_State", {}).get("Language", "").lower()
    code = state.get("Coder_State", {}).get("Code", "")
    
    print(f"[Execute_Builder] Building: type={type_file}, lang={language}")
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
builder.add_node("ToolsNode", ToolsNode)

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
        "tools": "ToolsNode",
        "coder": "CoderAgent",
        "end": END
    }
)

# Edge from ToolsNode back to CheckerAgent
builder.add_edge("ToolsNode", "CheckerAgent")

# Compile graph
graph = builder.compile()