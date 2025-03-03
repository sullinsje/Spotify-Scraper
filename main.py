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

#region: gets & search
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

#endregion

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

def view_item():
    search_types = ['artist', 'track', 'album']
    while True:
        os.system("cls")
        type = input("What would you like to search for? (album, track, artist) (press 'q' to quit)\n").lower()
        if type in search_types:
            match type:
                case 'artist':
                    os.system("cls")
                    artist_name = input("What artist would you like to search for?\n")
                    artist = get_artist(artist_name)
                    os.system("cls")
                    print(artist.__repr__())
                    v = verify_search()
                    if v == "N":
                        print("Sorry the info was not what you desired. Try adding more terms to narrow down the search!")
                    print("Press enter to continue...")
                    input()
                
                case 'track':
                    os.system("cls")
                    track_name = input("What track would you like to search for?\n")
                    track = get_track(track_name)
                    os.system("cls")
                    print(track.__repr__())
                    v = verify_search()
                    if v == "N":
                        print("Sorry the info was not what you desired. Try adding more terms to narrow down the search!")
                    print("Press enter to continue...")
                    input()

                case 'album':
                    os.system("cls")
                    album_name = input("What album would you like to search for?\n")
                    album = get_album(album_name)
                    os.system("cls")
                    print(album.__repr__())
                    v = verify_search()
                    if v == "N":
                        print("Sorry the info was not what you desired. Try adding more terms to narrow down the search!")
                    print("Press enter to continue...")
                    input()
                case _:
                    break       

        elif type == 'q':
            break
        else:
            print("Invalid input entered! Press enter to retry...")
            input()

def verify_search():
    while True:
        x = input("Is this what you were looking for? (Y/N)\n").upper()
        if x == "N" or x == "Y":
            break
        else:
            print("Invalid option!")
    return x

def main():
    return 0

view_item()