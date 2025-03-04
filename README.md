# Spotify-Scraper
Utilizes the Spotify Web API to grab data from spotify objects, using this data to create objects to perform functions with.


# Project status prior to upload

### API Keys
The first part of the project outside of deciding I wanted to mess with the Spotify API was to see what I could do with it. Eager to get started, I quickly performed a search on the API authorization workflow for the Spotify API and found a simple workflow that works well for me here: https://stackoverflow.com/q/64461018

The authorization response is formed with the client credentials of the app that must be created in the Spotify dev dashboard. We then get the response as JSON to form our access token which is required for our GET requests. Every request has the header: `'Authorization': 'Bearer {token}'.format(token=access_token)`

### Creating Search and Get Functions
Next was to start messing with the GET requests one can make with the Spotify API. I started with Get Artist; Spotify documentation and code examples in class helped make this incredibly simple. I just made the GET request with the cooresponding endpoint and received the desired JSON. The hard part was parsing this JSON into my desired form. I decided since all the GET requests were similar, I would make a search function. This would use the Search endpoint and two parameters: the search term and the type (artist, album, track). I would then parse the JSON from the GET request inside of my Search function to retrieve the item's URI/ID and then return what was retrieved. Then the returned item could be used inside all GET functions. 
#### Parsing JSON to Pydantic Classes
For ease of getting specific attributes of the JSON received from the GET requests, I created classes for each type of response. I naively began with just artist, track, and album classes without reading too much into the documentation. The classes each had attributes for the desired JSON fields. The first issue I ran into was that albums and tracks returned lists of simplified versions of the other classes, so separate classes needed to be created. Next came issues with attributes themselves; I did not realize that the attributes needed to be named EXACTLY like the fields in the JSON output. With both of these problems solved, I could now create objects with the JSON retrieved from the GET functions, and the functions would return the created object. 

### Other Functions
Described in the planning were three major functions for this project:
- Create Playlist
    - A class was created inside of models.py for a playlist. It has a name and playlist attribute. A function inside of it allows singular tracks to be added (album and simple track functionaliy has not been added)
    - This function during upload only creates an playlist. Items will need to be added
- Niche Calculator
    - Calculates how unpopular a track, album, or artist is based on their Popularity attribute
- Add to Database
    - This function adds the passed in item to a database.
    - At time of upload, the database to update's path is hard-coded in, and the database has to be named "playlist.db" and be inside of the app's directory. May be changed later
    - The passed in item can be a track, playlist, or album. The database holds songs with their name, spotify ID, year, track number, etc., and playlists and albums will be treated as collections and every song in them will be added individually.


## Issues

- The largest issue I faced was creating the classes from JSON I got from the API. Researching did not help me out, and I kept producing solutions that kept hitting the wall. I eventually realized from in class examples that class attributes are named exactly what the JSON fields are. I assume this is because of how Pydantic parses JSON to classes. After naming my attributes correctly, it worked flawlessly.
- Added view_item() function with no issues!
- Cleaned up niche_calculator() function: had issues regarding how I initially wrote the function and needed to change it to ask for the item to calculate niche-ness for
- Added ability to clear the database. Not a common thing to do and was not discussed in class, so had to look up how to using SQLAlchemy.
- I had issues with getting the program to run on machines after cloning the repo. This was due to the lack of an env file. The most simple solution was to add the env directly to github. But this is terrible security wise. I will remove this following grading and eventually figure out a solution. 
- No other major issues experienced. A lot of issues I ran into were simple programming errors; not a lot of issues that stumped me and required research. Any other issues were mostly ran into regarding the database stuff. This was mostly experienced in Lab 2, so I did not have much trouble this time around.
