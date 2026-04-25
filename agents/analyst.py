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
    - Receives two separate research blocks for Subject A and Subject B
    - Builds comparison from scratch using independent data
    - Calculates price-to-performance ratios
    - Identifies trends and gives a final recommendation
    """

    print("\n[Analyst] Starting independent comparison analysis...")

    subject_a = state.get("subject_a", "Subject A")
    subject_b = state.get("subject_b", "Subject B")
    raw_research_a = state.get("raw_research_a", "")
    raw_research_b = state.get("raw_research_b", "")
    query = state.get("query", "")

    if not raw_research_a and not raw_research_b:
        print("[Analyst] No research data found in state.")
        state["analysis"] = "No data available to analyze."
        return state

    prompt = f"""
You are a professional market and technology analyst.
You have been given INDEPENDENT research data collected separately for two subjects.
Your job is to build a comparison from scratch using only this raw data.
Do NOT rely on any pre-existing comparisons. Build your own analysis.

ORIGINAL QUERY: {query}

--- INDEPENDENT DATA FOR: {subject_a} ---
{raw_research_a[:3000]}

--- INDEPENDENT DATA FOR: {subject_b} ---
{raw_research_b[:3000]}

Now produce a structured comparison report with these exact sections:

1. INDIVIDUAL PROFILES
   - Summarize key facts, specs, and figures for {subject_a} based purely on its own data
   - Summarize key facts, specs, and figures for {subject_b} based purely on its own data

2. HEAD-TO-HEAD COMPARISON
   - Compare them directly across every relevant dimension (price, performance, features, quality, value, etc.)
   - Use actual numbers and data points wherever available
   - Present this as a clear, factual side-by-side analysis

3. PRICE-TO-PERFORMANCE / VALUE ANALYSIS
   - Which offers better value for money and why?
   - Use specific numbers to justify your conclusion

4. TRENDS & MARKET POSITION
   - What does the data tell you about where each stands in the market?
   - Any notable patterns or observations?

5. FINAL RECOMMENDATION
   - Based purely on the independent data you analyzed, which is better and for whom?
   - Be specific — different recommendations for different user types if applicable

Be precise, use numbers wherever possible, and stay strictly based on the research data provided.
Do not invent data. If something is not in the research, say so clearly.
"""

    print("[Analyst] Sending independent datasets to LLM for comparison...")

    response = llm.invoke(prompt)
    analysis = response.content

    print("[Analyst] Comparison analysis complete. Passing to Writer.")

    state["analysis"] = analysis
    return state