from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import BaseTool
from state import State
from tools.data_collector import identify_topic_by_purpose, search_web_by_topic, crawl_web_by_url, extract_information_by_topic
from tools.kg_builder import identify_data_entities_relationships, convert_data_to_KG
from config import config
from pydantic import BaseModel, Field
from typing import List, Dict

llm = AzureChatOpenAI(
    azure_deployment=config.AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME,
    openai_api_version=config.OPENAI_API_VERSION,
)

class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the user's emails or calendar for more information.",
            },
        }

class ToDataCollectorAgent(BaseModel):
    """Transfers work to the Data Collector agent to handle all necessary steps for data collection from the internet based on a given purpose or topic."""
    purpose: str = Field(
        description="The purpose or topic for which data needs to be collected."
    )

class ToKGBuilderAgent(BaseModel):
    """Transfers work to the KG Builder agent to handle all necessary steps for building a knowledge graph from the collected data."""
    collected_data: List[Dict[str, str]] = Field(
        description="The collected data from the internet based on a given purpose or topic."
    )

class DataCollectorAgent:
    def __init__(self):
        self.tools = [identify_topic_by_purpose, search_web_by_topic, crawl_web_by_url, extract_information_by_topic]
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a specialized assistant for collecting data from the internet. "
                "The primary assistant delegates work to you whenever the user needs help gathering information on a specific topic or purpose. "
                "Use the provided tools to identify topics, search the web, crawl websites, and extract relevant information. "
                "Be thorough and persistent in your data collection. If initial searches don't yield sufficient results, expand your query or try alternative approaches. "
                "If you need more information or the user changes their mind, use the CompleteOrEscalate function to return control to the main assistant. "
                "Remember that the data collection process isn't complete until after the relevant tools have been successfully used to gather comprehensive information. "
                "\n\nCurrent data collection purpose:\n<Purpose>\n{purpose}\n</Purpose>"
                "\n\nIf the user needs help, and none of your tools are appropriate for it, then "
                '"CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.',
            ),
            ("placeholder", "{messages}"),
        ])
        self.runnable = self.prompt | llm.bind_tools(self.tools + [CompleteOrEscalate])

    def run(self, state: State) -> Dict:
        result = self.runnable.invoke({"input": state["messages"][-1].content})
        return {"collected_data": result.collected_data}

class KGBuilderAgent:
    def __init__(self):
        self.tools = [identify_data_entities_relationships, convert_data_to_KG]
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a specialized assistant for building Knowledge Graphs. "
                "The primary assistant delegates work to you whenever the user needs help constructing a knowledge graph from collected data. "
                "Use the provided tools to identify entities, relationships, and convert the data into a knowledge graph structure. "
                "Be thorough and persistent in your graph construction. If initial attempts don't yield a comprehensive graph, try alternative approaches or ask for clarification. "
                "If you need more information or the user changes their mind, use the CompleteOrEscalate function to return control to the main assistant. "
                "Remember that the knowledge graph construction isn't complete until after the relevant tools have been successfully used to create a comprehensive graph structure. "
                "\n\nCurrent collected data:\n<CollectedData>\n{collected_data}\n</CollectedData>"
                "\n\nIf the user needs help, and none of your tools are appropriate for it, then "
                '"CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.',
            ),
            ("placeholder", "{messages}"),
        ])
        self.runnable = self.prompt | llm.bind_tools(self.tools)

    def run(self, state: State) -> Dict:
        result = self.runnable.invoke({"input": state["collected_data"]})
        return {
            "identified_entities": result.identified_entities,
            "identified_relationships": result.identified_relationships,
            "knowledge_graph": result.knowledge_graph
        }