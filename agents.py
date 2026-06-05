from crewai import Agent
from tools import search_tool, pdf_tool

researcher = Agent(
    role="Research Agent",
    goal="Find the most relevant and up-to-date information on the given topic",
    backstory="""You are an expert researcher who finds accurate information 
    from the web and documents. You always cite your sources.""",
    tools=[search_tool, pdf_tool],
    llm="groq/llama-3.3-70b-versatile",
    function_calling_llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False
)

analyst = Agent(
    role="Analysis Agent",
    goal="Analyse and extract key insights from the research findings",
    backstory="""You are a critical thinker who reads research and pulls out 
    the most important themes, facts, and patterns.""",
    llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False
)

writer = Agent(
    role="Writing Agent",
    goal="Write a clear, structured research report from the analysis",
    backstory="""You are a professional writer who turns complex analysis 
    into clear, well-structured reports with proper sections and bullet points.""",
    llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False
)

reviewer = Agent(
    role="Review Agent",
    goal="Review the report for accuracy, clarity and completeness",
    backstory="""You are a strict editor who checks reports for factual 
    accuracy, missing information, and unclear writing. You suggest improvements.""",
    llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False
)