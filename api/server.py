from flask import Flask, jsonify, request, redirect, url_for, session
from flask_cors import CORS, cross_origin
import requests

import os



from MusicManager import AppleManager, SpotifyManager, YouTubeManager

AM = AppleManager()
SP = SpotifyManager()
YT = YouTubeManager()



app = Flask(__name__) # Initialize the Flask application
CORS(app) # and enable CORS


@app.route('/')
@cross_origin()
def index():
    #return {'message': 'Connected to EZ-Shift API'}
    client = os.environ.get('APPLE_KEY_ID')
    redirect = os.environ.get('APPLE_REDIRECT')
    auth = f"https://appleid.apple.com/auth/authorize?client_id={client}&response_type=code&redirect_uri={redirect}&scope=music"
    print(f"Auth URL: {auth}")
    return redirect(auth)


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
    code = request.args.get('code')
    client = os.environ.get('APPLE_TEAM_ID')
    secret = os.environ.get('APPLE_KEY_ID')
    redirect = os.environ.get('APPLE_REDIRECT')

    url = f"https://appleid.apple.com/auth/token?grant_type=authorization_code&code={code}&client_id={client}&client_secret={secret}&redirect_uri={redirect}"
    response = requests.post(url)
    data = response.json()
    print(f"Data: {data}")
    return data['access_token']

@app.route('/Apple/Playlist', methods=['GET']) # get the users playlists from spotify
@cross_origin()
def getAM():
    
    data = AM.getPlaylists() # Get the playlists , an array of objects
        
    return jsonify(data)


@app.route('/Apple/Convert', methods=['POST'])  # Convert a playlist to Apple Music
@cross_origin()
def postAM():

    data = request.get_json() # Get the data from the request

    if data['playlist']['origin'] == 'Spotify': # If the playlist doesn't exist, create it

        id = data['playlist']['id']

        tracks = SP.getTracks(id) # Get the tracks from the request

    else:

        tracks = data['playlist']['tracks']

    AM.postPlaylist(data, tracks) # Post the playlist to the server

    return jsonify(success=True)




#Youtube Music

@app.route('/Youtube/Playlist', methods=['GET']) # Get All Library Playlists
@cross_origin()
def getYT():
    #YT.get()
    data = YT.getPlaylists() # Get the playlists , an array of objects
        
    return jsonify(data)

@app.route('/Youtube/Convert', methods=['POST']) # Convert a playlist to Youtube
@cross_origin()
def postYT():   
    data = request.get_json() # Get the data from the request

    id = data['playlist']['id']
    
    if data['playlist']['origin'] == 'Apple': # If the playlist doesn't exist, create it
    
        tracks = AM.getTracks(id) # Get the tracks from the request
    
    elif data['playlist']['origin'] == 'Spotify': 

        tracks = SP.getTracks(id)

    else:

        tracks = data['playlist']['tracks']

    YT.postPlaylist(data, tracks) # Post the playlist to the server

    return jsonify(success=True)


@app.route('/Youtube/Playlist/2', methods=['GET']) # get the users playlists from Youtube Music
@cross_origin()
def getYT2():
    #if 'credentials' not in session:

        #return redirect(url_for('authorize'))

    oauth2_token = os.environ.get('YOUTUBE_API_KEY')

    url = 'https://www.googleapis.com/youtube/v3/playlists'

    headers = {"Accept": "application/json", "Authorization": f"Bearer {oauth2_token}"}

    response = requests.get(url, headers = headers)

    data = response.json()

    print(data)

    return jsonify(data)


# Start the server when the script is run directly
if __name__ == '__main__':
    app.run()
    