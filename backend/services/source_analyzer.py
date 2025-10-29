"""Source code analysis service for extracting technical insights from HTML source."""

from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SourceCodeAnalyzer:
    """Analyzes raw HTML source for technical SEO and conversion optimization insights."""
    
    def __init__(self):
        self.tracking_patterns = {
            "google_analytics": [
                r"gtag\s*\(",
                r"ga\s*\(",
                r"GoogleAnalyticsObject",
                r"gtm\.js",
            ],
            "facebook_pixel": [
                r"fbevents\.js",
                r"fbq\s*\(",
                r"facebook\.net/en_US/fbevents\.js",
            ],
            "google_ads": [
                r"googleads\.g\.doubleclick\.net",
                r"gtag.*AW-",
                r"google_conversion_id",
            ],
            "hotjar": [
                r"hotjar\.com/",
                r"hj\s*\(",
            ],
            "intercom": [
                r"intercom\.io",
                r"Intercom\s*\(",
            ],
            "drift": [
                r"drift\.com",
                r"drift\.load",
            ],
            "mixpanel": [
                r"mixpanel\.com",
                r"mixpanel\.track",
            ],
        }
    
    def analyze_source(self, html_content: str, url: str) -> Dict:
        """
        Analyze raw HTML source for technical insights.
        
        Args:
            html_content: Raw HTML source code
            url: The page URL
            
        Returns:
            Dict with technical analysis results
        """
        soup = BeautifulSoup(html_content, "lxml")
        
        return {
            "url": url,
            "tracking_analysis": self._analyze_tracking(html_content),
            "structured_data": self._extract_structured_data(soup),
            "meta_analysis": self._analyze_meta_tags(soup),
            "performance_hints": self._analyze_performance(soup, html_content),
            "conversion_elements": self._analyze_conversion_elements(soup),
            "technical_seo": self._analyze_technical_seo(soup),
        }
    
    def _analyze_tracking(self, html_content: str) -> Dict:
        """Detect tracking and analytics implementations."""
        
        tracking_found = {}
        
        for platform, patterns in self.tracking_patterns.items():
            found = False
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    found = True
                    break
            tracking_found[platform] = found
        
        # Count total tracking scripts
        total_tracking = sum(1 for found in tracking_found.values() if found)
        
        # Check for common conversion tracking
        conversion_tracking = {
            "google_conversion": bool(re.search(r"google_conversion_id|gtag.*event.*conversion", html_content, re.IGNORECASE)),
            "facebook_conversion": bool(re.search(r"fbq.*track.*Purchase|fbq.*track.*Lead", html_content, re.IGNORECASE)),
            "custom_events": len(re.findall(r"gtag.*event|fbq.*track|mixpanel\.track", html_content, re.IGNORECASE)),
        }
        
        return {
            "platforms_detected": tracking_found,
            "total_platforms": total_tracking,
            "conversion_tracking": conversion_tracking,
            "privacy_compliance": self._check_privacy_compliance(html_content),
        }
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract JSON-LD and other structured data."""
        
        structured_data = []
        
        # JSON-LD scripts
        json_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append({
                    "type": "json-ld",
                    "schema_type": data.get("@type", "Unknown") if isinstance(data, dict) else "Multiple",
                    "data": data,
                })
            except json.JSONDecodeError:
                pass
        
        # Microdata
        microdata_items = soup.find_all(attrs={"itemtype": True})
        for item in microdata_items[:5]:  # Limit to prevent overflow
            structured_data.append({
                "type": "microdata",
                "schema_type": item.get("itemtype", "").split("/")[-1],
                "properties": [prop.get("itemprop") for prop in item.find_all(attrs={"itemprop": True})],
            })
        
        return structured_data
    
    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict:
        """Analyze meta tags for SEO and social sharing."""
        
        meta_analysis = {
            "title": soup.title.string if soup.title else None,
            "description": None,
            "keywords": None,
            "og_tags": {},
            "twitter_tags": {},
            "robots": None,
            "canonical": None,
        }
        
        # Basic meta tags
        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag:
            meta_analysis["description"] = description_tag.get("content", "")
        
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag:
            meta_analysis["keywords"] = keywords_tag.get("content", "")
        
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        if robots_tag:
            meta_analysis["robots"] = robots_tag.get("content", "")
        
        # Canonical URL
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag:
            meta_analysis["canonical"] = canonical_tag.get("href", "")
        
        # Open Graph tags
        og_tags = soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")})
        for tag in og_tags:
            prop = tag.get("property", "").replace("og:", "")
            meta_analysis["og_tags"][prop] = tag.get("content", "")
        
        # Twitter Card tags
        twitter_tags = soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")})
        for tag in twitter_tags:
            name = tag.get("name", "").replace("twitter:", "")
            meta_analysis["twitter_tags"][name] = tag.get("content", "")
        
        return meta_analysis
    
    def _analyze_performance(self, soup: BeautifulSoup, html_content: str) -> Dict:
        """Analyze performance-related elements."""
        
        # Count resources
        scripts = soup.find_all("script", src=True)
        stylesheets = soup.find_all("link", rel="stylesheet")
        images = soup.find_all("img", src=True)
        
        # Check for optimization techniques
        has_minification = "min.js" in html_content or "min.css" in html_content
        has_compression = bool(re.search(r"gzip|br|deflate", html_content))
        has_cdn = any(
            "cdn" in script.get("src", "") or "amazonaws" in script.get("src", "")
            for script in scripts
        )
        
        # Check for lazy loading
        has_lazy_loading = any(
            img.get("loading") == "lazy" or "lazy" in img.get("class", [])
            for img in images
        )
        
        return {
            "resource_counts": {
                "scripts": len(scripts),
                "stylesheets": len(stylesheets),
                "images": len(images),
            },
            "optimizations": {
                "minification": has_minification,
                "compression_hints": has_compression,
                "cdn_usage": has_cdn,
                "lazy_loading": has_lazy_loading,
            },
            "inline_styles": len(soup.find_all("style")),
            "inline_scripts": len(soup.find_all("script", src=False)),
        }
    
    def _analyze_conversion_elements(self, soup: BeautifulSoup) -> Dict:
        """Analyze conversion-related elements."""
        
        # Trust badges and security indicators
        trust_indicators = []
        security_keywords = ["ssl", "secure", "verified", "certified", "guarantee", "trusted", "norton", "mcafee"]
        
        for keyword in security_keywords:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            if elements:
                trust_indicators.append(keyword)
        
        # Social proof elements
        social_proof = {
            "testimonials": len(soup.find_all(string=re.compile(r"testimonial|review|feedback", re.IGNORECASE))),
            "customer_count": bool(soup.find_all(string=re.compile(r"\d+.*customers?|\d+.*clients?|\d+.*users?", re.IGNORECASE))),
            "ratings": len(soup.find_all(attrs={"class": lambda x: x and "star" in str(x).lower()})),
        }
        
        # Urgency and scarcity elements
        urgency_keywords = ["limited", "expires", "hurry", "now", "today", "deadline", "countdown"]
        urgency_elements = []
        
        for keyword in urgency_keywords:
            if soup.find_all(string=re.compile(keyword, re.IGNORECASE)):
                urgency_elements.append(keyword)
        
        return {
            "trust_indicators": trust_indicators,
            "social_proof": social_proof,
            "urgency_elements": urgency_elements,
            "forms_count": len(soup.find_all("form")),
            "cta_buttons": len(soup.find_all(["button", "input"], type=["submit", "button"])),
        }
    
    def _analyze_technical_seo(self, soup: BeautifulSoup) -> Dict:
        """Analyze technical SEO elements."""
        
        # Heading structure
        headings = {}
        for i in range(1, 7):
            headings[f"h{i}"] = len(soup.find_all(f"h{i}"))
        
        # Image optimization
        images = soup.find_all("img")
        images_without_alt = sum(1 for img in images if not img.get("alt"))
        
        # Internal vs external links
        links = soup.find_all("a", href=True)
        external_links = sum(1 for link in links if link.get("href", "").startswith("http"))
        internal_links = len(links) - external_links
        
        return {
            "heading_structure": headings,
            "images": {
                "total": len(images),
                "missing_alt": images_without_alt,
                "alt_optimization": (len(images) - images_without_alt) / len(images) * 100 if images else 100,
            },
            "links": {
                "total": len(links),
                "internal": internal_links,
                "external": external_links,
            },
            "page_size_estimate": len(str(soup)) // 1024,  # Rough estimate in KB
        }
    
    def _check_privacy_compliance(self, html_content: str) -> Dict:
        """Check for privacy compliance indicators."""
        
        privacy_keywords = ["privacy policy", "cookie", "gdpr", "ccpa", "consent"]
        compliance_indicators = {}
        
        for keyword in privacy_keywords:
            compliance_indicators[keyword] = bool(
                re.search(keyword.replace(" ", r"\s+"), html_content, re.IGNORECASE)
            )
        
        return compliance_indicators


# Singleton instance
_source_analyzer: Optional[SourceCodeAnalyzer] = None


def get_source_analyzer() -> SourceCodeAnalyzer:
    """Get or create the source code analyzer singleton."""
    global _source_analyzer
    if _source_analyzer is None:
        _source_analyzer = SourceCodeAnalyzer()
    return _source_analyzer