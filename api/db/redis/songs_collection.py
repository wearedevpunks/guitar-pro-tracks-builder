from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .base import RedisCollectionBase
from api.infrastructure.logging import get_logger


class Song(BaseModel):
    """Song model for Guitar Pro tracks."""
    
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Artist name")
    album: Optional[str] = Field(None, description="Album name")
    genre: Optional[str] = Field(None, description="Music genre")
    year: Optional[int] = Field(None, description="Release year", ge=1900, le=2100)
    duration: Optional[int] = Field(None, description="Duration in seconds", ge=0)
    tempo: Optional[int] = Field(None, description="Tempo in BPM", ge=1, le=300)
    key_signature: Optional[str] = Field(None, description="Key signature (e.g., 'C major', 'Am')")
    time_signature: Optional[str] = Field(None, description="Time signature (e.g., '4/4', '3/4')")
    difficulty: Optional[int] = Field(None, description="Difficulty level (1-10)", ge=1, le=10)
    instruments: List[str] = Field(default_factory=list, description="List of instruments")
    tags: List[str] = Field(default_factory=list, description="Song tags/categories")
    file_path: Optional[str] = Field(None, description="Path to the Guitar Pro file")
    description: Optional[str] = Field(None, description="Song description")
    is_public: bool = Field(default=True, description="Whether the song is publicly visible")
    created_by: Optional[str] = Field(None, description="User ID who created the song")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Master of Puppets",
                "artist": "Metallica",
                "album": "Master of Puppets",
                "genre": "Heavy Metal",
                "year": 1986,
                "duration": 515,
                "tempo": 212,
                "key_signature": "E minor",
                "time_signature": "4/4",
                "difficulty": 8,
                "instruments": ["Electric Guitar", "Bass Guitar", "Drums"],
                "tags": ["metal", "thrash", "classic"],
                "file_path": "songs/master_of_puppets.gp5",
                "description": "Epic thrash metal masterpiece",
                "is_public": True,
                "created_by": "user123"
            }
        }


class SongsCollection(RedisCollectionBase[Song]):
    """Songs collection with specialized methods for Guitar Pro tracks."""
    
    def __init__(self, redis_client=None):
        """Initialize the songs collection."""
        super().__init__(
            collection_name="songs",
            model_class=Song,
            redis_client=redis_client
        )
        self.logger = get_logger(__name__)
    
    async def search_by_artist(self, artist: str, limit: int = 100) -> List[Song]:
        """Search songs by artist name."""
        self.logger.debug(f"Searching songs by artist: {artist}")
        
        # Get all items and filter by artist
        all_items = await self.list(limit=1000)  # Large limit for searching
        
        matching_songs = [
            song for song in all_items 
            if artist.lower() in song.artist.lower()
        ][:limit]
        
        self.logger.debug(f"Found {len(matching_songs)} songs by artist: {artist}")
        return matching_songs
    
    async def search_by_genre(self, genre: str, limit: int = 100) -> List[Song]:
        """Search songs by genre."""
        self.logger.debug(f"Searching songs by genre: {genre}")
        
        filters = {"genre": genre}
        songs = await self.list(limit=limit, filters=filters)
        
        self.logger.debug(f"Found {len(songs)} songs in genre: {genre}")
        return songs
    
    async def get_by_difficulty_range(self, min_difficulty: int, max_difficulty: int, limit: int = 100) -> List[Song]:
        """Get songs within a difficulty range."""
        self.logger.debug(f"Getting songs with difficulty {min_difficulty}-{max_difficulty}")
        
        all_items = await self.list(limit=1000)
        
        matching_songs = [
            song for song in all_items 
            if song.difficulty is not None and min_difficulty <= song.difficulty <= max_difficulty
        ][:limit]
        
        self.logger.debug(f"Found {len(matching_songs)} songs in difficulty range")
        return matching_songs
    
    async def get_by_instrument(self, instrument: str, limit: int = 100) -> List[Song]:
        """Get songs that include a specific instrument."""
        self.logger.debug(f"Getting songs with instrument: {instrument}")
        
        all_items = await self.list(limit=1000)
        
        matching_songs = [
            song for song in all_items 
            if any(instrument.lower() in instr.lower() for instr in song.instruments)
        ][:limit]
        
        self.logger.debug(f"Found {len(matching_songs)} songs with instrument: {instrument}")
        return matching_songs
    
    async def get_by_tags(self, tags: List[str], match_all: bool = False, limit: int = 100) -> List[Song]:
        """Get songs by tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, song must have all tags. If False, any tag matches.
            limit: Maximum number of results
        """
        self.logger.debug(f"Getting songs with tags: {tags}, match_all: {match_all}")
        
        all_items = await self.list(limit=1000)
        
        if match_all:
            matching_songs = [
                song for song in all_items 
                if all(tag.lower() in [t.lower() for t in song.tags] for tag in tags)
            ]
        else:
            matching_songs = [
                song for song in all_items 
                if any(tag.lower() in [t.lower() for t in song.tags] for tag in tags)
            ]
        
        result = matching_songs[:limit]
        self.logger.debug(f"Found {len(result)} songs with tags")
        return result
    
    async def get_public_songs(self, limit: int = 100) -> List[Song]:
        """Get all public songs."""
        self.logger.debug("Getting public songs")
        
        filters = {"is_public": True}
        songs = await self.list(limit=limit, filters=filters)
        
        self.logger.debug(f"Found {len(songs)} public songs")
        return songs
    
    async def get_songs_by_user(self, user_id: str, limit: int = 100) -> List[Song]:
        """Get songs created by a specific user."""
        self.logger.debug(f"Getting songs by user: {user_id}")
        
        filters = {"created_by": user_id}
        songs = await self.list(limit=limit, filters=filters)
        
        self.logger.debug(f"Found {len(songs)} songs by user: {user_id}")
        return songs
    
    async def get_recent_songs(self, days: int = 30, limit: int = 100) -> List[Song]:
        """Get recently created songs."""
        self.logger.debug(f"Getting songs from last {days} days")
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        songs = await self.list_by_created_date(start_date=cutoff_date, limit=limit)
        
        self.logger.debug(f"Found {len(songs)} recent songs")
        return songs
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics."""
        self.logger.debug("Getting songs collection statistics")
        
        total_songs = await self.count()
        public_songs = await self.count(filters={"is_public": True})
        
        # Get all songs to calculate other stats
        all_songs = await self.list(limit=10000)
        
        genres = {}
        artists = {}
        difficulties = {}
        years = {}
        
        for song in all_songs:
            # Genre stats
            if song.genre:
                genres[song.genre] = genres.get(song.genre, 0) + 1
            
            # Artist stats
            artists[song.artist] = artists.get(song.artist, 0) + 1
            
            # Difficulty stats
            if song.difficulty:
                difficulties[song.difficulty] = difficulties.get(song.difficulty, 0) + 1
            
            # Year stats
            if song.year:
                years[song.year] = years.get(song.year, 0) + 1
        
        stats = {
            "total_songs": total_songs,
            "public_songs": public_songs,
            "private_songs": total_songs - public_songs,
            "top_genres": dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:10]),
            "top_artists": dict(sorted(artists.items(), key=lambda x: x[1], reverse=True)[:10]),
            "difficulty_distribution": dict(sorted(difficulties.items())),
            "year_distribution": dict(sorted(years.items(), reverse=True)[:10])
        }
        
        self.logger.debug("Generated songs collection statistics")
        return stats


# Global songs collection instance
_songs_collection: Optional[SongsCollection] = None


def get_songs_collection() -> SongsCollection:
    """Get the global songs collection instance."""
    global _songs_collection
    
    if _songs_collection is None:
        _songs_collection = SongsCollection()
    
    return _songs_collection


def reset_songs_collection() -> None:
    """Reset the global songs collection instance (useful for testing)."""
    global _songs_collection
    if _songs_collection:
        # Note: In a real scenario, you might want to close the Redis connection
        pass
    _songs_collection = None