from typing import Optional, Dict, List, Set
from redis_om import Field
import datetime

from models import BaseModel

class Game(BaseModel):
    created_ts: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now(datetime.timezone.utc))  # Creation timestamp
    guild_id: int = Field(index=True)
    
    text_channel_ids: Set = Field(index=True)
    '''Channels this game belongs to. Each channel can be assigned to only one game. Takes precedence over categories'''

    category_ids: Set = Field(index=True)
    '''Channel categories this game belongs to. Each category can be assigned to only one game, but channels within can override the game assigned'''

    display_name: str
    '''Display version of search_name (can have mix of upper and lowercase letters)'''

    search_name: str = Field(index=True, min_length=2, max_length=64)
    '''User-searchable name. Must be all lowercase'''

    type: Optional[str] = 'D&D'

    # char_ids: Optional[Set[str]]
    # characters: Optional[Dict[str, Dict]]
