from pydantic import BaseModel

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from typing import List

Base = declarative_base()

#region: simplified versions of classes
class S_Artist(BaseModel):
    name: str
    def __repr__(self):
        return self.name

class S_Album(BaseModel):
    name: str
    release_date: str 
    def __repr__(self):
        return f"{self.name}"
  
class S_Track(BaseModel):
    name: str
    track_number: int
    id: str
    artists: list[S_Artist]

    def __repr__(self):
        x = ""
        for artist in self.artists:
            x += artist.__repr__()
        return f"{self.track_number}. {self.name} - {x}"
        

#endregion

class Artist(BaseModel):
    id: str
    name: str
    followers: dict
    genres: list
    popularity: int

    def __repr__(self):
        followers = self.followers['total']
        genres = ""
        for genre in self.genres:
            genres += f"{genre}, "
        genres = genres[:-2]

        return f"{self.name}\nFollowers: {followers}\nGenres: {genres}\nPopularity: {self.popularity}/100"
  
class Track(BaseModel):
    id: str
    name: str
    popularity: int
    artists: list[S_Artist]
    album: S_Album
    track_number: int
    def __repr__(self):
        artists = ""
        for artist in self.artists:
            artists += artist.__repr__()
        return f"{self.name} - {artists} (Track {self.track_number} from the album: {self.album.__repr__()}) \npopularity: {self.popularity}/100"

class Tracks(BaseModel):
    items: list[S_Track]

    def __repr__(self):
        output = "Track list: \n"
        for track in self.items:
            output += track.__repr__() + "\n"
        return output

class Album(BaseModel):
    id: str
    type: str
    total_tracks: int
    name: str
    release_date: str
    artists: List[S_Artist]
    tracks: Tracks
    popularity: int
        
    def __repr__(self):
        artists = ""
        for artist in self.artists:
            artists += artist.__repr__()
        return f"{self.name}\n{artists}\nReleased: {self.release_date}\nPopularity: {self.popularity}/100\n{self.tracks.__repr__()}"

class Playlist:
    def __init__(self, name):
        self.name = name
        self.playlist = []

    def Add(self, item):
        if type(item) == Track:
            self.playlist.append(item)
        elif type(item) == Album:
            for track in item.tracks.items:
                self.playlist.append(track)
        else:
            print("Cannot add this item!")
    
    def __repr__(self):
        output = f"{self.name}:\n"
        for track in self.playlist:
            artists = ""
            for artist in track.artists:
                artists += artist.__repr__()
            output += f"{track.name} - {artists}\n"
        return output
    
class DB_Track(Base):
    __tablename__ = "Songs"

    ID = Column(String, primary_key=True)
    Name = Column(String)
    Artists = Column(String)
    Track_Number = Column(Integer)
    Album = Column(String)
    Popularity = Column(String)

    def __repr__(self):
        return (f"{'ID: ' + self.ID:<25}\t{'Name: ' + self.Name:<25}\t{'Artist: ' + self.Artists:<25}\tTrack Number: {self.Track_Number}\t'Album: {self.Album}\tPopularity: {self.Popularity}")