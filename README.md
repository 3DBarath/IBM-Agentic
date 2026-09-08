# IBM Agentic AI Track: Multi-Round Talent Intelligence & Recruitment Assistant

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-black?logo=vercel)](https://barath-agentic-hr.vercel.app/)
[![TNSDC Virtual Internship Program](https://img.shields.io/badge/TNSDC-IBM%20Agentic%20AI-blue.svg)](https://www.naanmudhalvan.tn.gov.in/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-green.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-v0.2-blue)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange)](https://langchain-ai.github.io/langgraph/)

🔗 **Live Demo:** [https://barath-agentic-hr.vercel.app/](https://barath-agentic-hr.vercel.app/)

An end-to-end Agentic AI recruitment platform designed for the **TNSDC Virtual Internship Program (IBM Agentic AI Track)**. The platform combines **LangChain Tool-Calling**, **LangGraph Workflow Orchestration**, **Agentic RAG Semantic Search**, and **Ollama Cloud LLMs (`gpt-oss:120b`)** to evaluate candidates against job descriptions and formulate tailored, multi-round technical interview kits.

---

## 🌟 Key Features

1. **Agentic RAG & Evidence Retrieval**:
   - Chunks candidate resumes into semantic units and computes vector similarity against the target Job Description (JD).
   - Identifies substantiated experience vs unverified skill claims.
2. **Deterministic Match & Gap Scoring**:
   - Calculates overall candidate alignment (0-100%) incorporating skill overlap, semantic relevance, and breadth of experience.
   - Highlights matching capabilities, missing requirements, and adjacent strengths.
3. **Multi-Round Real-World Interview Kit**:
   Generates targeted questions with expected answer rubrics across 4 industry-standard interview loops:
   - **Round 1:** Initial Recruiter Screening (Career trajectory, motivation, team fit).
   - **Round 2:** Core Technical & Coding Screen (Language depth, DSA, problem-solving).
   - **Round 3:** System Architecture & Design (Scalability, trade-offs, microservices, databases).
   - **Round 4:** Behavioral & Team Leadership (STAR Framework: Situation, Task, Action, Result).
4. **State-of-the-Art Reactive Dashboard**:
   - Built under `@make-interfaces-feel-better` and modern web standards.
   - Sub-30ms local reactive interactions.
   - Zero emojis (clean SVG icons with matched optical stroke weights).
   - Concentric border radii, tactile `scale(0.96)` click feedback, and tabular numeric score indicators.
5. **Security First**:
   - Dedicated Python `.venv` isolation.
   - Zero API key leaks; secrets strictly managed through `.env` and excluded via `.gitignore`.

---

## 🏗️ Architecture & LangGraph State Machine

```
User Input (PDF Resume + Job Description)
                     │
                     ▼
         [Node 1: parse_and_chunk]
         - Document extraction (PyPDF)
         - Text chunking & skill catalog matching
                     │
                     ▼
         [Node 2: rag_retrieval]
         - In-memory vector semantic index
         - Querying against Job Description
         - Evidence extraction & score weighting
                     │
                     ▼
       [Node 3: analyze_candidate]
         - Candidate profiling via Ollama Cloud
         - Skill gap analysis
                     │
                     ▼
    [Node 4: generate_interview_kit]
         - Round 1: Screening Questions + Rubric
         - Round 2: Technical / Coding Questions
         - Round 3: System Design Scenarios
         - Round 4: Behavioral (STAR) Matrix
                     │
                     ▼
       [Node 5: synthesize_dossier]
         - Executive evaluation dossier
         - Downloadable Markdown & JSON payload
```

---

## 📅 Alignment with TNSDC / IBM 5-Day Curriculum

| Day | Syllabus Topic | Implementation in Project |
| :--- | :--- | :--- |
| **Day 1** | Agentic AI & Project Foundation | Model setup (`gpt-oss:120b` via Ollama Cloud), environment isolation (`.venv`), and project scope. |
| **Day 2** | Building the AI Agent & Tools | Custom tools for PDF extraction, skill parsing, and deterministic score computation (`src/tools.py`). |
| **Day 3** | LangGraph & Multi-Step Workflow | `StateGraph` state machine with 5 nodes, typed state dictionaries, and error fallbacks (`src/graph.py`). |
| **Day 4** | Agentic RAG Pipeline | Semantic chunking, cosine vector similarity search, and evidence augmentation (`src/rag.py`). |
| **Day 5** | End-to-End Project & Demo | Full integration with FastAPI backend, reactive dashboard, and exportable dossiers (`src/server.py`). |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/<your-username>/IBM-Agentic.git
cd IBM-Agentic

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and verify your configuration:
```env
OLLAMA_API_KEY=your_ollama_cloud_api_key
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gpt-oss:120b
PORT=8000
HOST=0.0.0.0
```

### 4. Run Application
```bash
python -m src.server
```
Visit **`http://localhost:8000`** in your browser.

---

## 🧪 Testing & Verification
To test the core LangGraph workflow directly via Python:
```bash
source .venv/bin/activate
python -c "from src.graph import recruitment_agent; print('LangGraph compiled successfully:', recruitment_agent is not None)"
```

---

## 📂 Project Structure
```
IBM-Agentic/
├── .env.example           # Example environment template
├── .gitignore             # Strict exclusions (.env, .venv, uploads)
├── requirements.txt       # Version-pinned Python dependencies
├── README.md              # Project documentation and submission report
├── src/
│   ├── config.py          # Secure environment & path loader
│   ├── llm.py             # Ollama Cloud API client
│   ├── rag.py             # PDF extraction & semantic vector store
│   ├── tools.py           # Skill extraction & match metrics
│   ├── graph.py           # 5-Node LangGraph workflow
│   └── server.py          # FastAPI application & REST endpoints
└── static/
    ├── index.html         # Accessible HTML dashboard
    ├── styles.css         # Modern design system (No glassmorphism)
    └── app.js             # Reactive DOM controller (<30ms interactions)
```

---

## 👥 Authors & Acknowledgments
- **Project Track:** IBM Agentic AI Track - TNSDC Virtual Internship Program
- **Partner:** Adroit Technologies Innovative Solutions Pvt. Ltd. in association with IBM
