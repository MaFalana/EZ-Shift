from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests

import os, jwt, datetime, calendar, time

from cryptography.hazmat.primitives import serialization

from api.MusicManager import SpotifyManager, YouTubeManager

SP = SpotifyManager()
YT = YouTubeManager()



app = Flask(__name__) # Initialize the Flask application
CORS(app) # and enable CORS


@app.route('/', methods=['GET']) # Home route
@cross_origin()
def home():
    return jsonify({"Meassage": "Welcome to the EZ-Shift API!"})


@app.route('/Spotify/Playlist', methods=['GET']) # get the users playlists from spotify
@cross_origin()
def getSpotify():

    data = SP.getPlaylists() # Get the playlists , an array of objects
        
    return jsonify(data)


# Create Playlist
@app.route('/Spotify/Convert', methods=['POST']) # Create a playlist on Spotify
@cross_origin()
def postSpotify():

    data = request.get_json() # Get the data from the request

    tracks = data['playlist']['tracks'] # Get the tracks from the request

    tracks = SP.searchSpotifyTracks(tracks) # Get the tracks from the request

    print(f'Tracks: {tracks}')
    
    SP.postPlaylist(data, tracks) # Post the playlist to the server

    return jsonify(success=True)


# Add items to playlist



#Apple Music

'''
Get All Library Playlists


Create a New Library Playlist
POST https://api.music.apple.com/v1/me/library/playlists

Add Tracks to a Library Playlist
POST https://api.music.apple.com/v1/me/library/playlists/{id}/tracks
'''
@app.route('/Apple/Callback', methods=['GET']) # 
@cross_origin()
def loginAM():
    #session.clear() # Clear the session
    client = os.environ.get('APPLE_TEAM_ID')
    redirect = os.environ.get('APPLE_REDIRECT')
    
    auth_url = f"https://appleid.apple.com/auth/authorize?client_id={client}&response_type=code&redirect_uri={redirect}"

    print(f'Auth URL: {auth_url}')
    
    return redirect(auth_url)


@app.route('/Apple/Playlist', methods=['GET']) # get the users playlists from spotify
@cross_origin()
def getAM():
    key = getDeveloperToken() # Generate the Apple Developer Token
    #key = os.environ.get('APPLE_DEV_TOKEN')

    print(key)

    url = 'https://api.music.apple.com/v1/me/library/playlists'

    headers = {
        "Accept": "application/json", 
        "Authorization": f"Bearer {key}",
        "Music-User-Token": ''
        }

    response = requests.get(url, headers = headers)

    data = response.json()

    print(data)

    playlists = data['data'] # Get the playlists , an array of objects

    total = data['meta']['total'] # Get the total number of playlists

    list = [] # Create an empty array to store the playlists

    for i in range(0, total): # Loop through the playlists and get the tracks
        
        w = playlists[i]['attributes']['artwork']['width']

        h = playlists[i]['attributes']['artwork']['height']

        image = playlists[i]['attributes']['artwork']['url'].replace('{w}', str(w)).replace('{h}', str(h))

        DATA = {
        'id': playlists[i]['id'],
        'title': playlists[i]['attributes']['name'],
        'image':  image,
        'description': playlists[i]['attributes']['description']['standard'],
        'tracks': [] #getAppleTracks(playlists[i]['id'])
    }
        list.append(DATA) # Append the playlist to the list
        
    return jsonify(list)


@app.route('/Apple/Convert', methods=['POST'])  # Convert a playlist to Apple Music
@cross_origin()
def postAM():

    data = request.get_json() # Get the data from the request

    playlist = data['playlist'] # Get the data from the request

    title = playlist['title'] # Get the title of the playlist

    songs = playlist['tracks'] # Get the playlists , an array of objects

    tracks = [] # Get the playlists , an array of objects

    playlist = {
    'name': title,  # Should be the same as the name from the original playlist
    'description': 'Playlist created by EZ-Shift',
    'tracks': tracks, # array of tracks from the original playlist
    }

    getDeveloperToken() # Generate the Apple Developer Token
    key = os.environ.get('APPLE_DEV_TOKEN')

    print(key)

    url = 'https://api.music.apple.com/v1/me/library/playlists'

    headers = {"Accept": "application/json", "Authorization": f"Bearer {key}"}

    response = requests.post(url, headers = headers, json = playlist)

    data = response.json()

    print(data)

def getDeveloperToken(): #Generates a Developer Token
    path = "./AuthKey.p8"  # Path to private key file
    alg = os.environ.get('APPLE_ALG')  # Asymmetric algorithm used to generate key
    key_id = os.environ.get('APPLE_KEY_ID')  # 10-character key identifier

    time_now = int(time.time())
    time_exp = int(calendar.timegm((datetime.datetime.now() + datetime.timedelta(days=180)).utctimetuple()))

    with open(path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    headers = {
	"alg": alg,
	"kid": key_id
    }

    jwt_payload = {
        "iss": "X3392H7G44",
        "iat": time_now,
        "exp": time_exp,
    }

    developer_token = jwt.encode(jwt_payload, private_key, algorithm=alg, headers=headers)
    
    os.environ['APPLE_DEV_TOKEN'] = developer_token

    return developer_token


#Youtube Music

@app.route('/Youtube/Playlist', methods=['GET']) # Get All Library Playlists
@cross_origin()
def getYT():
    data = YT.getPlaylists() # Get the playlists , an array of objects
        
    return jsonify(data)

@app.route('/Youtube/Convert', methods=['POST']) # Convert a playlist to Youtube
@cross_origin()
def postYT():   
    data = request.get_json() # Get the data from the request

    if data['playlist']['origin'] == 'Spotify': # If the playlist doesn't exist, create it

        id = data['playlist']['id']

        tracks = SP.getTracks(id) # Get the tracks from the request

    else:

        tracks = data['playlist']['tracks']

    YT.postPlaylist(data, tracks) # Post the playlist to the server

    return jsonify(success=True)


# Start the server when the script is run directly
if __name__ == '__main__':
    app.run()
    