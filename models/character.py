from typing import Dict, Optional
from models.base_model import BaseModel
from redis_om import Field
import datetime

class Attribute(BaseModel):
    display_name: str  # Display version of search_name (can have mix of upper and lowercase letters)
    search_name: str = Field(index=True, min_length=2, max_length=64)  # User-searchable name. Must be all lowercase

    value: int
    max_value: Optional[int]

class Character(BaseModel):
    created_ts: Optional[datetime.datetime] = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))  # Creation timestamp
    player_id: Optional[int] = Field(default=None, index=True)
    game_id: str = Field(index=True)

    display_name: str  # Display version of search_name (can have mix of upper and lowercase letters)
    search_name: str = Field(index=True, min_length=2, max_length=64)  # User-searchable name. Must be all lowercase

    attributes: Dict[str, Attribute]  # Character stats