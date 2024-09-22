from langchain_core.tools import tool
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from crawl4ai import WebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from config import config

@tool
def find_web(topic: str) -> list[dict]:
    """Search and return data from the internet."""
    retriever = TavilySearchAPIRetriever(k=20, include_generated_answer=True, query=topic)
    docs = retriever.invoke(topic)
    # return content and url
    result = [{"content": doc.page_content, "url": doc.metadata["source"]} for doc in docs]
    return result

@tool
def get_webs_content(webs: list[dict], topic: str):
    """
    Description: scrape content from given webs (url) for given topic.
    topic: the topic of the content to be scraped based on the user's question.
    webs: list of web urls searched based on user's question.
    """
    print("topic:", topic)
    contents = []
    for web in webs:
        try:
            crawler = WebCrawler()
            crawler.warmup()
            result = crawler.run(
                url=web.get("url"),
                word_count_threshold=1,
                bypass_cache=True,
            )
            contents.append(result.extracted_content)
        except Exception as e:
            print(f"Error processing web {web.get('url')}: {str(e)}")
            continue
    return contents
