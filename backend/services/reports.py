"""
Reports service for retrieving past analyses.
"""

from datetime import datetime, timedelta
from typing import List
import random


async def get_user_reports_mock(user_id: int, limit: int = 10, offset: int = 0) -> dict:
    """
    Mock function to retrieve user's past reports.
    
    TODO: Replace with real database query using SQLAlchemy.
    """
    
    # Generate mock reports
    reports = []
    total = random.randint(3, 15)
    
    if offset >= total:
        return {
            "reports": [],
            "total": total
        }

    available = max(total - offset, 0)

    for i in range(min(limit, available)):
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        reports.append({
            "analysis_id": 1000 + offset + i,
            "overall_score": random.randint(70, 95),
            "urls": [
                f"https://example.com/page{random.randint(1, 5)}",
                f"https://example.com/checkout",
            ],
            "created_at": created_at.isoformat()
        })
    
    return {
        "reports": reports,
        "total": total
    }


async def get_report_by_id_mock(analysis_id: int) -> dict:
    """
    Mock function to retrieve detailed report by ID.
    
    TODO: Replace with real database query.
    """
    
    from .analyzer import analyze_funnel_mock
    
    # Generate mock detailed report
    mock_urls = [
        "https://example.com/sales",
        "https://example.com/checkout",
        "https://example.com/upsell"
    ]
    
    result = await analyze_funnel_mock(mock_urls)
    result["analysis_id"] = analysis_id
    
    return result
