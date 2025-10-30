"""Performance analysis service for measuring page speed and Core Web Vitals."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes page performance using Google PageSpeed Insights API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    async def analyze_performance(self, url: str, strategy: str = "mobile") -> Optional[Dict]:
        """
        Analyze page performance using Google PageSpeed Insights.
        
        Args:
            url: The URL to analyze
            strategy: 'mobile' or 'desktop'
            
        Returns:
            Dict with performance metrics or None if analysis fails
        """
        if not self.api_key:
            logger.warning("Google PageSpeed Insights API key not configured")
            return None
        
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy,
            "category": ["PERFORMANCE", "ACCESSIBILITY", "BEST_PRACTICES", "SEO"],
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return self._extract_metrics(data, url)
                
        except Exception as e:
            logger.error(f"PageSpeed Insights API error for {url}: {str(e)}")
            return None
    
    def _extract_metrics(self, data: Dict, url: str) -> Dict:
        """Extract key performance metrics from PageSpeed Insights response."""
        
        lighthouse_result = data.get("lighthouseResult", {})
        categories = lighthouse_result.get("categories", {})
        audits = lighthouse_result.get("audits", {})
        
        # Core Web Vitals
        core_web_vitals = {}
        
        # Largest Contentful Paint (LCP)
        lcp_audit = audits.get("largest-contentful-paint", {})
        if lcp_audit:
            core_web_vitals["lcp"] = {
                "value": lcp_audit.get("numericValue", 0) / 1000,  # Convert to seconds
                "displayValue": lcp_audit.get("displayValue", ""),
                "score": lcp_audit.get("score", 0),
            }
        
        # First Input Delay (FID) - use Total Blocking Time as proxy
        tbt_audit = audits.get("total-blocking-time", {})
        if tbt_audit:
            core_web_vitals["fid_proxy"] = {
                "value": tbt_audit.get("numericValue", 0),
                "displayValue": tbt_audit.get("displayValue", ""),
                "score": tbt_audit.get("score", 0),
            }
        
        # Cumulative Layout Shift (CLS)
        cls_audit = audits.get("cumulative-layout-shift", {})
        if cls_audit:
            core_web_vitals["cls"] = {
                "value": cls_audit.get("numericValue", 0),
                "displayValue": cls_audit.get("displayValue", ""),
                "score": cls_audit.get("score", 0),
            }
        
        # First Contentful Paint (FCP)
        fcp_audit = audits.get("first-contentful-paint", {})
        if fcp_audit:
            core_web_vitals["fcp"] = {
                "value": fcp_audit.get("numericValue", 0) / 1000,
                "displayValue": fcp_audit.get("displayValue", ""),
                "score": fcp_audit.get("score", 0),
            }
        
        # Speed Index
        speed_index_audit = audits.get("speed-index", {})
        if speed_index_audit:
            core_web_vitals["speed_index"] = {
                "value": speed_index_audit.get("numericValue", 0) / 1000,
                "displayValue": speed_index_audit.get("displayValue", ""),
                "score": speed_index_audit.get("score", 0),
            }
        
        # Overall scores
        performance_score = categories.get("performance", {}).get("score", 0)
        accessibility_score = categories.get("accessibility", {}).get("score", 0)
        best_practices_score = categories.get("best-practices", {}).get("score", 0)
        seo_score = categories.get("seo", {}).get("score", 0)
        
        # Performance opportunities (things to fix)
        opportunities = []
        for audit_key, audit_data in audits.items():
            score = audit_data.get("score")
            savings_ms = audit_data.get("details", {}).get("overallSavingsMs", 0)
            
            # Only include if score is low and has significant savings
            if score is not None and score < 0.9 and savings_ms and savings_ms > 500:
                opportunities.append({
                    "title": audit_data.get("title", ""),
                    "description": audit_data.get("description", ""),
                    "savings_ms": savings_ms,
                    "score": score,
                })
        
        # Sort opportunities by potential savings
        opportunities.sort(key=lambda x: x["savings_ms"], reverse=True)
        
        return {
            "url": url,
            "performance_score": int((performance_score or 0) * 100),
            "accessibility_score": int((accessibility_score or 0) * 100),
            "best_practices_score": int((best_practices_score or 0) * 100),
            "seo_score": int((seo_score or 0) * 100),
            "core_web_vitals": core_web_vitals,
            "opportunities": opportunities[:5],  # Top 5 opportunities
            "analysis_timestamp": lighthouse_result.get("fetchTime", ""),
        }
    
    async def analyze_multiple_pages(self, urls: List[str]) -> List[Dict]:
        """Analyze performance for multiple pages."""
        
        tasks = [self.analyze_performance(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        performance_data = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Performance analysis failed for {urls[i]}: {result}")
                continue
            if result is not None:
                performance_data.append(result)
        
        return performance_data


# Singleton instance
_performance_analyzer: Optional[PerformanceAnalyzer] = None


def get_performance_analyzer(api_key: Optional[str] = None) -> PerformanceAnalyzer:
    """Get or create the performance analyzer singleton."""
    global _performance_analyzer
    if _performance_analyzer is None:
        _performance_analyzer = PerformanceAnalyzer(api_key=api_key)
    return _performance_analyzer