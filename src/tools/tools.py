from langchain_core.tools import tool

import os
import re
import requests
import trafilatura

from bs4 import BeautifulSoup
from readability import Document
from tavily import TavilyClient
from dotenv import load_dotenv


load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def web_search(query: str) -> str:
    """Search the web using Tavily and return relevant search results.

    Args:
        query: The search query to execute.

    Returns:
        A formatted list of search results containing titles,
        URLs, and snippets.
    """

    try:
        response = tavily.search(
            query=query,
            max_results=5
        )

        results = response.get("results", [])

        if not results:
            return "No search results were found."

        output = []

        for result in results:
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")

            output.append(
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Snippet: {content[:500]}\n"
            )

        return "\n".join(output)

    except Exception as e:
        return f"Web search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and extract readable text from a webpage.

    Args:
        url: The URL of the webpage to scrape.

    Returns:
        Cleaned textual content from the webpage.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        html = response.text

        # Strategy 1: Trafilatura
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", extracted)
            return cleaned[:5000]

        # Strategy 2: Readability
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(
            clean_html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", text)
            return cleaned[:5000]

        # Strategy 3: Full page fallback
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            text
        )

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"