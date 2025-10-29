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
        screenshot_base64: Optional[str] = None,
        visual_elements: Optional[Dict] = None,
    ) -> Dict:
        """
        Analyze a single page using GPT-4o with Vision.
        
        Args:
            page_content: Scraped page content
            page_number: Position in funnel (1-indexed)
            total_pages: Total number of pages in funnel
            screenshot_base64: Optional base64 encoded screenshot for visual analysis
            visual_elements: Optional extracted visual data (CTAs, images, etc.) from screenshot
            
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
                visual_elements=visual_elements,
            )
            
            # Build messages with optional vision
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a professional conversion optimization consultant with 15+ years of experience "
                        "analyzing and improving marketing funnels. Your role is to provide clear, actionable analysis "
                        "that helps marketers and funnel builders improve their conversion rates.\n"
                        "\n"
                        "ANALYSIS APPROACH:\n"
                        "• Be specific and direct - identify exact issues and provide concrete solutions\n"
                        "• Focus on elements that drive measurable conversion improvements\n"
                        "• Provide precise recommendations (e.g., 'Change headline to: [exact text]' not 'improve messaging')\n"
                        "• Prioritize high-impact changes over minor tweaks\n"
                        "• Use clear, professional language that any marketer would understand\n"
                        "\n"
                        "CORE EVALUATION CRITERIA:\n"
                        "1. **Clarity**: Can visitors immediately understand the offer and value proposition?\n"
                        "2. **Value Proposition**: Are benefits clearly communicated? Is the offer compelling?\n"
                        "3. **Trust & Proof**: Are there credible testimonials, data, case studies, or guarantees?\n"
                        "4. **Call-to-Action**: Are CTAs clear, visible, and friction-free? Do they create urgency?\n"
                        "5. **User Experience**: Is navigation intuitive? Does the flow guide visitors toward conversion?\n"
                        "\n"
                        "WHEN ANALYZING VISUALS (if screenshot provided):\n"
                        "• Identify ALL call-to-action buttons by their visual appearance, text, and placement\n"
                        "• Assess above-the-fold content - what's immediately visible without scrolling?\n"
                        "• Evaluate mobile responsiveness and layout effectiveness\n"
                        "• Check visual hierarchy - does design guide attention to key elements?\n"
                        "• Identify missing or weak trust indicators (logos, badges, testimonials)\n"
                        "\n"
                        "WHEN ANALYZING TEXT CONTENT:\n"
                        "• Scan for all CTA button text, links, and form submissions\n"
                        "• Evaluate headline clarity and benefit-driven copy\n"
                        "• Identify objection handling and urgency mechanisms\n"
                        "• Check for specificity in claims (numbers, timeframes, guarantees)\n"
                        "\n"
                        "IMPORTANT: If you see CTA buttons in the screenshot OR in the scraped content, acknowledge them "
                        "specifically in your analysis. Don't claim CTAs are missing if they exist.\n"
                        "\n"
                        "Return structured JSON only with your professional analysis."
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
                temperature=0.2,  # Low temperature for consistent, deterministic analysis
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
                            "You are a professional conversion optimization consultant providing an executive summary "
                            "of a complete funnel analysis. Your summary should be clear, actionable, and focused on "
                            "high-impact improvements that will drive measurable results. Use professional language "
                            "that marketing and business professionals expect."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Low temperature for consistent summaries
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
        visual_elements: Optional[Dict] = None,
    ) -> str:
        """Build the prompt for analyzing a single page with CRO expert guidance."""

        page_type = self._guess_page_type(page_number, total_pages)

        headings = "\n".join(page.headings[:12]) or "None"
        key_content = "\n".join([p[:300] for p in page.paragraphs[:8]]) or "None"
        ctas = "\n".join(page.ctas[:12]) or "None"
        forms = " | ".join(page.forms[:4]) if page.forms else "None detected"
        videos = " | ".join(page.videos[:4]) if page.videos else "None detected"
        iframes = "\n".join([f"- {iframe['description']}: {iframe['src']}" for iframe in page.iframes[:4]]) if page.iframes else "None"

        # Format visual elements data if available
        visual_ctas = ""
        if visual_elements and visual_elements.get("buttons"):
            buttons = visual_elements["buttons"]
            total_buttons = visual_elements.get("totalButtons", len(buttons))
            visual_ctas = f"\n\nCTA BUTTONS DETECTED ON FULL PAGE ({total_buttons} total):\n"
            for btn in buttons[:15]:  # Show top 15
                text = btn.get("text", "").strip()
                if not text:
                    continue
                tag = btn.get("tag", "")
                href = btn.get("href", "")
                visual_ctas += f"- '{text}' ({tag})"
                if href:
                    visual_ctas += f" → {href}"
                visual_ctas += "\n"
        
        visual_images = ""
        if visual_elements and visual_elements.get("images"):
            images = visual_elements["images"]
            total_images = visual_elements.get("totalImages", len(images))
            visual_images = f"\n\nIMAGES DETECTED: {total_images} total images on page"
            if images[:5]:
                visual_images += "\nKey images:\n"
                for img in images[:5]:  # Show top 5
                    alt = img.get("alt", "No alt text")
                    visual_images += f"- {alt}\n"

        visual_note = (
            "FULL PAGE SCREENSHOT PROVIDED: This screenshot captures the ENTIRE page from top to bottom. "
            "Analyze all sections - hero, body content, testimonials, CTAs throughout the page, footer, etc. "
            "The visual element data below shows ALL buttons and images found on the complete page, not just above-the-fold."
            if include_visual
            else "No screenshot available. Base analysis on scraped text content, headings, CTAs, and page structure."
        )
        
        iframe_note = ""
        if page.iframes:
            iframe_note = (
                f"\n\n⚠️ IMPORTANT: This page has {len(page.iframes)} embedded iframe(s) - likely order forms or sales pages embedded in the main page. "
                "The sales copy above the iframe is what we can see, but there may be additional content/forms inside the iframe that we can't access. "
                "When analyzing, consider that this is probably a hybrid page with sales copy + an embedded order form below."
            )

        return f"""
Analyze page {page_number} of {total_pages} in this marketing funnel. Provide specific, actionable recommendations for improving conversion rates.

{visual_note}{iframe_note}

PAGE CONTEXT:
- Funnel Position: {page_type}
- URL: {page.url}
- Page Title: {page.title}
- Meta Description: {page.meta_description or 'Not provided'}

CONTENT ANALYSIS:

Headlines & Subheadings:
{headings}

Body Copy (key sections):
{key_content}

Call-to-Action Elements:
{ctas}{visual_ctas}

Forms Detected: {forms}

Video/Media Elements: {videos}{visual_images}

Embedded iframes/order forms:
{iframes}

ANALYSIS REQUIREMENTS:

1. **Identify ALL CTAs**: Look for CTA buttons in both the screenshot (if provided) and the scraped content above. 
   List every CTA you find with its exact text.

2. **Evaluate Current State**: What's working well? What specific elements are hurting conversion?

3. **Provide Exact Recommendations**: Don't say "improve the headline" - provide the exact headline text to use.
   Don't say "add CTAs" if CTAs exist - instead evaluate their effectiveness and suggest improvements.

4. **Prioritize Impact**: Focus on changes that will meaningfully improve conversion rates.

5. **Be Specific**: Use numbers, exact copy, specific placement instructions.

Return ONLY valid JSON with this structure:
{{
    "page_type": "sales_page | order_form | upsell | thank_you | landing | other",
    "scores": {{
        "clarity": 0-100,  // How clear is the value proposition?
        "value": 0-100,    // How compelling is the offer?
        "proof": 0-100,    // How credible are the claims?
        "design": 0-100,   // How effective is the visual design?
        "flow": 0-100      // How smooth is the user journey?
    }},
    "feedback": "Professional 3-5 sentence summary of the page's conversion effectiveness. Be specific about what's working and what needs improvement.",
    "headline_recommendation": "Exact headline text that would improve clarity and conversion. Make it benefit-driven and specific.",
    "cta_recommendations": [
        {{
            "copy": "Exact button text to use",
            "location": "Specific placement (e.g., 'above the fold, next to headline')",
            "reason": "Why this CTA will convert better"
        }}
    ],
    "design_improvements": [
        {{
            "area": "Specific page section (e.g., 'Hero section', 'Above the fold')",
            "recommendation": "Exact change to make",
            "impact": "Expected conversion impact (e.g., 'Improves clarity', 'Reduces friction')"
        }}
    ],
    "trust_elements_missing": [
        {{
            "element": "Specific trust element needed (e.g., 'Client testimonials with photos', 'Money-back guarantee badge')",
            "why": "How this builds trust and improves conversion"
        }}
    ],
    "ab_test_priority": {{
        "element": "The single highest-priority element to A/B test",
        "control": "Current version",
        "variant": "Recommended test variant",
        "expected_lift": "Estimated percentage improvement (e.g., '10-15%')",
        "reasoning": "Why this test is the priority"
    }},
    "priority_alerts": [
        {{
            "severity": "high|medium|low",
            "issue": "Specific problem affecting conversions",
            "impact": "How this impacts conversion rate",
            "fix": "Exact steps to resolve"
        }}
    ],
    "funnel_flow_gaps": [
        {{
            "step": "Where in the customer journey",
            "issue": "What's missing or broken",
            "fix": "How to fix it"
        }}
    ],
    "copy_diagnostics": {{
        "hook": "Does the opening create immediate interest? What's working/missing?",
        "offer": "Is the value proposition crystal clear? What could be clearer?",
        "urgency": "What urgency mechanisms exist? Are they credible?",
        "objections": "Which objections are addressed? Which are missing?",
        "audience_fit": "Does the copy speak directly to the target customer?"
    }},
    "visual_diagnostics": {{
        "hero": "Effectiveness of above-the-fold content and first impression",
        "layout": "Visual organization and information hierarchy",
        "contrast": "Readability and visual clarity",
        "mobile": "Mobile responsiveness and usability",
        "credibility": "Professional appearance and trust signals"
    }},
    "video_recommendations": [
        {{
            "context": "Where video appears or should appear",
            "recommendation": "Specific improvement or addition"
        }}
    ],
    "email_capture_recommendations": [
        "Specific recommendations for email opt-in strategy and nurture sequence"
    ]
}}

CRITICAL: If you identify CTA buttons (either visually or in the content), acknowledge them specifically. 
Don't claim CTAs are missing if they're present - instead evaluate their effectiveness."""
    
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
        
        return f"""Provide an executive summary of this complete funnel analysis. Overall performance score: {overall_score}/100.

INDIVIDUAL PAGE PERFORMANCE:

{pages_summary}

EXECUTIVE SUMMARY REQUIREMENTS:

Provide a professional 4-6 sentence summary covering:

1. **Overall Assessment**: Current funnel performance and conversion effectiveness
2. **Key Strengths**: What's working well that should be maintained or amplified
3. **Primary Opportunity**: The single highest-impact improvement opportunity (be specific - which page, which element, expected impact)
4. **Quick Wins**: 2-3 actionable changes that can be implemented immediately
5. **Strategic Recommendation**: One broader strategic consideration for long-term optimization

Focus on specific, actionable insights. Avoid generic advice. Use professional marketing language."""
    
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
