from langgraph.graph import START, END, StateGraph
from PlannerAgent.PlannerAgent import PlannerAgent
from DeveloperAgent.DeveloperAgent import DeveloperAgent
from State.State import MalGenAgentState, Input_State
from CoderAgent.Coder import CoderAgent
from CheckerAgent.Checker import CheckerAgent
from RoutingLogic.Router import should_continue
from Execute_Builder.ExecuteBuilder import Execute_Builder

# State Graph Builder
builder = StateGraph(MalGenAgentState, input_schema=Input_State)

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