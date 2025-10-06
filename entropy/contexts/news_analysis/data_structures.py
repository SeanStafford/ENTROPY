from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsMetadata:
    source: str
    fetch_timestamp: datetime
    article_hash: str
    language: str = "en"



