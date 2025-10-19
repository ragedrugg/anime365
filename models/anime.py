"""
Модели для аниме (Series)
"""

from typing import List, Optional, Union, TYPE_CHECKING
from pydantic import BaseModel, Field
from .common import Title, Link, Description, Genre

if TYPE_CHECKING:
    from .episodes import Episode


class Series(BaseModel):
    """Модель аниме (сериала)"""
    id: int
    aniDbId: Optional[int] = None
    animeNewsNetworkId: Optional[int] = None
    fansubsId: Optional[int] = None
    imdbId: Optional[int] = None
    worldArtId: Optional[int] = None
    isActive: Optional[int] = None
    isAiring: Optional[int] = None
    isHentai: Optional[int] = None
    links: List[Link] = Field(default_factory=list)
    myAnimeListId: Optional[int] = None
    myAnimeListScore: Optional[str] = None
    worldArtScore: Optional[str] = None
    worldArtTopPlace: Optional[Union[str, int]] = None
    numberOfEpisodes: Optional[int] = None
    season: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    typeTitle: Optional[str] = None
    titles: Optional[Title] = None
    posterUrl: Optional[str] = None
    posterUrlSmall: Optional[str] = None
    titleLines: List[str] = Field(default_factory=list)
    allTitles: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    url: Optional[str] = None
    descriptions: List[Description] = Field(default_factory=list)
    episodes: List['Episode'] = Field(default_factory=list)
    genres: List[Genre] = Field(default_factory=list)


class SeriesResponse(BaseModel):
    """Ответ со списком аниме"""
    data: Union[List[Series], Series]
