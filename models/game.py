from typing import Optional, Dict, List, Set
from redis_om import Field
import datetime

from models import BaseModel

class Game(BaseModel):
    created_ts: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now(datetime.timezone.utc))  # Creation timestamp
    guild_id: int = Field(index=True)
    
    text_channel_ids: List[str] = Field(index=True)
    '''
    Channels this game belongs to. Each channel can be assigned to only one game. Takes precedence over categories.
    Due to limitation in Redis OM preview, must store IDs as str
    '''

    category_ids: List[str] = Field(index=True)
    '''
    Channel categories this game belongs to. Each category can be assigned to only one game, but channels within can override the game assigned.
    Due to limitation in Redis OM preview, must store IDs as str
    '''

    display_name: str
    '''Display version of search_name (can have mix of upper and lowercase letters)'''

    search_name: str = Field(index=True, min_length=2, max_length=64)
    '''User-searchable name. Must be all lowercase'''

    type: Optional[str] = 'D&D'

    # char_ids: Optional[Set[str]]
    # characters: Optional[Dict[str, Dict]]
