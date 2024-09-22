from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from state import State
from config import config
from agents import ToDataCollectorAgent, ToKGBuilderAgent

llm = AzureChatOpenAI(
    azure_deployment=config.AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME,
    openai_api_version=config.OPENAI_API_VERSION,
)

assistant_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant for building Knowledge Graphs. "
        "Use the provided tools to guide the user through collecting data and constructing the Knowledge Graph. "
        "When collecting data or building the graph, be thorough and persistent. "
        "If a step is unclear, ask for clarification before proceeding."
        "\nCurrent time: {time}.",
    ),
    ("placeholder", "{messages}"),
])

class Assistant:
    def __init__(self, runnable):
        self.runnable = runnable

    def __call__(self, state: State):
        while True:
            result = self.runnable.invoke(state)
            
            # If the LLM returns an empty response, re-prompt it
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        
        return {
            "messages": result
        }

assistant_runnable = assistant_prompt | llm.bind_tools(
   [
        ToDataCollectorAgent,
        ToKGBuilderAgent,
]
)