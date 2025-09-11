from langgraph.graph import START, END, StateGraph, MessagesState
from PlannerAgent.PlannerAgent import PlannerAgent
from DeveloperAgent.DeveloperAgent import DeveloperAgent
from State.State import MalGenAgentState

builder = StateGraph(MalGenAgentState)
builder.add_node("PlannerAgent", PlannerAgent)
builder.add_node("DeveloperAgent", DeveloperAgent)

builder.add_edge(START, "PlannerAgent")
builder.add_edge("PlannerAgent", "DeveloperAgent")
builder.add_edge("DeveloperAgent", END)

# Compile graph
graph = builder.compile()