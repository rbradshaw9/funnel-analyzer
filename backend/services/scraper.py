"""Web scraping service for extracting content from funnel pages."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PageContent:
    """Structured content extracted from a web page."""
    
    def __init__(
        self,
        url: str,
        title: str,
        headings: List[str],
        paragraphs: List[str],
        ctas: List[str],
        meta_description: Optional[str] = None,
        forms: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
    ):
        self.url = url
        self.title = title
        self.headings = headings
        self.paragraphs = paragraphs
        self.ctas = ctas
        self.meta_description = meta_description
        self.forms = forms or []
        self.videos = videos or []
    
    def get_full_text(self) -> str:
        """Combine all text content for analysis."""
        parts = [
            f"Title: {self.title}",
            f"Meta Description: {self.meta_description or 'None'}",
            "\nHeadings:",
            *[f"- {h}" for h in self.headings[:10]],  # Limit to prevent token overflow
            "\nKey Content:",
            *[p[:500] for p in self.paragraphs[:5]],  # Limit paragraph length
            "\nCalls-to-Action:",
            *[f"- {cta}" for cta in self.ctas[:10]],
        ]

        if self.forms:
            parts.extend([
                "\nForms Detected:",
                *[f"- {form}" for form in self.forms[:5]],
            ])

        if self.videos:
            parts.extend([
                "\nEmbedded Media:",
                *[f"- {video}" for video in self.videos[:5]],
            ])
        return "\n".join(parts)


async def scrape_url(url: str, timeout: int = 30) -> PageContent:
    """
    Scrape a single URL and extract relevant content.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        PageContent object with extracted data
        
    Raises:
        Exception: If scraping fails
    """
    logger.info(f"Scraping URL: {url}")
    
    try:
        # Run synchronous requests in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FunnelAnalyzer/1.0; +https://funnelanalyzer.pro)"
                },
            ),
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # Extract title
        title = soup.title.string.strip() if soup.title else urlparse(url).path
        
        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc.get("content", "").strip() if meta_desc else None
        
        # Extract headings (h1, h2, h3)
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(text)
        
        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short paragraphs
                paragraphs.append(text)
        
        # Extract CTAs (buttons, links with action words)
        ctas = []
        cta_keywords = ["buy", "order", "get", "start", "join", "sign", "subscribe", "download", "try", "claim"]
        
        # Find buttons
        for button in soup.find_all(["button", "input"]):
            text = button.get_text(strip=True) or button.get("value", "")
            if text:
                ctas.append(text)
        
        # Find links that look like CTAs
        for link in soup.find_all("a"):
            text = link.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in cta_keywords):
                ctas.append(text)
        
        # Extract forms for lead capture insight
        forms = []
        for form in soup.find_all("form"):
            snippets = []

            heading = form.find(["h1", "h2", "h3", "legend", "label"])
            heading_text = heading.get_text(strip=True) if heading else ""
            if heading_text:
                snippets.append(heading_text)

            inputs = []
            for input_el in form.find_all(["input", "textarea", "select"]):
                placeholder = input_el.get("placeholder", "").strip()
                name = input_el.get("name", "").strip()
                label = input_el.get("aria-label", "").strip()
                descriptor = placeholder or label or name
                if descriptor:
                    inputs.append(descriptor)

            if inputs:
                snippets.append(f"Fields: {', '.join(inputs[:6])}")

            submit_button = form.find(["button", "input"], attrs={"type": "submit"})
            if submit_button:
                submit_text = submit_button.get_text(strip=True) or submit_button.get("value", "").strip()
                if submit_text:
                    snippets.append(f"CTA: {submit_text}")

            if snippets:
                forms.append(" | ".join(snippets))

        # Extract embedded video/iframe content for richer analysis
        videos = []
        for video in soup.find_all("video"):
            src = video.get("src")
            if not src:
                source_tag = video.find("source")
                if source_tag:
                    src = source_tag.get("src")
            if src:
                videos.append(src.strip())

        video_domains = ("youtube", "vimeo", "wistia", "loom", "vid", "stream")
        for iframe in soup.find_all("iframe"):
            src = (iframe.get("src") or "").strip()
            if src and any(domain in src.lower() for domain in video_domains):
                title = (iframe.get("title") or "").strip()
                videos.append(f"{title} - {src}" if title else src)

        logger.info(
            f"Scraped {url}: {len(headings)} headings, {len(paragraphs)} paragraphs, {len(ctas)} CTAs, {len(forms)} forms, {len(videos)} videos"
        )
        
        return PageContent(
            url=url,
            title=title,
            headings=headings,
            paragraphs=paragraphs,
            ctas=ctas,
            meta_description=meta_description,
            forms=forms,
            videos=videos,
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")
        raise Exception(f"Failed to fetch page: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}")
        raise Exception(f"Failed to parse page content: {str(e)}")


async def scrape_funnel(urls: List[str]) -> List[PageContent]:
    """
    Scrape multiple URLs in parallel.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of PageContent objects in the same order as input URLs
    """
    logger.info(f"Scraping funnel with {len(urls)} pages")
    
    tasks = [scrape_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error PageContent objects
    page_contents = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"Failed to scrape {urls[i]}: {str(result)}")
            # Create minimal content for failed pages
            page_contents.append(
                PageContent(
                    url=urls[i],
                    title=f"Failed to load: {urls[i]}",
                    headings=[],
                    paragraphs=[f"Error: {str(result)}"],
                    ctas=[],
                )
            )
        else:
            page_contents.append(result)
    
    return page_contents
