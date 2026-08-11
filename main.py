from src.tools import tools

# web_search_query = "Recent advancements in AI research"
# search_results = tools.web_search(web_search_query)
# print(f"Search results for '{web_search_query}':\n{search_results}")

# url = "https://www.geeksforgeeks.org/python/implementing-web-scraping-python-beautiful-soup"
# scraped_content = tools.scrape_url(url)
# print(f"Scraped content from {url}:\n{scraped_content}")


from src.pipeline.pipeline import run_research_pipeline

topic  = "Recent advancements in AI research"
run_research_pipeline(topic)