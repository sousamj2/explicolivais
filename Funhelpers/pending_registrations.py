from cachetools import TTLCache
from typing import Optional, Dict

# TTLCache with max 1000 entries and 1 hour (3600 seconds) TTL
pending_registrations = TTLCache(maxsize=1000, ttl=3600)

def save_pending_registration(token: str, data: Dict) -> None:
    pending_registrations[token] = data

def get_pending_registration(token: str) -> Optional[Dict]:
    return pending_registrations.get(token)

def delete_pending_registration(token: str) -> None:
    if token in pending_registrations:
        del pending_registrations[token]
