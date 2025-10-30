"""Device fingerprinting utilities for session tracking and attribution."""

import hashlib
from typing import Optional


def generate_fingerprint(
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    screen_resolution: Optional[str] = None,
    timezone: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    """
    Generate a device fingerprint hash from available browser/device data.
    
    This creates a semi-stable identifier for tracking sessions across
    page views when cookies aren't available or for probabilistic matching.
    
    Args:
        ip_address: Client IP address (IPv4 or IPv6)
        user_agent: Browser user agent string
        screen_resolution: Screen resolution (e.g., "1920x1080")
        timezone: Browser timezone (e.g., "America/New_York")
        language: Browser language (e.g., "en-US")
    
    Returns:
        SHA256 hash of the combined fingerprint data
    
    Note:
        Fingerprints are NOT 100% unique and can change when:
        - IP address changes (VPN, mobile network switching)
        - Browser updates (user agent changes)
        - Screen resolution changes (external monitor)
        
        Use as probabilistic matching, not guaranteed identity.
    """
    components = [
        ip_address or "",
        user_agent or "",
        screen_resolution or "",
        timezone or "",
        language or "",
    ]
    
    # Combine all components with a delimiter
    fingerprint_string = "|".join(components)
    
    # Generate SHA256 hash
    fingerprint_hash = hashlib.sha256(fingerprint_string.encode("utf-8")).hexdigest()
    
    return f"fp_{fingerprint_hash[:32]}"  # Prefix + first 32 chars for readability


def normalize_ip(ip_address: Optional[str]) -> Optional[str]:
    """
    Normalize IP address for more stable fingerprinting.
    
    For IPv6, this could include removing local segments.
    For now, just returns the IP as-is.
    """
    if not ip_address:
        return None
    
    # Future enhancement: normalize IPv6, handle proxies, etc.
    return ip_address.strip()


def calculate_fingerprint_similarity(fp1: str, fp2: str) -> float:
    """
    Calculate similarity between two fingerprints (0.0 to 1.0).
    
    Since fingerprints are hashes, they're either identical or not.
    This function is here for future enhancements where we might
    use partial matching or fuzzy fingerprinting.
    
    Returns:
        1.0 if identical, 0.0 if different
    """
    return 1.0 if fp1 == fp2 else 0.0
