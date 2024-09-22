from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from langchain_core.messages import ToolMessage
from graph.assistant import Assistant, assistant_runnable
from graph.agents import DataCollectorAgent, KGBuilderAgent, ToDataCollectorAgent, ToKGBuilderAgent
from graph.state import State, update_dialog_stack
from utilities import create_entry_node

def create_graph():
    builder = StateGraph(State)

    # Main assistant
    builder.add_node("primary_assistant", Assistant(assistant_runnable))
    
    # Data Collector agent
    data_collector = DataCollectorAgent()
    builder.add_node("data_collector", data_collector.run)
    builder.add_node("enter_data_collector", create_entry_node("Data Collector", "data_collector"))
    builder.add_edge("enter_data_collector", "data_collector")

    # KG Builder agent
    kg_builder = KGBuilderAgent()
    builder.add_node("kg_builder", kg_builder.run)
    builder.add_node("enter_kg_builder", create_entry_node("Knowledge Graph Builder", "kg_builder"))
    builder.add_edge("enter_kg_builder", "kg_builder")

    # Add edges for primary assistant
    def route_primary_assistant(state: State) -> Literal["enter_data_collector", "enter_kg_builder", "__end__"]:
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls if state["messages"] else []
        if tool_calls[0]["name"] == ToDataCollectorAgent.__name__:
            return "enter_data_collector"
        elif tool_calls[0]["name"] == ToKGBuilderAgent.__name__:
            return "enter_kg_builder"
        return END

    builder.add_conditional_edges(
        "primary_assistant",
        route_primary_assistant,
        {
            "enter_data_collector": "enter_data_collector",
            "enter_kg_builder": "enter_kg_builder",
            END: END,
        },
    )

    # Add edges for specialized workflows
    def route_to_workflow(state: State) -> Literal["primary_assistant", "data_collector", "kg_builder"]:
        dialog_state = state.get("dialog_state", [])
        if not dialog_state:
            return "primary_assistant"
        return dialog_state[-1]

    builder.add_conditional_edges(START, route_to_workflow)

    # Add a node to pop dialog state and return to primary assistant
    def pop_dialog_state(state: State) -> dict:
        """Pop the dialog stack and return to the main assistant.

        This lets the full graph explicitly track the dialog flow and delegate control
        to specific sub-graphs.
        """
        messages = []
        if state["messages"][-1].tool_calls:
            # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
            messages.append(
                ToolMessage(
                    content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                    tool_call_id=state["messages"][-1].tool_calls[0]["id"],
                )
            )
        return {
            "dialog_state": "pop",
            "messages": messages,
        }

    builder.add_node("leave_skill", pop_dialog_state)
    builder.add_edge("leave_skill", "primary_assistant")

    # Add edges for specialized workflows to return to primary assistant
    builder.add_edge("data_collector", "leave_skill")
    builder.add_edge("kg_builder", "leave_skill")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

main_graph = create_graph()