import os
from dotenv import load_dotenv
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests, base64

load_dotenv()

ytmusic = YTMusic("api/oauth.json")  # Create an instance of the Youtube Music API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ.get('SPOTIFY_CLIENT'), client_secret=os.environ.get('SPOTIFY_SECRET'), redirect_uri=os.environ.get('SPOTIFY_REDIRECT'), scope=os.environ.get('SPOTIFY_SCOPES')))

class MusicManager(object):
    def __init__(self):
        self.playlists = []

    def getPlaylists(self):
        raise NotImplementedError("Subclasses must implement this method")

    def getTracks(self):
        raise NotImplementedError("Subclasses must implement this method")

    def postPlaylist(self):
        raise NotImplementedError("Subclasses must implement this method")


class AppleManager(MusicManager):
    def __init__(self):
        super().__init__() # Call the parent constructor

    def getPlaylists(self):
        raise NotImplementedError("Subclasses must implement this method")

    def getTracks(self):
        raise NotImplementedError("Subclasses must implement this method")

    def postPlaylist(self):
        raise NotImplementedError("Subclasses must implement this method")


# Spotify Music Manager
class SpotifyManager(MusicManager):
    def __init__(self):
        super().__init__() # Call the parent constructor

    def getPlaylists(self):
        offset = 0 # Set the offset to 0
        total = 1
        list = [] # Create an empty array to store the playlists

        while total != len(list): # Loop through the playlists and get the tracks
            playlists = sp.current_user_playlists(limit=50,offset=offset) # Get the playlists , an array of objects

            print(f'Total playlists: {playlists["total"]}')

            total = playlists["total"]

            for playlist in playlists['items']: # Loop through the playlists and get the tracks
                total = playlist['tracks']['total'] # Get the total number of tracks in the playlist
                DATA = {
                    'id': playlist['id'],
                    'title': playlist['name'],
                    'image':  playlist['images'][0]['url'],
                    'description': f"{playlist['owner']['display_name']} • {total} songs",
                    'tracks': [],#self.getTracks(playlist['id'], total)
                    'origin': 'Spotify'
                }
                
                list.append(DATA) # Append the playlist to the list
            
            print(f'Check Size of list: {len(list)}')

            offset += 50

        return list


    def postPlaylist(self, data, tracks):
        
        user_id = sp.me()['id']  # Get the authenticated user's ID

        source = data['playlist'] # Get the data from the request

        playlist = {
        'name': source['title'],  # Should be the same as the name from the original playlist
        'image': [{'url': source['image']}] , # Should be the same as the image from the original playlist
        'description': 'Playlist created by EZ-Shift',
        'public': False,
        'tracks': [track['uri'] for track in tracks] # array of tracks from the original playlist
        }

        new = sp.user_playlist_create(user_id, playlist['name'], playlist['public'], False, playlist['description'])

        sp.playlist_add_items(new['id'], playlist['tracks'])

        sp.playlist_upload_cover_image(new['id'], self.createCoverArt(playlist['image'][0]['url']))

        print("Playlist created and tracks added successfully!")
        
        

    def getTracks(self, id): # Method to get the tracks from a spotify playlist
        offset = 0 # Set the offset to 0
        list = []
        total = sp.playlist(id)['tracks']['total']

        while total != len(list):

            tracks = sp.playlist_tracks(id,limit=100, offset=offset) # Get the playlists , an array of objects
            
            for item in tracks['items']: # Loop through the tracks and get the track name and artist name
                DATA = {
                'id': item['track']['id'],
                'title': item['track']['name'],
                'artist': item['track']['artists'][0]['name'],
                'uri': item['track']['uri']
            }
                list.append(DATA) # Append the track to the list
            
            offset += 100

        return list


    def searchSpotifyTracks(self, source): # Method to get the tracks from a playlist that is going to be converted to spotify

        limit = 1

        tracks = [] # Create an empty array to store the tracks

        for song in source: #appends the songs from the source playlist

            query = f"{song['artist']} {song['title']}"

            data = sp.search(q=query, type='track', limit=limit)

            item = data['tracks']['items'][0] # Get the tracks , an array of objects

            track = {
            'id': item['id'],
            'title': item['name'],
            'artist': item['artists'][0]['name'],
            'uri': item['uri']
            }

            tracks.append(track) # Append the track to the list

        return tracks

    def createCoverArt(self, image):
        data = requests.get(image).content
        image_base64 = base64.b64encode(data).decode('utf-8')
        return image_base64


# Youtube Music Manager
class YouTubeManager(MusicManager):
    def __init__(self):
        super().__init__() # Call the parent constructor

    #Youtube Music
    def getPlaylists(self):
        playlists = ytmusic.get_library_playlists() # Get the playlists , an array of objects

        list = [] # Create an empty array to store the playlists

        #print(playlists)
        
        total = len(playlists) # Get the total number of playlists

        for i in range(0, total): # Loop through the playlists and get the tracks
            DATA = {
            'id': playlists[i]['playlistId'],
            'title': playlists[i]['title'],
            'image':  playlists[i]['thumbnails'][0]['url'],
            'description': playlists[i]['description'],
            'tracks': self.getTracks(playlists[i]['playlistId']),
            'origin': 'Youtube'
        }
            list.append(DATA) # Append the playlist to the list

            #print(DATA)
            
        return list
    

    def postPlaylist(self, data, tracks):

        playlist = data['playlist'] # Get the data from the request

        title = playlist['title'] # Get the title of the playlist

        #playlist['tracks'] # Get the playlists , an array of objects

        list = [] # Get the playlists , an array of objects

        for song in tracks: # Loop through the playlists and get the tracks

            query = f"{song['artist']} {song['title']}" # Search Query

            print(f'Searching for: {query}')

            results = ytmusic.search(query, "songs") # Search for the song

            if results:
                list.append(results[0]['videoId']) # Appends the first song/video ID to the playlist

        ytmusic.create_playlist(title, "Playlist created by EZ-Shift", "Private", list) # Create the playlist

    
    def getTracks(self, id): # Method to get the tracks from a playlist

        data = ytmusic.get_playlist(id, None) # Get the playlists , an array of objects
        
        tracks = []

        items = data['tracks'] # Get the tracks , an array of objects

        for i in range(0, len(items)): # Loop through the tracks and get the track name and artist name
            DATA = {
            'id': items[i]['videoId'],
            'title': items[i]['title'],
            'artist': items[i]['artists'][0]['name']
            }
            tracks.append(DATA) # Append the track to the list

            #print(DATA)

        return tracks

