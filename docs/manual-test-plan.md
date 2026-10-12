# Manual Test Plan & Quality Assurance Checklist
## The Lenny Growth Assistant
**Author:** Forward Deployed Engineering Lead  

---

### Test Suite 1: Backend Health & System Connectivity
1. **Health Check (`GET /health`):**
   - Expected: `200 OK` with JSON `{"status": "healthy", "service": "lenny-growth-assistant", "version": "1.0.0"}`.
2. **Readiness Check (`GET /health/ready`):**
   - Expected: `200 OK` with dependency statuses for database (`connected`), retrieval engine (`indexed`), and LLM provider gateway status.
3. **Model Configuration & Status (`GET /api/models`):**
   - Expected: Returns list of supported providers (`ollama`, `anthropic`, `openai`, `mock`) with explicit `available: true/false` flags. Ollama is marked `false` if not running locally, preventing false statuses.

---

### Test Suite 2: Session & Message Persistence
1. **Create Session (`POST /api/sessions`):**
   - Expected: `201 Created` with a new UUID `id`, timestamp, and metadata.
2. **List Sessions (`GET /api/sessions`):**
   - Expected: Returns all persisted sessions sorted by `updated_at DESC`.
3. **Get Session Details (`GET /api/sessions/{session_id}`):**
   - Expected: Returns session object along with chronologically ordered messages.
4. **Delete Session (`DELETE /api/sessions/{session_id}`):**
   - Expected: Deletes the session and cascades message deletion cleanly.

---

### Test Suite 3: Grounded Q&A & Source Attribution
1. **Known Lenny Topic Query:**
   - Query: *"What is Elena Verna's definition of Product-Led Sales and how does it connect with PLG?"*
   - Expected: Answer cites Elena Verna's episode, with verifiable references containing episode title and timestamps.
2. **Out of Domain / Insufficient Evidence Query:**
   - Query: *"What did Lenny's guests say about the best recipe for baking sourdough bread?"*
   - Expected: System explicitly responds that the indexed transcripts contain insufficient evidence.
3. **Multi-turn Session Context:**
   - Turn 1: *"Tell me Shreyas Doshi's view on high-agency PMs."*
   - Turn 2: *"What was his second key point?"*
   - Expected: Turn 2 correctly uses prior session context while retrieving grounded supporting evidence.

---

### Test Suite 4: Ship 30 for 30 Writing Skill
1. **Dedicated Essay Generation (`POST /api/skills/ship30`):**
   - Request: Topic: *"Finding True Product-Market Fit"*, Target word count: 1250.
   - Expected:
     - Hook Stops the scroll.
     - Section headings with clear narrative progression.
     - Bold emphasis on key terms and bulleted actionable takeaways.
     - Word count approximately 1,250 words.
     - Traceable source references section at the bottom.

---

### Test Suite 5: Artifact Generation & Security Isolation
1. **Markdown Artifact Generation:**
   - Expected: Output contains clean Markdown, rendering properly with typography styling in the viewer.
2. **HTML/CSS Artifact Generation:**
   - Expected: Output contains complete HTML document with self-contained CSS.
3. **Security Sandboxing:**
   - Test payload containing `<script>alert(window.origin)</script>` or cookie theft.
   - Expected: Inside the iframe, scripts are blocked by CSP (`script-src 'none'`) and `sandbox="allow-same-origin"`, with zero execution in the parent DOM.
