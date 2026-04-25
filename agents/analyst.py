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
    - Receives independent research data for n subjects
    - Builds an n-way comparison from scratch
    - Works for 1 subject (deep analysis) or n subjects (comparison)
    """

    print("\n[Analyst] Starting analysis...")

    subjects = state.get("subjects", [])
    raw_research_per_subject = state.get("raw_research_per_subject", {})
    query = state.get("query", "")

    if not raw_research_per_subject:
        print("[Analyst] No research data found in state.")
        state["analysis"] = "No data available to analyze."
        return state

    # Build the research block for the prompt
    research_block = ""
    for subject in subjects:
        data = raw_research_per_subject.get(subject, "No data collected.")
        research_block += f"\n{data[:3000]}\n"

    # Dynamically build the prompt based on number of subjects
    if len(subjects) == 1:
        comparison_instruction = f"""
Produce a deep analysis report for {subjects[0]} with these sections:

1. OVERVIEW
   - Key facts, specs, pricing, and features based purely on the research data

2. STRENGTHS
   - What does the data say this subject excels at?

3. WEAKNESSES
   - What limitations or negatives appear in the data?

4. VALUE ANALYSIS
   - Is it worth the price? Use specific numbers.

5. FINAL VERDICT
   - Who should choose this and why?
"""
    else:
        subjects_list = ", ".join(subjects)
        comparison_instruction = f"""
Produce a structured {len(subjects)}-way comparison report for: {subjects_list}

Use these sections:

1. INDIVIDUAL PROFILES
{chr(10).join(f"   - Summarize key facts, specs, and figures for {s} based purely on its own independent data" for s in subjects)}

2. HEAD-TO-HEAD COMPARISON
   - Compare all {len(subjects)} subjects directly across every relevant dimension
   - Use actual numbers and data points wherever available
   - Present clear, factual side-by-side analysis

3. VALUE ANALYSIS
   - Which offers the best value for money and why?
   - Rank them from best to worst value with justification

4. TRENDS & MARKET POSITION
   - What does the data say about where each stands in the market?
   - Any notable patterns?

5. FINAL RECOMMENDATION
   - Which is best overall and for which type of user?
   - Give specific recommendations for different user needs
"""

    prompt = f"""
You are a professional market and technology analyst.
You have been given INDEPENDENT research data collected separately for each subject.
Build your analysis from scratch using only this raw data.
Do NOT rely on pre-existing comparisons. Form your own conclusions.

ORIGINAL QUERY: {query}

--- RESEARCH DATA ---
{research_block}

{comparison_instruction}

Be precise, use numbers wherever possible, and stay strictly based on the research data.
If data is missing for something, clearly state it rather than inventing numbers.
"""

    print(f"[Analyst] Analyzing {len(subjects)} subject(s) independently...")
    response = llm.invoke(prompt)
    analysis = response.content

    print("[Analyst] Analysis complete. Passing to Writer.")
    state["analysis"] = analysis
    return state