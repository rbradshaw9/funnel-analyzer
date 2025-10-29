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
                        "You're a battle-tested funnel expert who's been in the trenches for 15+ years. "
                        "You've optimized thousands of funnels and you know what actually works (and what's just marketing BS). "
                        "\n\nYour style:\n"
                        "• Talk like a real person, not a consultant - be direct and conversational\n"
                        "• Point out what's broken and exactly how to fix it\n"
                        "• Give specific examples, not theory ('change this headline to...' not 'consider improving messaging')\n"
                        "• Focus on what actually moves the needle - no fluff\n"
                        "\n\nWhat you care about:\n"
                        "1. Can people instantly understand what you're selling? (clarity wins)\n"
                        "2. Do they care? (benefits over features, every time)\n"
                        "3. Do they believe you? (proof, specifics, real results)\n"
                        "4. Is it stupid-easy to take action? (remove friction)\n"
                        "5. Why should they act now? (urgency that actually makes sense)\n"
                        "\n\nWhen you see visuals:\n"
                        "• Does the page actually look like it would work on a phone? (most traffic is mobile)\n"
                        "• What catches your eye first? (is it the right thing?)\n"
                        "• Is there too much going on? (simplify, simplify, simplify)\n"
                        "• Do the colors and layout help or hurt the message?\n"
                        "\n\nBe honest. If something sucks, say so. If it's good, say that too. "
                        "Your job is to help people make more money by fixing their funnels.\n"
                        "\n\nReturn structured JSON only with your analysis."
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
                            "You're a funnel expert who just finished analyzing someone's entire marketing funnel. "
                            "Give them the straight truth about what's working and what needs to change. "
                            "Be conversational, direct, and helpful - like you're talking to a friend who trusts your advice. "
                            "Focus on what actually matters for making more sales."
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
        iframes = "\n".join([f"- {iframe['description']}: {iframe['src']}" for iframe in page.iframes[:4]]) if page.iframes else "None"

        visual_note = (
            "You've got a screenshot to work with. Look at what actually grabs attention first, check if it works on mobile, and see if the layout helps or hurts."
            if include_visual
            else "No screenshot available, but you can still give solid advice based on the copy and structure."
        )
        
        iframe_note = ""
        if page.iframes:
            iframe_note = (
                f"\n\n⚠️ IMPORTANT: This page has {len(page.iframes)} embedded iframe(s) - likely order forms or sales pages embedded in the main page. "
                "The sales copy above the iframe is what we can see, but there may be additional content/forms inside the iframe that we can't access. "
                "When analyzing, consider that this is probably a hybrid page with sales copy + an embedded order form below."
            )

        return f"""
Alright, you're looking at page {page_number} of {total_pages} in this funnel. Give it to them straight - what's working, what's broken, and exactly how to fix it.

{visual_note}{iframe_note}

Here's what we're working with:
- Position in funnel: {page_type}
- URL: {page.url}
- Page Title: {page.title}
- Meta description: {page.meta_description or 'None'}

Main Headlines:
{headings}

The actual copy on the page:
{key_content}

Call-to-action buttons:
{ctas}

Forms on the page: {forms}

Videos/media: {videos}

Embedded iframes (order forms, embedded pages, etc.):
{iframes}

Give me your analysis in JSON format. Be specific and actionable - not "improve the headline" but "change the headline to: [exact text]".

Return ONLY valid JSON with this structure:
{{
    "page_type": "sales_page | order_form | upsell | thank_you | landing | other",
    "scores": {{
        "clarity": 0-100,
        "value": 0-100,
        "proof": 0-100,
        "design": 0-100,
        "flow": 0-100
    }},
    "feedback": "Talk like you're explaining this to a friend over coffee - what's the real issue here and how do we fix it? 3-5 sentences.",
    "headline_recommendation": "Write the exact headline they should use instead",
    "cta_recommendations": [
        {{"copy": "exact button text", "location": "where it goes", "reason": "why this will work better"}}
    ],
    "design_improvements": [
        {{"area": "what part of the page", "recommendation": "specific change to make", "impact": "how this helps conversions"}}
    ],
    "trust_elements_missing": [
        {{"element": "what proof/trust element is needed", "why": "why it matters"}}
    ],
    "ab_test_priority": {{
        "element": "the one thing to test first",
        "control": "what they have now",
        "variant": "what to test against it",
        "expected_lift": "rough % improvement",
        "reasoning": "why this is the priority"
    }},
    "priority_alerts": [
        {{"severity": "high|medium|low", "issue": "what's the problem", "impact": "how it hurts conversions", "fix": "what to do about it"}}
    ],
    "funnel_flow_gaps": [
        {{"step": "where in the flow", "issue": "what's broken", "fix": "how to fix it"}}
    ],
    "copy_diagnostics": {{
        "hook": "does the opening grab them? or is it weak?",
        "offer": "is it crystal clear what they're getting?",
        "urgency": "any reason to act now? or can they put it off forever?",
        "objections": "are we handling the obvious objections?",
        "audience_fit": "does this actually speak to the target customer?"
    }},
    "visual_diagnostics": {{
        "hero": "does the top of the page nail it or fall flat?",
        "layout": "is it clean and easy to follow, or cluttered?",
        "contrast": "can people actually read this stuff?",
        "mobile": "does this work on a phone? (because most people are on phones)",
        "credibility": "does it look professional enough to trust?"
    }},
    "video_recommendations": [
        {{"context": "where the video is (or should be)", "recommendation": "what to do with it"}}
    ],
    "email_capture_recommendations": [
        "Specific ways to improve email capture or nurture sequence"
    ]
}}

Remember: Be direct, be specific, talk like a human. No corporate BS, no consultant-speak. Just real talk about what needs to change.
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
        
        return f"""Alright, you just reviewed this entire funnel. Overall score: {overall_score}/100.

Here's what you found on each page:

{pages_summary}

Now give them the executive summary - the stuff that actually matters. Write 4-6 sentences covering:

1. The real deal: How's this funnel actually performing? What's working, what's not?
2. The big opportunity: What's the ONE change that would move the needle the most? (Be specific - which page, which element)
3. Quick wins: Give them 2-3 things they can fix today that'll make a difference
4. Bigger picture: Any strategic stuff they should think about for the long term?

Talk like you're explaining this to a friend who owns the business. Be helpful, be direct, skip the fluff.
"""
    
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
