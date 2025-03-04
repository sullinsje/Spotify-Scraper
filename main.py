import requests
from dotenv import load_dotenv
import os
from models import Artist, Track, S_Track, Album, Playlist, Base, DB_Track
from pydantic import ValidationError
from sqlalchemy import create_engine, exists, select, delete
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

cache = []
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

def create_playlist():
    os.system("cls")
    name = input("What would you like to name this playlist?\n")
    playlist = Playlist(name=name)
    print("Press enter to add items...")
    input()
    while True:
        os.system("cls")
        item = get_item()
        if item != -1:
            playlist.Add(item)
            again = input("Press enter to continue or 'Q' to quit...").upper()
            if again == 'Q':
                break
        else:
            break
    return playlist

def niche_calculator():
    item = get_item()

    os.system("cls")
    if type(item) == Artist:
        print(item.__repr__())
        popularity = item.popularity
        if popularity > 50:
            print(f"not very niche...")
        else:
            print(f"super niche! you aren't a poser!")
    elif type(item) == Track or type(item) == Album:
        print(item.__repr__())
        popularity = item.popularity
        if popularity > 30:
            print(f"not very niche...")
        else:
            print(f"super niche! you aren't a poser!")
    else:
        print("Can't judge the popularity of this item...")
    
    print("Press enter to continue...")
    input()

def get_item():
    while True:
        os.system("cls")
        type = input("What item would you like to get?\n1. artist\n2. track\n3. album\n4. exit\n")
        
        if type == '1':
            os.system("cls")
            artist_name = input("Enter the artist name:\n")
            artist = get_artist(artist_name)
            cache.append(artist)
            return artist
        
        elif type == '2':
            os.system("cls")
            track_name = input("Enter the track name:\n")
            track = get_track(track_name)
            cache.append(track)
            return track
        
        elif type == '3':
            os.system("cls")
            album_name = input("Enter the album name:\n")
            album = get_album(album_name)
            cache.append(album)
            return album
        
        elif type == '4':
            return -1

        else:
            os.system("cls")
            print("An error occurred! Press enter to continue...\n")
            input()

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
                print("Item added successfully!")
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
                if type(track) == Track:
                    t = DB_Track(ID=track.id, Name=track.name, 
                                Artists=artists, Track_Number=track.track_number,
                                Album=track.album.name)
                elif type(track) == S_Track:
                    t = DB_Track(ID=track.id, Name=track.name, 
                                Artists=artists, Track_Number=track.track_number,
                                Album=None)
                try:
                    session.add(t) 
                    session.commit()
                    print("Item added successfully!")
                except:
                    print("An error occurred...")
            else:
                print(f"{track.name} already exists!")
    else:
        print("Cannot add this item...")
    print("Press enter to continue...")
    input()

def view_item():
    while True:
        item = get_item()
        if item != -1:
            os.system("cls")
            print(item.__repr__())
            v = verify_search()
            if v == "N":
                print("Sorry the info was not what you desired. Try adding more terms to narrow down the search!")
            
            x = input("Press enter to continue or 'Q' to quit...").upper()
            if x == 'Q':
                break
        else:
            break
    
def verify_search():
    while True:
        x = input("Is this what you were looking for? (Y/N)\n").upper()
        if x == "N" or x == "Y":
            break
        else:
            print("Invalid option!")
    return x

def read_all():
    os.system("cls")
    output = ""
    result = session.execute(select(DB_Track))
    for value in result:
        output += ('\n' + value.__repr__())
    if output == "":
        output = "Empty database!"
    
    return output

def _delete():
    os.system("cls")
    x = read_all()
    print(x)
    
    if x != "Empty database!":
        track = input("\nWhat track would you like to delete? (Enter ID of song above!)\n")
        nameExist = exists().where(DB_Track.ID == track)
        nameExist = session.query(nameExist).scalar()
        if track == "" or nameExist == False:
            print("Track doesn't exist!")
            input("Press enter to continue...")
            return
        
        de = delete(DB_Track).where(DB_Track.ID == track)
        try:
            session.execute(de)
            session.commit()
            print("Track successfully deleted!")
            input("Press enter to continue...")
        except Exception:
            print("An error occurred. Press enter to continue...")
            input()
    else:
        print("Press enter to continue...")
        input()

def display_menu():
    print("========== Main Menu ==========")
    print("1. Create an Item")
    print("2. Niche Calculator")
    print("3. Create a Playlist")
    print("4. Post to database")
    print("5. Delete from database")
    print("6. Clear database")
    print("7. View database")
    print("8. View Playlists")
    print("9. Exit")
    print("===============================")

def menu():
    while True:
        os.system("cls")
        display_menu()
        option = input("Choose a menu option (1, 2, 3, 4, 5, 6, 7, 8): ")

        if option == "1":
            os.system("cls")
            view_item()

        elif option == "2":
            os.system("cls")
            niche_calculator()
            
        elif option == "3":
            os.system("cls")
            p = create_playlist()
            cache.append(p)
            print("Playlist successfully created! Press enter to continue...")
            input()
            
        elif option == "4":
            os.system("cls")
            for i in range(0, len(cache)):
                print(f"{i}. {cache[i].name} ({type(cache[i])})")
            if len(cache) > 0:
                while True:
                    try:
                        x = (int(input("Which previously viewed item would you like to add to database? (-1 to quit)\n")))
                        
                        if x >= 0 and x < len(cache):
                            item = cache.pop(x)
                            item_to_db(item)
                            break
                        elif x == -1:
                            break
                        else:
                            print("Invalid option!")
                    except:
                        print("Value was not an integer!")

            else:
                print("No items have been created! Press enter to continue...")
                input()

        elif option == "5":
            os.system("cls")
            _delete()
        
        elif option == "6":
            os.system("cls")
            try:
                session.query(DB_Track).delete()
                session.commit()
                print("Database successfully cleared!")
            except:
                print("An error occurred...")
            
            print("Press enter to continue...")
            input()
        
        elif option == "7":
            os.system("cls")
            print(read_all())
            print("Press enter to continue...")
            input()
        
        elif option == "8":
            os.system("cls")
            for i in range(0, len(cache)):
                if type(cache[i]) == Playlist:
                    print(f"{cache[i]}\n\n")
            print("Press enter to continue...")
            input()

        elif option == "9":
            os.system("cls")
            print("Goodbye!")
            break

        else:
            os.system("cls")
            print("Invalid input entered.")
            input("Press enter to continue...")

menu()