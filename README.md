<div align="center">

# ⚖️ Multi-Agent AI Decision Debater

**Stop making big decisions alone. Let 6 AI agents argue it out first.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-purple?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70b-orange?style=flat-square)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)



</div>

---

## What Is This?

Most people make big decisions by Googling for 10 minutes and trusting their gut. This project takes a different approach — you describe your decision, and a team of 6 specialized AI agents debate every angle of it before delivering a confidence-scored verdict.

It is not a chatbot. It is a **multi-agent debate system** built on LangGraph, where each agent has a distinct role, personality, and objective.

---

## How It Works

```
                    ┌─────────────────┐
                    │  Orchestrator   │  ← Frames the debate dimensions
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   Optimist  │   │   Devil's   │   │    Risk     │
   │             │   │  Advocate   │   │   Analyst   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                    ┌─────────────────┐
                    │   Researcher    │  ← Searches the live web
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Judge       │  ← Delivers the verdict
                    └─────────────────┘
```

The Optimist, Devil's Advocate, and Risk Analyst run **in parallel** — simultaneously — using LangGraph's graph execution model. This is not a simple sequential chain. It is a true directed graph with parallel branches.

---

## The Agents

| Agent | Role |
|---|---|
| 🧠 **Orchestrator** | Breaks your decision into key evaluation dimensions and coordinates the debate |
| ☀️ **Optimist** | Builds the strongest possible case *for* your decision |
| 😈 **Devil's Advocate** | Tears the optimist's case apart with logic and counter-evidence |
| 🛡️ **Risk Analyst** | Identifies specific risks, assigns severity scores, suggests mitigations |
| 🔍 **Researcher** | Searches the live internet via Tavily and synthesizes a clean evidence briefing |
| ⚖️ **Judge** | Weighs all arguments and delivers a verdict with a confidence score and next steps |

---

## Features

- **Parallel agent execution** — three agents run simultaneously, not sequentially
- **Live web research** — the Researcher agent pulls real, current data at runtime
- **Confidence scoring** — the Judge returns a 0–100% confidence score with the verdict
- **Adjustable judge harshness** — dial from 1 (lenient) to 5 (brutal) in Advanced Settings
- **Toggle agents on/off** — exclude any agent from the debate
- **Clean dark UI** — built with Streamlit and custom CSS

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| LLM | Llama 3.3-70b via [Groq](https://groq.com) |
| Web research | [Tavily Search API](https://tavily.com) |
| Frontend | [Streamlit](https://streamlit.io) |
| Language | Python 3.10+ |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com) — no credit card required
- A free [Tavily API key](https://app.tavily.com) — no credit card required

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/multi-agent-decision-debater.git
cd multi-agent-decision-debater

# 2. Create and activate a virtual environment
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Project Structure

```
multi-agent-decision-debater/
├── debate_team.py      # Agent definitions, prompts, and LangGraph graph
├── app.py              # Streamlit web interface
├── requirements.txt    # Python dependencies
├── .env                # API keys (never committed)
├── .gitignore
└── README.md
```

---

## Requirements

Create a `requirements.txt` with the following:

```
langchain
langgraph
langchain-groq
langchain-community
tavily-python
streamlit
python-dotenv
```

---

## Usage Example

**Input:**
> Decision: Should I quit my job to start an AI consulting business?
> Context: I am 26, have 3 years of ML experience, $20k in savings, no dependents.

**Output:**
- Orchestrator identifies 4 evaluation dimensions
- Optimist, Devil's Advocate, and Risk Analyst argue in parallel
- Researcher finds current market data on AI consulting demand
- Judge delivers: `PROCEED WITH CAUTION — 67% confidence`
- Concrete next steps and critical assumptions to validate

---

## Roadmap

- [ ] Memory — save and revisit past debates
- [ ] Export verdict as PDF report
- [ ] Debate history dashboard
- [ ] API endpoint for integration into other apps

---

## License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Built with LangGraph · Groq · Tavily · Streamlit

</div>
