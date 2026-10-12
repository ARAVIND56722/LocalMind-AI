import logging
from typing import List, Dict, Any, Optional
from app.services.retrieval.service import retrieval_service
from app.services.providers.gateway import provider_gateway
from app.services.skills.ship30 import ship30_skill
from app.services.artifacts.compiler import artifact_compiler
from app.schemas.schemas import SourceCitation, ArtifactBase

logger = logging.getLogger(__name__)

QA_SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an internal AI partner for product managers, founders, and growth leaders.
Your knowledge base is grounded strictly in the transcripts of Lenny's Podcast and Lenny's Newsletter.

CRITICAL INSTRUCTIONS:
1. Answer ONLY using the provided transcript evidence.
2. If the retrieved passages do NOT contain enough information to answer the question, you MUST explicitly acknowledge this:
   "Based on the available transcripts in Lenny's library, there is insufficient evidence to answer this question."
3. Attribute your points to specific guests and episodes. Cite timestamps where available (e.g. "[Elena Verna, 00:00:14]").
4. Never hallucinate, extrapolate beyond the text, or fabricate podcast episodes.
5. Format your response cleanly using markdown with bold headings and concise bullet points.
"""

ARTIFACT_SYSTEM_PROMPT = """You are an expert product designer and technical document architect.
When asked to produce a document, PRD, checklist, or UI layout:
1. Output complete, working code in either a ```markdown ... ``` or ```html ... ``` code block.
2. For HTML artifacts, write self-contained modern HTML with inline CSS. Use modern fonts, responsive cards, clean typography, and accessible layouts.
3. Ground any product management frameworks or metrics directly in the provided Lenny transcript context.
"""

class PiAgentRouter:
    """
    Implements the Pi Coding Agent philosophy:
    Lightweight, model-agnostic, deterministic intent evaluation and tool orchestration.
    """

    def route_intent(self, message: str, explicit_workflow: str = "auto") -> str:
        """
        Determines the workflow: 'ship30', 'artifact', or 'qa'.
        """
        if explicit_workflow in ["ship30", "artifact", "qa"]:
            return explicit_workflow

        msg_lower = message.lower()
        if any(w in msg_lower for w in ["ship 30", "ship30", "atomic essay", "1250 word", "write an essay"]):
            return "ship30"
        elif any(w in msg_lower for w in ["generate artifact", "create html", "create a prd", "create markdown", "build an artifact", "html/css"]):
            return "artifact"
        else:
            return "qa"

    async def execute(
        self,
        session_id: str,
        message: str,
        history: List[Dict[str, str]],
        workflow: str = "auto",
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> tuple[str, List[SourceCitation], Optional[Dict[str, Any]], Dict[str, Any]]:
        
        selected_workflow = self.route_intent(message, workflow)
        logger.info(f"Session {session_id}: Routing to workflow '{selected_workflow}'")

        # 1. Ship 30 for 30 Skill Workflow
        if selected_workflow == "ship30":
            essay, citations, meta = await ship30_skill.generate_essay(
                topic=message,
                provider_name=provider_name,
                model_name=model_name
            )
            artifact_dict = {
                "title": f"Ship 30 Essay: {message[:40]}...",
                "artifact_type": "markdown",
                "content": essay,
                "metadata": meta
            }
            return essay, citations, artifact_dict, meta

        # 2. Retrieve transcript evidence for QA or Artifact
        citations = retrieval_service.search(message, top_k=5)
        evidence_text = ""
        if citations:
            evidence_lines = []
            for c in citations:
                evidence_lines.append(
                    f"--- Source: {c.title} (Guest: {c.guest or 'N/A'}, Speaker: {c.speaker or 'N/A'}, Time: {c.timestamp or 'N/A'}) ---\n"
                    f"{c.quote}"
                )
            evidence_text = "\n\n".join(evidence_lines)
        else:
            evidence_text = "No direct passages found in Lenny's transcript library."

        # 3. Artifact Workflow
        if selected_workflow == "artifact":
            system_prompt = ARTIFACT_SYSTEM_PROMPT
            user_msg = (
                f"REQUEST: {message}\n\n"
                f"RELEVANT EVIDENCE FROM TRANSCRIPTS:\n{evidence_text}\n\n"
                f"Produce the complete artifact enclosed in ```html or ```markdown fences."
            )
        else:
            # Standard Grounded QA Workflow
            system_prompt = QA_SYSTEM_PROMPT
            user_msg = (
                f"QUESTION: {message}\n\n"
                f"RETRIEVED TRANSCRIPT EVIDENCE:\n{evidence_text}\n\n"
                f"Answer the question using ONLY the evidence above. If insufficient evidence exists, state so clearly."
            )

        # Assemble message list with prior conversation turns for follow-ups
        llm_messages = []
        for h in history[-6:]:  # preserve recent turns for multi-turn conversational context
            llm_messages.append({"role": h["role"], "content": h["content"]})
        llm_messages.append({"role": "user", "content": user_msg})

        # Generate response using selected provider
        active_provider, provider_impl = await provider_gateway.get_provider(provider_name)
        response_text = await provider_impl.generate(
            messages=llm_messages,
            system_prompt=system_prompt,
            model=model_name
        )

        # Check if an artifact was generated in the response
        extracted_artifact = artifact_compiler.extract_artifact_from_text(response_text)
        
        meta = {
            "workflow": selected_workflow,
            "provider": active_provider,
            "citations_found": len(citations),
            "evidence_grounded": bool(citations)
        }

        return response_text, citations, extracted_artifact, meta

pi_agent = PiAgentRouter()
