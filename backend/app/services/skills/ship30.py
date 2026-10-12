import logging
from typing import List, Dict, Any, Optional
from app.services.retrieval.service import retrieval_service
from app.services.providers.gateway import provider_gateway
from app.schemas.schemas import SourceCitation

logger = logging.getLogger(__name__)

SHIP30_SYSTEM_PROMPT = """You are a master digital writer and mentor trained strictly in the Ship 30 for 30 methodology by Dickie Bush and Nicolas Cole.
Your mission is to turn grounded tech, product management, and growth insights from Lenny's Podcast and Newsletter transcripts into a high-impact, publication-grade digital essay.

STRICT WRITING RULES:
1. TARGET LENGTH: Approximately 1,250 words (aim for 1,100 - 1,400 words).
2. THE HEADLINE: Must stop the scroll. Clear over clever. Formulate using proven templates: "How [Subject] Unlocked [Outcome]" or "[Number] Counter-Intuitive Rules for [Topic]".
3. THE HOOK: The first 1-3 sentences must present a paradox or open loop that forces the reader down the slippery slope. No fluffy conversational introductions like "In this article we will explore...".
4. THE PROGRESSION: Use 3-5 distinct, punchy subheadings (### H3) that build an airtight narrative case.
5. SKIMMABLE VISUAL CADENCE:
   - Break walls of text into 1-3 sentence paragraphs.
   - Use **bold text** strategically for emphasis on key takeaways.
   - Use bullet points (- ) and numbered lists for rapid scanning.
6. THE CONCLUSION: Deliver one concrete, tactical 1-page playbook summary or framework that a VP of Product or Founder can implement tomorrow.
7. GROUNDING & ATTRIBUTION:
   - Ground every core insight, metric, and quote in the provided transcript evidence.
   - NEVER fabricate guests, episodes, numbers, or quotes.
   - At the bottom of the essay, include a dedicated "### Source References" section explicitly citing the episode title, guest, and approximate timestamp.
"""

class Ship30Skill:
    def __init__(self):
        pass

    async def generate_essay(
        self,
        topic: str,
        user_instructions: Optional[str] = None,
        target_words: int = 1250,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> tuple[str, List[SourceCitation], Dict[str, Any]]:
        # 1. Retrieve evidence from Lenny transcripts
        citations = retrieval_service.search(topic, top_k=6)
        
        # 2. Build evidence context
        evidence_blocks = []
        for c in citations:
            evidence_blocks.append(
                f"- [Episode: {c.title} | Guest: {c.guest or 'N/A'} | Timestamp: {c.timestamp or 'N/A'}]\n"
                f"  Speaker: {c.speaker}\n"
                f"  Quote: \"{c.quote}\""
            )
        evidence_text = "\n\n".join(evidence_blocks) if evidence_blocks else "No direct transcript matches."

        # 3. Construct user prompt
        prompt = (
            f"TOPIC: {topic}\n\n"
            f"TARGET WORD COUNT: ~{target_words} words\n\n"
            f"ADDITIONAL USER INSTRUCTIONS: {user_instructions or 'Focus on tactical, practitioner-level PM & Growth playbooks.'}\n\n"
            f"GROUNDED TRANSCRIPT EVIDENCE FROM LENNY'S ARCHIVE:\n"
            f"{evidence_text}\n\n"
            f"Write the full Ship 30 for 30 essay following all required digital writing constraints now."
        )

        active_provider, provider_impl = await provider_gateway.get_provider(provider_name)
        essay_content = await provider_impl.generate(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=SHIP30_SYSTEM_PROMPT,
            model=model_name
        )

        meta = {
            "skill": "ship30",
            "provider": active_provider,
            "target_word_count": target_words,
            "actual_word_count": len(essay_content.split()),
            "citations_count": len(citations)
        }

        return essay_content, citations, meta

ship30_skill = Ship30Skill()
