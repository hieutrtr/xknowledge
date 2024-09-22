from typing import Annotated, List, Dict, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    collected_data: Optional[List[Dict[str, str]]]
    identified_entities: Optional[List[str]]
    identified_relationships: Optional[List[Dict[str, str]]]
    knowledge_graph: Optional[Dict[str, List[Dict[str, str]]]]
    dialog_state: Annotated[
        list[Literal["enter_data_collector", "enter_kg_builder", "data_collector", "kg_builder"]],
        update_dialog_stack,
    ]