from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from datetime import datetime
from graph.state import State
from config import config
from tools.web import find_web, get_webs_content

ASSISTANT_MODEL = config.ASSISTANT_MODEL

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
    
llm = ChatOpenAI(model=ASSISTANT_MODEL, temperature=0)

assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful data assistant. Your job is search for information around a given topic to build knowledge base for the topic."
            "Your workflow will be:"
            "\n1. Search on the internet for web urls and contents. "
            "\n2. Collect information from each web url into dataset. "
            "\nThe results from your work are a response to user and a dataset about the topic and user's question."
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

assistant_tools = [find_web, get_webs_content]

assistant_runnable = assistant_prompt | llm.bind_tools(assistant_tools)
