from crewai.tools import tool
from tavily import TavilyClient
from pypdf import PdfReader
from config import TAVILY_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@tool("Web Search Tool")
def search_tool(query: str) -> str:
    """Searches the web for up-to-date information on a given query using Tavily."""
    try:
        results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
            include_raw_content=False,
            include_domains=[
                "wikipedia.org",
                "britannica.com",
                "nature.com",
                "pubmed.ncbi.nlm.nih.gov",
                "scholar.google.com",
                "ibm.com",
                "microsoft.com",
                "google.com",
                "mckinsey.com",
                "harvard.edu",
                "mit.edu",
                "stanford.edu",
                "who.int",
                "un.org",
                "forbes.com",
                "techcrunch.com"
            ]
        )
        output = ""
        if results.get("answer"):
            output += f"Quick Answer: {results['answer']}\n\n"
        output += "Detailed Sources:\n"
        for i, r in enumerate(results["results"], 1):
            output += f"\nSource {i}:\n"
            output += f"Title: {r['title']}\n"
            output += f"URL: {r['url']}\n"
            output += f"Content: {r['content']}\n"
            output += f"Score: {r.get('score', 'N/A')}\n"
            output += "-" * 40 + "\n"
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool("PDF Reader Tool")
def pdf_tool(pdf_path: str) -> str:
    """Reads and extracts text content from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        return f"PDF reading failed: {str(e)}"