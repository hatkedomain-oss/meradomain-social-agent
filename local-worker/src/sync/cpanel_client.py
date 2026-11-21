"""
MeraDomain Social Agent - cPanel REST API Client
Communicates with https://social.meradomain.in/api/
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
try:
    from config import settings
except ImportError:
    try:
        from ..config import settings
    except ImportError:
        from ...config import settings

class CpanelClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = (api_url or settings.CPANEL_API_URL).rstrip("/")
        self.api_key = api_key or settings.CPANEL_API_KEY
        self.headers = {
            "X-API-KEY": self.api_key,
            "Accept": "application/json"
        }

    def upload_media(self, file_path: Path) -> str:
        """Uploads a visual plate to cPanel and returns the public URL."""
        if not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {file_path}")

        url = f"{self.api_url}/upload.php"
        with open(file_path, "rb") as f:
            files = {"media": (file_path.name, f, "image/png")}
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=self.headers, files=files)
                res.raise_for_status()
                data = res.json()
                if not data.get("success"):
                    raise RuntimeError(f"Upload failed: {data.get('error')}")
                return data["url"]

    def sync_campaign(self, campaign_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pushes a full campaign and draft posts to cPanel queue (Status: PENDING_REVIEW)."""
        url = f"{self.api_url}/posts.php"
        with httpx.Client(timeout=20.0) as client:
            res = client.post(url, headers=self.headers, json=campaign_payload)
            res.raise_for_status()
            return res.json()

    def fetch_due_posts(self) -> List[Dict[str, Any]]:
        """Queries approved posts due for publishing."""
        url = f"{self.api_url}/posts.php?due=1"
        with httpx.Client(timeout=15.0) as client:
            res = client.get(url, headers=self.headers)
            res.raise_for_status()
            data = res.json()
            return data.get("posts", [])

    def mark_published(self, post_id: int, published_url: Optional[str] = None) -> Dict[str, Any]:
        """Updates post status to PUBLISHED with link."""
        url = f"{self.api_url}/posts.php"
        payload = {
            "id": post_id,
            "status": "PUBLISHED",
            "published_url": published_url
        }
        with httpx.Client(timeout=15.0) as client:
            res = client.patch(url, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()

    def mark_failed(self, post_id: int, error_log: str) -> Dict[str, Any]:
        """Updates post status to FAILED with error details."""
        url = f"{self.api_url}/posts.php"
        payload = {
            "id": post_id,
            "status": "FAILED",
            "error_log": error_log
        }
        with httpx.Client(timeout=15.0) as client:
            res = client.patch(url, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()
