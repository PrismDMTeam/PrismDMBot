from typing import Optional
from redis_om import Field
import datetime

from models.base_model import BaseModel

class Game(BaseModel):
    created_ts: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)  # Creation timestamp
    guild_id: int = Field(index=True)

    display_name: str  # Display version of search_name (can have mix of upper and lowercase letters)
    search_name: str = Field(index=True, min_length=2, max_length=64)  # User-searchable name. Must be all lowercase

    type: Optional[str] = 'D&D'

    char_ids: Optional[list[str]]
