# Product Requirements Document (PRD)
## The Lenny Growth Assistant
**Author:** Forward Deployed Engineering Lead  
**Target Organization:** Oogway Labs  
**Status:** Approved for Implementation  
**Version:** 1.0.0  

---

### 1. Executive Summary & Problem Definition
Product Managers (PMs), Founders, and Growth leaders spend countless hours trying to extract tactical, operational frameworks from top-tier practitioners. *Lenny’s Podcast* and *Lenny’s Newsletter* comprise one of the tech industry’s richest repositories of verified growth playbooks, retention benchmarks, product strategy teardowns, and leadership wisdom.

However, existing knowledge access suffers from critical flaws:
1. **Unstructured Search Friction:** Finding what Shreyas Doshi said about "Good PM vs. Great PM" or what Elena Verna advised on B2B product-led sales requires scrubbing through 2-hour podcasts or scrolling 40-page transcripts.
2. **Generic LLM Hallucinations:** Vanilla ChatGPT or Claude models hallucinate metrics, falsely attribute quotes to Lenny or guests, and generate generic MBA platitudes rather than Lenny's guests' real practitioner insights.
3. **Synthesis & Actionability Gap:** Teams don't just want Q&A; they need immediate editorial leverage (e.g. turning insights into high-impact Ship 30 for 30 essays) or structured artifacts (e.g. PRD templates, growth frameworks, roadmaps) rendered directly in their workspace.

**The Lenny Growth Assistant** is an internal editorial research studio and AI application that bridges this gap: providing strict grounded answers with direct speaker and timestamp citations, turning insights into 1,250-word Ship 30 for 30 essays, and generating renderable Markdown/HTML artifacts in a secure sandbox.

---

### 2. Primary Users & Personas
- **Growth Leads & VP Product:** Need benchmark figures, retention loops, and pricing/packaging examples cited directly from heads of growth (e.g. Brian Balfour, Elena Verna, Casey Winters).
- **Product Managers & Founders:** Need atomic, battle-tested essay drafts (Ship 30 format) and tactical documents (PRDs, user interview guides, KPI trees) generated from practitioner consensus.
- **Researchers & Content Creators:** Need traceable podcast citations (Episode title, Guest, timestamps, source URLs) to verify claims before publishing.

---

### 3. Core Workflows & User Journeys

#### Workflow 1: Grounded Growth & Product Q&A
- **User Action:** Types a specific PM/Growth question (e.g., *"How should early-stage startups identify true Product-Market Fit versus false traction according to Lenny's guests?"*).
- **System Action:** Retrieves relevant passages with hybrid semantic/lexical ranking, constructs an evidence context, and queries the selected model (local Ollama or cloud provider).
- **Output:** A structured, insightful response citing exact episodes and speakers. If evidence is lacking, it explicitly states: *"Based on the available transcripts, there is insufficient evidence to answer this definitively."*

#### Workflow 2: Ship 30 for 30 Essay Generation
- **User Action:** Invokes essay generation via prompt or UI mode (e.g., *"Write a Ship 30 essay on Elena Verna's B2B PLG flywheel"*).
- **System Action:** Invokes the dedicated `ship30` writing engine applying digital writing principles (compelling hook, clear progression, 1,250 words target, skimmable bolding/bullets, grounded takeaways).
- **Output:** An essay structured according to atomic digital writing frameworks, backed by a dedicated source-attribution table.

#### Workflow 3: Artifact Generation & Sandboxed Studio Viewer
- **User Action:** Requests a document or interactive artifact (e.g., *"Create a high-converting pricing page breakdown HTML artifact"* or *"Generate a comprehensive Feature Launch Checklist PRD in Markdown"*).
- **System Action:** Generates structured Markdown or full self-contained HTML/CSS.
- **Output:** Opens the side-by-side **Editorial Workspace**. Markdown renders cleanly; HTML renders inside a sandboxed `iframe` with strict CSP, null-origin isolation, and script blocking.

---

### 4. Technical Stack & Mandatory Constraints
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide React icons.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2 schemas, SQLAlchemy / asyncpg / SQLite fallback.
- **Persistence:** PostgreSQL (Docker Compose) with automatic SQLite dual-dialect compatibility for zero-friction local developer setup.
- **Knowledge Engine:** High-performance BM25 + embedding hybrid retrieval with exact speaker/episode metadata preservation.
- **Models:**
  - Local: Ollama (`llama3.2`, `mistral`, `qwen2.5`) with health verification.
  - Cloud: Anthropic Claude (`claude-3-5-sonnet`, `claude-3-haiku`) & OpenAI (`gpt-4o`, `gpt-4o-mini`).
- **Agent Architecture:** Modular agent routing engine following the Pi Coding Agent philosophy (minimalist, model-agnostic, explicit state-driven tool dispatch).

---

### 5. Success Metrics
- **Grounding Accuracy:** 100% of factual claims in Q&A must cite indexed transcript chunks; 0% fabricated URLs or non-existent guest quotes.
- **Graceful Failure Rate:** 100% of out-of-domain queries trigger the standardized "insufficient evidence" disclaimer rather than hallucinatory drift.
- **Essay Structure Adherence:** Generated Ship 30 essays hit between 1,000–1,500 words with required hook, subheadings, bulleted takeaways, and citation footer.
- **Viewer Isolation:** 0 security leakage (XSS, parent DOM access, cookie theft) in the artifact preview iframe.
- **Cold-Start Time:** Under 10 seconds for backend initialization and retrieval readiness.

---

### 6. Risks, Trade-offs & Mitigations
| Risk | Severity | Mitigation |
| :--- | :--- | :--- |
| **Hallucinated Citations** | High | Strict RAG prompt constraints; post-generation validation checks citations against indexed document IDs. |
| **Ollama Local Unavailability** | Medium | Provider abstraction detects Ollama status; displays real connectivity state; gracefully falls back to configured cloud or mock test provider with explicit warning. |
| **Unsafe HTML Execution** | High | Preview rendered in `iframe sandbox="allow-same-origin"` with CSP `default-src 'none'; style-src 'unsafe-inline'; img-src data: https:;`. Arbitrary JavaScript execution is disabled by default. |
| **Docker Engine Not Running** | Low | Dual-engine database connection: uses PostgreSQL when `DATABASE_URL` is set, with automatic seamless SQLite fallback for zero-install evaluation. |
