from langchain_core.tools import tool
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from crawl4ai import WebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from config import config

@tool
def find_web(topic: str) -> list[dict]:
    """Find the webs on the internet that are relevant to the topic."""
    retriever = TavilySearchAPIRetriever(k=13)
    docs = retriever.invoke(topic)
    # return content and url
    result = [{"content": doc.page_content, "url": doc.metadata["source"]} for doc in docs]
    return result

@tool
def get_webs_content(webs: list[dict]):
    """crape content from given web url instructed by content."""
    contents = []
    for web in webs:
        try:
            crawler = WebCrawler()
            crawler.warmup()
            result = crawler.run(
                url=web.get("url"),
                word_count_threshold=1,
                extraction_strategy=LLMExtractionStrategy(
                    provider="gpt-4", api_token=config.OPENAI_API_KEY,
                    extraction_type="schema",
                    instruction="From the crawled content, extract all mentioned about {content}".format(content=web.get("content"))
                ),            
                bypass_cache=True,
            )
            contents.append(result.extracted_content)
        except Exception as e:
            print(f"Error processing web {web.get('url')}: {str(e)}")
            continue
    return contents
