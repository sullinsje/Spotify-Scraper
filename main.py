import requests
from dotenv import load_dotenv
import os
from models import Artist, Track, Album, Playlist, Base, DB_Track
from pydantic import ValidationError
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

#region: token stuff + database stuff
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

AUTH_URL = "https://accounts.spotify.com/api/token"
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

auth_response_data = auth_response.json()

access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

SQLALCHEMY_DATABASE_URL = "sqlite:///./playlist.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

#endregion

def get_artist(artist_name):
    BASE_URL = 'https://api.spotify.com/v1/artists/'

    uri = search(artist_name, 'artist')
    if (uri != -1):
        uri = uri.replace('spotify:artist:', "")
        result = requests.get(BASE_URL + uri, headers=headers)
        
        if result.status_code == 200:
            try:
                data = result.json()
                artist = Artist(**data)
                return artist
            except ValidationError:
                print("Could not find artist!")
        else:
            print("Could not find artist!")
    else:
        print("Uri not found!")
    
def get_track(track_name):
    BASE_URL = 'https://api.spotify.com/v1/tracks/'

    uri = search(track_name, 'track')
    if (uri != -1):
        uri = uri.replace('spotify:track:', "")
        result = requests.get(BASE_URL + uri, headers=headers)
        
        if result.status_code == 200:
            try:
                data = result.json()
                track = Track(**data)
                return track
            except:
                print("Could not find track!")
        else:
            print("Could not find track!")
    else:
        print("Uri not found!")

def get_album(album_name):
    BASE_URL = 'https://api.spotify.com/v1/albums/'

    uri = search(album_name, 'album')
    if (uri != -1):
        uri = uri.replace('spotify:album:', "")
        result = requests.get(BASE_URL + uri, headers=headers)
        
        if result.status_code == 200:
            try:
                data = result.json()
                album = Album(**data)
                return album
            except:
                print("Could not find album!")
        else:
            print("Could not find album!")
    else:
        print("Uri not found!")

def search(term, type):
    search_types = ['artist', 'track', 'album']
    if type not in search_types:
        return -1
    
    BASE_URL = 'https://api.spotify.com/v1/search/'
    params = { 'q': term, 'type': type, 'limit': 1 }
    result = requests.get(BASE_URL, headers=headers, params=params)

    if result.status_code == 200:
        data = result.json()
        try:
            uri = data[type + 's']['items'][0]['uri']
        except:
            return -1
        return uri
    else:
        return -1

def create_playlist(name):
    playlist = Playlist(name=name)
    return playlist

def niche_calculator(item):
    if type(item) == Artist:
        popularity = item.popularity
        if popularity > 50:
            return ("not very niche...")
        else:
            return ("you must frequent rym...")
    elif type(item) == Track or type(item) == Album:
        popularity = item.popularity
        if popularity > 30:
            return ("not very niche...")
        else:
            return ("you must frequent rym...")
    else:
        return "Can't judge the popularity of this item..."

def item_to_db(item):
    if type(item) == Track:
        idExist = exists().where(item.id == DB_Track.ID)
        idExist = session.query(idExist).scalar()
        if idExist == False:
            artists = ""
            for a in item.artists:
                artists += f"{a.__repr__()}, "
            artists = artists[:-2]
            t = DB_Track(ID=item.id, Name=item.name, 
                     Artists=artists, Track_Number=item.track_number,
                     Album=item.album.__repr__(), Popularity=item.popularity)
            try:
                session.add(t) 
                session.commit()
                input("Item added successfully!")
            except:
                print("An error occurred...")
        else:
            print("Item already exists!")
    
    elif type(item) == Album:
        for track in item.tracks.items:
            idExist = exists().where(track.id == DB_Track.ID)
            idExist = session.query(idExist).scalar()
            if idExist == False:
                artists = ""    
                for a in item.artists:
                    artists += f"{a.__repr__()}, "
                artists = artists[:-2]
                t = DB_Track(ID=track.id, Name=track.name, 
                            Artists=artists, Track_Number=track.track_number,
                            Album=item.name)
                try:
                    session.add(t) 
                    session.commit()
                    print("Item added successfully!")
                except:
                    print("An error occurred...")
            else:
                print("Item already exists!")

    elif type(item) == Playlist:
        for track in item.playlist:
            idExist = exists().where(track.id == DB_Track.ID)
            idExist = session.query(idExist).scalar()
            if idExist == False:
                artists = ""    
                for a in track.artists:
                    artists += f"{a.__repr__()}, "
                artists = artists[:-2]
                t = DB_Track(ID=track.id, Name=track.name, 
                            Artists=artists, Track_Number=track.track_number,
                            Album=track.album.name)
                try:
                    session.add(t) 
                    session.commit()
                except:
                    print("An error occurred...")
            else:
                print(f"{track.name} already exists!")
    else:
        print("Cannot add this item...")

def print_tests():
    weezer = get_artist("Jawbreaker")
    print(weezer.__repr__())

    song = get_track("Radio Christie Front Drive")
    print(song.__repr__())

    album = get_album("Agony & Irony")
    print(album.__repr__())

    print(niche_calculator(weezer))
    print(niche_calculator(song))
    print(niche_calculator(album))
    print(niche_calculator(12))

def playlist_tests(song1, song2, song3, playlist_name):
    playlist = Playlist(playlist_name)

    song = get_track(song1)
    playlist.Add(song)

    song = get_track(song2)
    playlist.Add(song)

    song = get_track(song3)
    playlist.Add(song)

    print(playlist.__repr__())

def db_tests(song_title, album_title, song_title2):
    song = get_track(song_title)
    item_to_db(song)
    album = get_album(album_title)
    item_to_db(album)
    playlist = Playlist("p")
    playlist.Add(get_track(song_title2))
    item_to_db(playlist)

#db_tests("Dumpweed", "blink-182", "Touchdown Boy")
#print_tests()
def testrun():
    while True:
        os.system("cls")
        print("We're going to add songs to a database from Spotify.")
        x = input("Create an album, track, or playlist? (Q to quit)\n")
        if x.upper() == "ALBUM":
            os.system("cls")
            a = input("What item would you like to create? (Including artist helps filter search!) ")
            try:
                album = get_album(a)
                while True:
                    os.system("cls")
                    c = input("Add item to database? (Y/N) ")
                    if c.upper() == 'Y':
                        item_to_db(album)
                        input()
                        break
                    elif c.upper() == 'N':
                        break
                    else:
                        print("invalid option...")
            except:
                print("An error occurred...")

        elif x.upper() == "TRACK":
            os.system("cls")
            t = input("What item would you like to create? (Including artist helps filter search!) ")
            try:
                track = get_track(t)
                while True:
                    os.system("cls")
                    c = input("Add item to database? (Y/N) ")
                    if c.upper() == 'Y':
                        item_to_db(track)
                        input()
                        break
                    elif c.upper() == 'N':
                        break
                    else:
                        print("invalid option...")
            except:
                print("An error occurred...")

        elif x.upper() == "PLAYLIST":
            os.system("cls")
            print("Let's create a playlist!")
            name = input("Playlist name: ")
            playlist = Playlist(name)

            while True:
                os.system("cls")
                t = input("Create a track to add (including artist filters results): ")
                try:
                    track = get_track(t)
                    playlist.Add(track)
                    c = input("Press enter to add another or Q to quit... ")
                    if c.upper() == "Q":
                        break
                except:
                    input("An error occurred...")

            try:
                while True:
                    os.system("cls")
                    c = input("Add item to database? (Y/N) ")
                    if c.upper() == 'Y':
                        item_to_db(playlist)
                        input()
                        break
                    elif c.upper() == 'N':
                        break
                    else:
                        print("invalid option...")
            except:
                print("An error occurred...")
        elif x.upper() == "Q":
            break
        else:
            print("Invalid input entered...")
            input()
testrun()
