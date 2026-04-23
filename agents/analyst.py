from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.3
)


def analyst_agent(state: dict) -> dict:
    """
    Agent 2: Analyst
    - Takes raw research content from Agent 1
    - Uses LLM to extract specs, prices, and benchmark numbers
    - Calculates price-to-performance ratios
    - Identifies key trends and patterns
    - Updates and returns the shared state
    """

    print("\n[Analyst] Starting analysis...")

    raw_research = state.get("raw_research", "")
    query = state.get("query", "")

    if not raw_research:
        print("[Analyst] No research data found in state.")
        state["analysis"] = "No data available to analyze."
        return state

    # Build the prompt for the LLM
    prompt = f"""
You are a professional market and technology analyst. 
You have been given raw research data about the following topic:

TOPIC: {query}

RAW RESEARCH DATA:
{raw_research[:6000]}

Your job is to analyze this data and produce a structured analysis. 
You must include the following sections:

1. KEY FINDINGS
   - List the most important facts, numbers, and specs found in the research
   - Include exact prices where available
   - Include exact benchmark scores or performance numbers where available

2. PRICE-TO-PERFORMANCE ANALYSIS
   - Calculate or estimate price-to-performance ratios based on the data
   - Compare which option gives the best value for money
   - Be specific with numbers

3. TRENDS & PATTERNS
   - What patterns do you see across the data?
   - What direction is the market moving?
   - Any notable observations?

4. RECOMMENDATION
   - Based purely on the data, which option is best for deep learning / AI workloads?
   - Who should buy which product and why?

Be precise, use numbers wherever possible, and stay strictly based on the research data provided.
"""

    print("[Analyst] Sending data to LLM for analysis...")

    response = llm.invoke(prompt)
    analysis = response.content

    print("[Analyst] Analysis complete. Passing to Writer.")

    # Update state with the analysis
    state["analysis"] = analysis
    return state