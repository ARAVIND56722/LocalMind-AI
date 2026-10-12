# The Lenny Growth Assistant
## Internal AI Editorial Research Studio for Product Managers & Growth Teams
**Oogway Labs | Forward Deployed Engineer Assignment**

---

### Overview
**The Lenny Growth Assistant** is an internal AI research and writing studio designed specifically for Product Managers, Growth Leads, and Founders. Grounded directly in transcripts from *Lenny’s Podcast* and *Lenny’s Newsletter*, it moves beyond generic chatbots by delivering:
1. **Verifiable, Grounded Q&A:** Synthesizes insights from world-class tech operators (e.g., Elena Verna, Shreyas Doshi, Tony Fadell, Claire Vo) with exact speaker citations, episode titles, and timestamps.
2. **Dedicated Ship 30 for 30 Writing Skill:** Transforms complex transcript takeaways into structured, atomic digital essays of approximately 1,250 words following the Ship 30 for 30 methodology (clear headline, slippery-slope hook, skimmable bolding/bullets, actionable takeaways, and a dedicated source-reference table).
3. **Sandboxed Artifact Studio:** Generates interactive Markdown documents and complete HTML/CSS artifacts, rendered beside the conversation in a secure, isolated sandbox with strict Content Security Policy enforcement.

---

### Architecture & Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, Asyncpg, Alembic |
| **Agent Engine** | **Pi Coding Agent Philosophy** — Model-agnostic, deterministic state & tool routing |
| **Persistence** | PostgreSQL (Docker Compose) with zero-config async SQLite (`aiosqlite`) fallback |
| **Models** | Local: **Ollama** (`llama3.2`, `mistral`) \| Cloud: **Anthropic Claude** & **OpenAI** \| Safe Evaluation Engine |
| **Knowledge Engine**| High-performance BM25 Okapi retriever with exact speaker/timestamp preservation |

---

### Key Capabilities & Workflows

#### 1. Grounded Question Answering
- Queries indexed dialogue chunks from Lenny's transcript library.
- Answers strictly from evidence.
- **Graceful Failure Handling:** If the question falls outside of Lenny's knowledge repository, the assistant explicitly responds:  
  `"Based on the available transcripts in Lenny's library, there is insufficient evidence to answer this question."`
- Real quotes and timestamps are rendered in interactive expandable source cards.

#### 2. Dedicated Ship 30 for 30 Digital Writing Skill
- Study of the Ship 30 for 30 framework encoded into `app/services/skills/ship30.py`.
- Formulates a high-converting headline, an open-loop hook, structured H3 headings, bold emphasis, and a 1-page playbook summary.
- Accompanied by verified source attributions at the bottom.

#### 3. Security-First Artifact Generation & Viewer
- Inspired by Claude Artifacts with side-by-side split view, word counter, and source toggling.
- Treats generated HTML as untrusted input:
  - `<script>` tags and inline event handlers (`onerror`, `onclick`) are automatically stripped.
  - Injects a restrictive Content Security Policy (`default-src 'none'; style-src 'unsafe-inline'; img-src data: https:;`).
  - Rendered in a sandboxed `iframe` with `sandbox="allow-same-origin"` to prevent cookie theft, localStorage access, or parent DOM manipulation.

---

### Quickstart Guide

#### Option A: Docker Compose (One-Command Deployment)
```bash
# 1. Clone the repository and navigate into it
git clone <repo-url>
cd lenny-growth-assistant

# 2. Copy the example environment configuration
cp .env.example .env

# 3. Start all services (PostgreSQL, FastAPI Backend, React Frontend)
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

#### Option B: Local Developer Startup (Zero-Install Database)

**1. Backend Setup:**
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**2. Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

### Running Automated Tests
The backend features automated test coverage across health checks, session lifecycle, grounded search, insufficient evidence acknowledgment, and Ship 30 skill execution:

```bash
cd backend
python -m pytest tests/ -v
```
**Test Results:** `6 passed, 0 failed (100% success rate)`

---

### Operational Readiness & Troubleshooting

- **Ollama Status:** The sidebar includes a live status monitor. If local Ollama is offline (`ollama serve`), the badge accurately displays `Offline` and allows one-click switching to Cloud Claude/OpenAI or the built-in evaluation engine without crashing.
- **Database Resilience:** If Docker is not running on a developer machine, the backend automatically falls back to local SQLite (`lenny_growth.db`), ensuring zero evaluation friction.
- **Re-indexing Knowledge Base:** To re-index transcripts at any time:
  ```bash
  python scripts/ingest.py
  ```

---

### Submission Deliverables Checklist
- [x] **PRD:** [`docs/PRD.md`](file:///c:/Users/akara/OneDrive/Documents/Oogway/docs/PRD.md)
- [x] **Architecture Specification:** [`docs/architecture.md`](file:///c:/Users/akara/OneDrive/Documents/Oogway/docs/architecture.md)
- [x] **Design & UX Guidelines:** [`docs/design.md`](file:///c:/Users/akara/OneDrive/Documents/Oogway/docs/design.md)
- [x] **Manual Test Plan:** [`docs/manual-test-plan.md`](file:///c:/Users/akara/OneDrive/Documents/Oogway/docs/manual-test-plan.md)
- [x] **Agent Trajectory Log:** [`agent-transcripts/development-log.md`](file:///c:/Users/akara/OneDrive/Documents/Oogway/agent-transcripts/development-log.md)
- [x] **Automated Tests:** [`backend/tests/test_backend.py`](file:///c:/Users/akara/OneDrive/Documents/Oogway/backend/tests/test_backend.py)
- [x] **Docker Compose Topology:** [`docker-compose.yml`](file:///c:/Users/akara/OneDrive/Documents/Oogway/docker-compose.yml)
