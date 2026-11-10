from __future__ import annotations
from typing import Any

FORMATS = {"apa", "harvard"}
def cite_sources(url: str, style: str = "apa") -> dict[str, Any]:
    try: 
       if not url.startswith("http"):
           raise ValueError("Invalid URL format. URL must start with 'http' or 'https'.")
       if style not in FORMATS:
           raise ValueError(f"Invalid citation style. Supported styles are: {', '.join(FORMATS)}.")
       return {"tool": "cite_sources", "result": {"cited": f"Cited {url} in {style} style."}}
    except Exception as exc:
       return {"tool": "cite_sources", "result": {"error": str(exc)}}