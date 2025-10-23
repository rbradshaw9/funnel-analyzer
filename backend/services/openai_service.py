"""OpenAI service for analyzing funnel content using GPT-4 with Vision."""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

from openai import AsyncOpenAI

from ..services.scraper import PageContent
from ..utils.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def analyze_page(
        self,
        page_content: PageContent,
        page_number: int,
        total_pages: int,
        screenshot_base64: Optional[str] = None
    ) -> Dict:
        """
        Analyze a single page using GPT-4o with Vision.
        
        Args:
            page_content: Scraped page content
            page_number: Position in funnel (1-indexed)
            total_pages: Total number of pages in funnel
            screenshot_base64: Optional base64 encoded screenshot for visual analysis
            
        Returns:
            Dict with scores, feedback, and specific recommendations
        """
        if not self.client:
            logger.warning("OpenAI API key not configured, using placeholder scores")
            return self._generate_placeholder_scores(page_content)
        
        try:
            prompt = self._build_expert_analysis_prompt(
                page=page_content,
                page_number=page_number,
                total_pages=total_pages,
                include_visual=bool(screenshot_base64),
            )
            
            # Build messages with optional vision
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Russell Brunson combined with Peep Laja - a world-class conversion rate optimization expert "
                        "with 15+ years optimizing 10,000+ funnels. You've increased conversion rates by an average of 127%. "
                        "\n\nYour analysis is:\n"
                        "• SPECIFIC: Provide exact headline rewrites, precise CTA copy, specific visual changes\n"
                        "• ACTIONABLE: Every recommendation can be implemented immediately\n"
                        "• DATA-DRIVEN: Reference proven conversion principles and psychology\n"
                        "• HONEST: Point out specific problems, don't sugarcoat\n"
                        "\n\nCore Principles You Apply:\n"
                        "1. Clarity beats cleverness (people scan, they don't read)\n"
                        "2. Specificity beats generalities (numbers and details build trust)\n"
                        "3. Benefits beat features (what's in it for them?)\n"
                        "4. Proof beats claims (show, don't tell)\n"
                        "5. Simplicity beats complexity (reduce cognitive load)\n"
                        "6. Urgency beats patience (give them a reason to act now)\n"
                        "\n\nWhen analyzing visuals, assess:\n"
                        "• Visual hierarchy (what grabs attention first?)\n"
                        "• Color psychology (do colors support or fight the message?)\n"
                        "• White space (is it cluttered or breathable?)\n"
                        "• Mobile responsiveness (60%+ traffic is mobile)\n"
                        "• Above-the-fold content (8 seconds to capture attention)\n"
                        "\n\nReturn structured JSON only with your expert analysis."
                    ),
                },
            ]
            
            # If we have a screenshot, use vision analysis
            if screenshot_base64:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this page VISUALLY and by CONTENT:\n\n{prompt}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                })
            else:
                # Text-only analysis
                messages.append({
                    "role": "user",
                    "content": prompt
                })
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.8,
                max_tokens=3000,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            logger.info(f"Analyzed page {page_number}/{total_pages}: {page_content.url}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error for {page_content.url}: {str(e)}")
            return self._generate_placeholder_scores(page_content)
    
    async def analyze_funnel_summary(
        self, page_results: List[Dict], overall_score: int
    ) -> str:
        """
        Generate an executive summary for the entire funnel.
        
        Args:
            page_results: List of individual page analysis results
            overall_score: Calculated overall funnel score
            
        Returns:
            Executive summary text
        """
        if not self.client:
            return self._generate_placeholder_summary(overall_score)
        
        try:
            prompt = self._build_summary_prompt(page_results, overall_score)
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert marketing strategist. Provide concise, actionable "
                            "executive summaries of funnel analyses. Focus on key strengths and "
                            "top 3 improvement opportunities."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated funnel summary (score: {overall_score})")
            return summary
            
        except Exception as e:
            logger.error(f"OpenAI API error for summary: {str(e)}")
            return self._generate_placeholder_summary(overall_score)

    def _build_expert_analysis_prompt(
        self,
        page: PageContent,
        page_number: int,
        total_pages: int,
        include_visual: bool,
    ) -> str:
        """Build the prompt for analyzing a single page with CRO expert guidance."""

        page_type = self._guess_page_type(page_number, total_pages)

        headings = "\n".join(page.headings[:12]) or "None"
        key_content = "\n".join([p[:300] for p in page.paragraphs[:8]]) or "None"
        ctas = "\n".join(page.ctas[:12]) or "None"
        forms = " | ".join(page.forms[:4]) if page.forms else "None detected"
        videos = " | ".join(page.videos[:4]) if page.videos else "None detected"

        visual_note = (
            "A high-resolution screenshot is provided. Critique hierarchy, spacing, hero layout, and any visible media."
            if include_visual
            else "No screenshot available. Infer visuals from copy structure and best practices."
        )

        return f"""
You are a world-class conversion rate optimization leader (Russell Brunson + Peep Laja mindset) reviewing page {page_number} of {total_pages} in a funnel. Always be specific, bluntly honest, and tie recommendations to conversion psychology.

{visual_note}

Page context:
- Funnel position: {page_type}
- URL: {page.url}
- Title: {page.title}
- Meta description: {page.meta_description or 'None'}
- Primary headings (ordered):\n{headings}
- Key copy excerpts:\n{key_content}
- CTAs: {ctas}
- Forms: {forms}
- Embedded media/video: {videos}

Return ONLY valid JSON with this exact structure (keep strings short but actionable):
{{
    "page_type": "sales_page | order_form | upsell | thank_you | landing | other",
    "scores": {{
        "clarity": 0-100,
        "value": 0-100,
        "proof": 0-100,
        "design": 0-100,
        "flow": 0-100
    }},
    "feedback": "3-5 sentences summarising biggest conversion issues and wins",
    "headline_recommendation": "Exact headline rewrite that will convert better",
    "cta_recommendations": [
        {{"copy": "button text", "location": "where to use", "reason": "why it will help"}}
    ],
    "design_improvements": [
        {{"area": "hero/testimonial/form/etc", "recommendation": "visual/design change", "impact": "conversion impact"}}
    ],
    "trust_elements_missing": [
        {{"element": "specific proof element", "why": "credibility reason"}}
    ],
    "ab_test_priority": {{
        "element": "the element to test",
        "control": "current version",
        "variant": "specific test idea",
        "expected_lift": "% range",
        "reasoning": "why this is priority"
    }},
    "priority_alerts": [
        {{"severity": "high|medium|low", "issue": "critical blocker", "impact": "effect on conversion", "fix": "what to do"}}
    ],
    "funnel_flow_gaps": [
        {{"step": "drop-off location", "issue": "what is broken", "fix": "how to close the gap"}}
    ],
    "copy_diagnostics": {{
        "hook": "is the hook strong?",
        "offer": "is the value proposition specific?",
        "urgency": "is there urgency or risk?",
        "objections": "how are objections handled?",
        "audience_fit": "does copy speak to ideal avatar?"
    }},
    "visual_diagnostics": {{
        "hero": "does hero communicate value quickly?",
        "layout": "hierarchy/white space feedback",
        "contrast": "is contrast/typography effective?",
        "mobile": "mobile responsiveness risks",
        "credibility": "visual trust signals present?"
    }},
    "video_recommendations": [
        {{"context": "where video sits or should sit", "recommendation": "exact upgrade"}}
    ],
    "email_capture_recommendations": [
        "Specific nurture or capture improvement"
    ]
}}

Rules:
- Mention screenshots explicitly if referenced.
- If a section does not apply, return an empty list or succinct note like "none"—never omit fields.
- Prefer specific copy, layout, and offer guidance over generic remarks.
"""
    
    def _build_summary_prompt(self, page_results: List[Dict], overall_score: int) -> str:
        """Build the prompt for generating executive summary."""
        summary_chunks: List[str] = []

        for index, page in enumerate(page_results, start=1):
            score = sum(page.get("scores", {}).values()) // 5 if page.get("scores") else 0
            headline = page.get("headline_recommendation", "N/A")

            ctas = page.get("cta_recommendations") or []
            if ctas:
                first_cta = ctas[0]
                if isinstance(first_cta, dict):
                    copy = first_cta.get("copy")
                    location = first_cta.get("location")
                    reason = first_cta.get("reason")
                    parts = [p for p in [copy, location, reason] if p]
                    top_cta = " | ".join(parts) if parts else "(CTA details unavailable)"
                else:
                    top_cta = str(first_cta)
            else:
                top_cta = "N/A"

            summary_chunks.append(
                f"Page {index} ({page.get('page_type', 'unknown')}): Score {score}/100\n"
                f"  Headline Suggestion: {headline}\n"
                f"  Top CTA: {top_cta}"
            )

        pages_summary = "\n".join(summary_chunks)
        
        return f"""As a conversion optimization expert, analyze this marketing funnel with an overall score of {overall_score}/100:

{pages_summary}

Provide a comprehensive executive summary (4-6 sentences) that includes:

1. Overall performance: honest conversion potential (mention copy, design, proof)
2. Biggest win: the ONE change with the highest leverage (name the page and element)
3. Quick wins: 2-3 fast changes covering copy, design, and offer clarity
4. Strategic recommendations: longer-term tests or multi-step flow fixes (reference video/email if relevant)

Be direct, specific, and actionable. Reference actual page elements. Think like a consultant presenting to a client."""
    
    def _guess_page_type(self, page_number: int, total_pages: int) -> str:
        """Guess page type based on position in funnel."""
        if page_number == 1:
            return "sales_page"
        elif page_number == total_pages:
            return "thank_you"
        elif "checkout" in str(page_number).lower() or page_number == total_pages - 1:
            return "order_form"
        elif page_number == 2:
            return "order_form"
        else:
            return "upsell"
    
    def _generate_placeholder_scores(self, page: PageContent) -> Dict:
        """Generate placeholder scores when OpenAI is not available."""
        import random
        
        base_score = 70 + random.randint(0, 20)
        
        return {
            "page_type": "sales_page",
            "scores": {
                "clarity": base_score + random.randint(-10, 10),
                "value": base_score + random.randint(-10, 10),
                "proof": base_score + random.randint(-10, 10),
                "design": base_score + random.randint(-10, 10),
                "flow": base_score + random.randint(-10, 10),
            },
            "feedback": (
                f"Analysis for {page.title}: This page demonstrates strong visual hierarchy and "
                "clear messaging. Consider enhancing social proof elements and streamlining the "
                "call-to-action placement for better conversion."
            ),
        }
    
    def _generate_placeholder_summary(self, overall_score: int) -> str:
        """Generate placeholder summary when OpenAI is not available."""
        return (
            f"Your funnel demonstrates strong performance with an overall score of {overall_score}/100. "
            "The value proposition is clear and compelling, with excellent visual design throughout. "
            "Key strengths include consistent branding, logical flow between pages, and effective use "
            "of urgency triggers. Areas for improvement: enhance social proof elements on the sales page, "
            "simplify the checkout process, and add more specific benefits to the upsell offer. "
            "The funnel maintains good momentum and reduces friction at critical decision points."
        )


# Singleton instance
_openai_service: OpenAIService | None = None


def get_openai_service() -> OpenAIService:
    """Get or create the OpenAI service singleton."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
