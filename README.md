# ◈ Autonomous Market & Tech Analyst Agent

> A multi-agent AI research system that autonomously searches the web, analyzes data, and generates professional PDF reports — with persistent memory and human-in-the-loop control.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-7c6ee0?style=flat-square)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Memory-2a9d6e?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-e94560?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## What Is This?

This project is a fully autonomous research pipeline powered by three specialized AI agents that work together to turn any research query into a structured, professional PDF report.

You type a question. The agents do the rest.

---

## How It Works

```
User Query
    │
    ▼
┌─────────────────────────────┐
│   Agent 1 · Researcher      │  Searches the web, checks memory
│   Tavily + BeautifulSoup    │  for past research, scrapes pages
└────────────┬────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Human-in-Loop │  You choose which 3 sources to focus on
     └───────┬───────┘
             │
             ▼
┌─────────────────────────────┐
│   Agent 2 · Analyst         │  Extracts facts, calculates
│   Groq LLM (Llama 3)        │  price-to-performance ratios,
│                             │  identifies trends
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Agent 3 · Writer          │  Formats everything into a
│   ReportLab                 │  professional PDF with citations
└────────────┬────────────────┘
             │
             ▼
      PDF Report + Memory
      saved to ChromaDB
```

---

## Key Features

- **3-Agent Pipeline** — Researcher, Analyst, and Writer agents each handle a specialized role and pass work to each other via a shared state object
- **Human-in-the-Loop** — The pipeline pauses after the search step and lets you select which sources to focus on before analysis begins
- **Persistent Memory** — ChromaDB stores every research session locally. Next time you research a similar topic, past findings are automatically retrieved and included
- **PDF Report Generation** — Every research session produces a styled, downloadable PDF with citations
- **Fully Local Memory** — Embeddings run on your machine via `sentence-transformers`. No paid embedding API needed
- **Professional UI** — Built with Streamlit, featuring a live agent activity log, dark theme, and smooth loading states

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Orchestration | LangGraph | Stateful multi-agent pipeline with conditional edges |
| LLM | Groq (Llama 3.3 70B) | Fast, free inference for analysis |
| Web Search | Tavily API | AI-optimized search returning clean results |
| Web Scraping | BeautifulSoup + Requests | Extracting full page content from URLs |
| Vector Memory | ChromaDB | Local persistent storage for past research |
| Embeddings | sentence-transformers | Local text embeddings, no API key needed |
| PDF Generation | ReportLab | Programmatic PDF creation with custom styling |
| UI | Streamlit | Interactive web interface |
| Environment | python-dotenv | Secure API key management |

---

## Project Structure

```
market-analyst-agent/
├── agents/
│   ├── researcher.py        # Agent 1 — web search + scraping
│   ├── analyst.py           # Agent 2 — LLM-powered analysis
│   └── writer.py            # Agent 3 — PDF report generation
├── tools/
│   ├── search.py            # Tavily web search wrapper
│   └── scraper.py           # BeautifulSoup page scraper
├── memory/
│   └── chroma_store.py      # ChromaDB save/retrieve/clear
├── graph/
│   └── pipeline.py          # LangGraph pipeline definition
├── ui/
│   └── app.py               # Streamlit frontend
├── outputs/                 # Generated PDF reports saved here
├── chroma_db/               # Local vector database (auto-created)
├── .env                     # API keys (never commit this)
├── .gitignore
└── requirements.txt
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Anish-000/market-analyst-agent.git
cd market-analyst-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your free API keys

**Groq** — Go to [console.groq.com](https://console.groq.com), sign up for free, and create an API key.

**Tavily** — Go to [app.tavily.com](https://app.tavily.com), sign up for free, and copy your API key from the dashboard.

### 4. Create your `.env` file

```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 5. Run the app

```bash
python -m streamlit run ui/app.py
```

Your browser will open automatically at `http://localhost:8501`.

---

## Example Queries

The system works for any research topic, not just tech.

- `Compare Nvidia RTX 5090 vs AMD RX 9070 for deep learning`
- `Lays vs Kurkure — brand comparison and consumer sentiment`
- `Microsoft 365 vs Google Workspace for small businesses`
- `Lionel Messi vs Cristiano Ronaldo — career statistics comparison`
- `Best budget smartphones under $300 in 2026`

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key for LLM inference |
| `TAVILY_API_KEY` | Your Tavily API key for web search |

---

## Important Notes

- The `chroma_db/` folder is created automatically on first run. It stores your research memory permanently on disk.
- The `outputs/` folder is created automatically and stores all generated PDF reports.
- Neither `chroma_db/` nor `outputs/` nor `.env` should ever be pushed to GitHub. They are included in `.gitignore`.
- On first run, `sentence-transformers` will download a small model (~90MB) to your machine. This only happens once.

---

## Architecture Notes

**Why LangGraph over a simple chain?**
LangGraph allows the pipeline to have conditional edges — the graph can pause mid-run, wait for user input, and resume. A simple LangChain chain cannot do this.

**Why ChromaDB for memory?**
ChromaDB runs entirely locally with no server setup. It stores vector embeddings on disk and survives between sessions, which is exactly what persistent research memory needs.

**Why Groq instead of OpenAI?**
Groq provides free, extremely fast inference on Llama 3 models. For a portfolio project with no budget, it is the best option available.

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with Python · LangGraph · ChromaDB · Groq · Streamlit*