"""
Funnel analyzer service with mock data.
This will be replaced with real OpenAI + scraping logic.
"""

from datetime import datetime
from typing import List
import random


async def analyze_funnel_mock(urls: List[str]) -> dict:
    """
    Mock funnel analysis that returns realistic dummy data.
    
    TODO: Replace with:
    1. Scrape each URL using Playwright or requests+BeautifulSoup
    2. Extract text content and take screenshots
    3. Send to OpenAI GPT-4o for analysis
    4. Parse structured response into scores
    5. Store in database
    """
    
    # Simulate processing time
    import asyncio
    await asyncio.sleep(1)
    
    # Generate mock scores
    base_score = random.randint(70, 95)
    scores = {
        "clarity": base_score + random.randint(-10, 10),
        "value": base_score + random.randint(-10, 10),
        "proof": base_score + random.randint(-10, 10),
        "design": base_score + random.randint(-10, 10),
        "flow": base_score + random.randint(-10, 10),
    }
    
    # Ensure scores are within 0-100
    scores = {k: max(0, min(100, v)) for k, v in scores.items()}
    overall_score = sum(scores.values()) // len(scores)
    
    # Generate mock page analyses
    page_types = ["sales_page", "order_form", "upsell", "downsell", "thank_you"]
    pages = []
    
    for idx, url in enumerate(urls):
        page_type = page_types[idx] if idx < len(page_types) else "additional_page"
        
        page_scores = {
            "clarity": scores["clarity"] + random.randint(-5, 5),
            "value": scores["value"] + random.randint(-5, 5),
            "proof": scores["proof"] + random.randint(-5, 5),
            "design": scores["design"] + random.randint(-5, 5),
            "flow": scores["flow"] + random.randint(-5, 5),
        }
        page_scores = {k: max(0, min(100, v)) for k, v in page_scores.items()}
        
        pages.append({
            "url": url,
            "page_type": page_type,
            "title": f"Example Page {idx + 1}",
            "scores": page_scores,
            "feedback": f"This {page_type.replace('_', ' ')} demonstrates strong visual hierarchy and clear messaging. The headline effectively communicates the core value proposition. Consider enhancing social proof elements and streamlining the call-to-action placement.",
            "screenshot_url": f"https://via.placeholder.com/1200x800/4F46E5/FFFFFF?text=Page+{idx+1}"
        })
    
    return {
        "analysis_id": random.randint(1000, 9999),
        "overall_score": overall_score,
        "scores": scores,
        "summary": f"Your funnel demonstrates strong performance with an overall score of {overall_score}/100. The value proposition is clear and compelling, with excellent visual design throughout. Key strengths include consistent branding, logical flow between pages, and effective use of urgency triggers. Areas for improvement: enhance social proof elements on the sales page, simplify the checkout process, and add more specific benefits to the upsell offer. The funnel maintains good momentum and reduces friction at critical decision points.",
        "pages": pages,
        "created_at": datetime.utcnow().isoformat(),
        "analysis_duration_seconds": random.randint(15, 45)
    }
