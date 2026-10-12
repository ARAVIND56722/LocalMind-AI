# System Architecture Document
## The Lenny Growth Assistant — Production FDE Architecture
**Version:** 1.0.0  
**Status:** Approved  

---

### 1. High-Level Architecture Overview

```mermaid
graph TD
    subgraph Frontend ["Editorial Studio (React + Vite + Tailwind + Framer Motion)"]
        UI_Chat[Chat Workspace & Session History]
        UI_Artifact[Sandboxed Artifact Viewer (Markdown + Isolated HTML/CSS iframe)]
        UI_Model[Model & Provider Status Drawer]
        API_Client[Typed API Client]
    end

    subgraph Backend ["FastAPI Application (Port 8000)"]
        Router[API Routers: /health, /api/sessions, /api/chat, /api/skills, /api/artifacts, /api/models]
        AgentEngine[Pi Agent Routing & Orchestration Engine]
        
        subgraph Submodules ["Core Services"]
            RAG[Retrieval & Grounding Service]
            Ship30Skill[Dedicated Ship 30 for 30 Skill]
            ArtifactService[Artifact Compiler & Security Sanitizer]
            ProviderGateway[LLM Provider Gateway (Ollama, Claude, OpenAI, Fallback)]
        end

        subgraph Storage ["Persistence & Knowledge"]
            DB[(PostgreSQL / SQLite Dual-Engine Engine)]
            VectorStore[(BM25 + Semantic Passage Index)]
        end
    end

    UI_Chat --> API_Client
    UI_Artifact --> API_Client
    UI_Model --> API_Client
    API_Client --> Router
    Router --> AgentEngine
    AgentEngine --> RAG
    AgentEngine --> Ship30Skill
    AgentEngine --> ArtifactService
    RAG --> VectorStore
    AgentEngine --> ProviderGateway
    Router --> DB
```

---

### 2. Design Principles & Key Decisions

1. **Agent Engine Selection (Pi Coding Agent Philosophy):**
   - We adopt the **Pi Agent** design philosophy: an unbloated, transparent, model-agnostic execution harness.
   - Unlike heavy black-box orchestrators that generate infinite loops, the Pi Agent evaluates intent (Q&A vs. Ship 30 Essay vs. Artifact), binds tools explicitly, injects verified conversation history, and invokes the chosen model provider with deterministic fallback.

2. **Grounding & Knowledge Architecture:**
   - Ingestion reads curated Markdown transcripts from Lenny's library (`podcasts/` and `newsletters/`).
   - Metadata is rigorously preserved: Episode Title, Guest Name, Transcript Timestamp, Episode URL, and Topic Tags.
   - Retrieval uses hybrid scoring: BM25 keyword matching + fast vector scoring. Passages are tagged with `[Ref: ID - Episode Title - Speaker - Timestamp]`.
   - Answers must cite passages using these tags. Hallucinated citations are rejected.

3. **Dedicated Ship 30 for 30 Writing Skill:**
   - Extracted from digital writing frameworks:
     - Clear Headline (Stop the scroll: "How [Subject] unlocked [Outcome]")
     - Compelling 1-2 sentence hook creating an open loop.
     - Section headings with rhythm and progression.
     - Bold emphasis on key terms; bullet points for skimmability.
     - 1,200 to 1,300 words target length.
     - Actionable conclusion with 1-page playbook summary.
     - Traceable source references at the end.

4. **Security & Sandboxed Artifact Isolation:**
   - HTML/CSS artifacts are rendered inside an isolated `iframe` with `sandbox="allow-same-origin"` and an injected Content Security Policy (`default-src 'none'; style-src 'unsafe-inline' https:; img-src data: https:; font-src https: data:;`).
   - Scripts are disabled (`script-src 'none'`), cookie and localStorage access is completely blocked, and parent DOM navigation is forbidden.
   - Users can toggle between **Preview** and **Source Code** with syntax highlighting and copy buttons.

5. **Multi-Provider Resilience (Ollama & Cloud):**
   - Local: Ollama (`http://localhost:11434/api/generate` and `/api/tags`).
   - Cloud: Anthropic Claude (`claude-3-5-sonnet`, `claude-3-haiku`) and OpenAI (`gpt-4o`, `gpt-4o-mini`).
   - Healthcheck endpoints (`/health`, `/health/ready`, `/api/models`) query Ollama's active port. If Ollama is offline, the UI accurately shows it as disconnected and switches to available cloud or simulated evaluation engine without crashing.
