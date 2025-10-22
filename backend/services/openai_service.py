"""OpenAI service for analyzing funnel content using GPT-4."""

from __future__ import annotations

import json
import logging
from typing import Dict, List

from openai import AsyncOpenAI

from ..services.scraper import PageContent
from ..utils.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def analyze_page(self, page_content: PageContent, page_number: int, total_pages: int) -> Dict:
        """
        Analyze a single page using GPT-4.
        
        Args:
            page_content: Scraped page content
            page_number: Position in funnel (1-indexed)
            total_pages: Total number of pages in funnel
            
        Returns:
            Dict with scores and feedback
        """
        if not self.client:
            logger.warning("OpenAI API key not configured, using placeholder scores")
            return self._generate_placeholder_scores(page_content)
        
        try:
            prompt = self._build_page_analysis_prompt(page_content, page_number, total_pages)
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert marketing funnel analyst. Analyze web pages and provide "
                            "actionable feedback on clarity, value proposition, social proof, design, and flow. "
                            "Return structured JSON responses only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
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
    
    def _build_page_analysis_prompt(
        self, page: PageContent, page_number: int, total_pages: int
    ) -> str:
        """Build the prompt for analyzing a single page."""
        page_type = self._guess_page_type(page_number, total_pages)
        
        return f"""Analyze this {page_type} page from a marketing funnel (page {page_number} of {total_pages}).

Page Content:
{page.get_full_text()[:3000]}

Provide a JSON response with:
{{
  "page_type": "{page_type}",
  "scores": {{
    "clarity": 0-100 (message clarity and headline strength),
    "value": 0-100 (value proposition strength),
    "proof": 0-100 (social proof, testimonials, trust signals),
    "design": 0-100 (visual design and layout quality),
    "flow": 0-100 (user journey and CTA effectiveness)
  }},
  "feedback": "2-3 sentence actionable feedback on strengths and improvements"
}}"""
    
    def _build_summary_prompt(self, page_results: List[Dict], overall_score: int) -> str:
        """Build the prompt for generating executive summary."""
        pages_summary = "\n".join([
            f"Page {i+1} ({r.get('page_type', 'unknown')}): Score {sum(r['scores'].values())//5}/100"
            for i, r in enumerate(page_results)
        ])
        
        return f"""Analyze this marketing funnel with an overall score of {overall_score}/100:

{pages_summary}

Provide a 3-4 sentence executive summary covering:
1. Overall performance assessment
2. Key strengths
3. Top 2-3 specific improvements needed

Be direct and actionable. Focus on conversion optimization."""
    
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
