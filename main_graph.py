from langgraph.graph import START, END, StateGraph
from src.Agent.PlannerAgent.PlannerAgent import PlannerAgent
from src.Agent.DeveloperAgent.DeveloperAgent import DeveloperAgent
from src.Agent.CoderAgent.Coder import CoderAgent
from src.Agent.CheckerAgent.Checker import CheckerAgent
from src.Execute_Builder.ExecuteBuilder import Execute_Builder
from src.State.State import MalGenAgentState, Input_State
from src.RoutingLogic.Router import should_continue


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