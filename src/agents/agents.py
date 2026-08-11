from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key = os.getenv("GROQ_API_KEY"),
    model = "llama-3.3-70b-versatile",
    temperature = 0
)

# Search Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt="""
You are a web research agent.

Your job is to research the user's topic using the web_search tool.

Always use web_search when external information is needed.

Search for:
- Recent information
- Reliable sources
- Relevant facts
- Important findings

Do not invent information.

After completing the search, summarize the findings clearly.
"""
    )


# Reader Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt="""
You are a research reading agent.

Your job is to analyze webpages and extract useful information.

Use scrape_url when a URL needs to be read.

Extract:
- Important facts
- Evidence
- Statistics
- Key findings
- Relevant conclusions

Do not invent information that is not present in the source.
"""
    )

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that writes a comprehensive report based on the information provided."),
    ("human", """Please write a detailed report based on the following topic and information.

    Topic : {topic}

    Research Gathered: {research}

    Structure the report as:
    - Introduction
    - Key findings (minimum 3 well explained points)
    - Conclusion
    - Sources (if any)

    Be sure to provide a well-structured and coherent report, using the information provided. If any information is missing or unclear, make reasonable assumptions and clearly state them in the report."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

critical_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a critical thinking assistant that evaluates the quality and reliability of research information."),
    ("human", """Please evaluate the following research information for quality and reliability.

    Report:
    {report}

    Response in this format:

    Score: X/10 (Provide a score out of 10 based on the quality and reliability of the information.)
    Feedback: (Provide detailed feedback on the strengths and weaknesses of the research information, including any potential biases, gaps, or areas for improvement.)
    Suggestions: (Provide specific suggestions for improving the quality and reliability of the research information, including any additional sources or methods that could be used to gather more reliable information.)"""),
])


critical_chain = critical_prompt | llm | StrOutputParser()