import os
from dotenv import load_dotenv
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests, base64, jwt, time, calendar, datetime
from cryptography.hazmat.primitives import serialization
from flask import request

import google_auth_oauthlib.flow

import googleapiclient.discovery
import googleapiclient.errors




load_dotenv()

ytmusic = YTMusic("api/oauth.json")  # Create an instance of the Youtube Music API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ.get('SPOTIFY_CLIENT'), client_secret=os.environ.get('SPOTIFY_SECRET'), redirect_uri=os.environ.get('REDIRECT'), scope=os.environ.get('SPOTIFY_SCOPES')))

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
        
        list = [] # Create an empty array to store the playlists

        url = 'https://api.music.apple.com/v1/me/library/playlists'

        list = self.addMore(list, url)

        print(f"Total Playlists: {len(list)}")
        
        return list

    def getTracks(self, id):

        list = []

        url = f"https://api.music.apple.com/v1/me/library/playlists/{id}/tracks"

        headers = {
            "Accept": "application/json", 
            "Authorization": f"Bearer {os.environ.get('APPLE_DEV_TOKEN')}",
            "Music-User-Token": f"{os.environ.get('APPLE_MUSIC_USER_TOKEN')}"
            }
        
        response = requests.get(url, headers = headers)

        data = response.json()

        #print(data)

        tracks = data['data'] # Get the playlists , an array of objects

        for item in tracks: # Loop through the tracks and get the track name and artist name
            DATA = {
            'id': item['id'],
            'title': item['attributes']['name'],
            'artist': item['attributes']['artistName']
            }

            list.append(DATA) # Append the track to the list

        return list

    def postPlaylist(self, data):
        
        playlist = data['playlist'] # Get the data from the request

        title = playlist['title'] # Get the title of the playlist

        #tracks = [] # Get the playlists , an array of objects

        playlist = {
            'attributes': 
            {
                'name': title,  # Should be the same as the name from the original playlist
                'description': 'Playlist created by EZ-Shift',
                'artwork': data['playlist']['image']
            }
        }

        url = 'https://api.music.apple.com/v1/me/library/playlists'

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('APPLE_DEV_TOKEN')}",
            "Music-User-Token": f"{os.environ.get('APPLE_MUSIC_USER_TOKEN')}"
            }


        response = requests.post(url, headers = headers, json = playlist)

        data = response.json()

        return data['data'][0]['id']


    def addTracks(self, id, tracks):

        list = []

        for track in tracks:

            Track = {
                'id': track['id'],
                'type': 'songs'
            }

            list.append(Track)

        data = {
            'data': list
        }

        url = f'https://api.music.apple.com/v1/me/library/playlists/{id}/tracks'

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('APPLE_DEV_TOKEN')}",
            "Music-User-Token": f"{os.environ.get('APPLE_MUSIC_USER_TOKEN')}"
            }


        response = requests.post(url, headers = headers, json = data)

        #data = response.json()

        #print(data)


    def getDeveloperToken(self): #Generates a Developer Token for Apple Music

        devToken = os.environ.get('APPLE_DEV_TOKEN')

        if devToken != "": # If the token exists, return it

                return devToken
        else:

            path = "api/AuthKey.p8"  # Path to private key file
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
        

    def authorize(self):# Redirect the user to Apple's authentication page
        client = os.environ.get('APPLE_TEAM_ID')
        redirect = os.environ.get('APPLE_REDIRECT')
        auth = f"https://appleid.apple.com/auth/authorize?client_id={client}&response_type=code&redirect_uri={redirect}&scope=music"
        return redirect(auth)
    
    def getMusicToken(self): # Get the Music User Token
        self.authorize()
        code = request.args.get('code')
        client = os.environ.get('APPLE_TEAM_ID')
        secret = os.environ.get('APPLE_KEY_ID')
        redirect = os.environ.get('APPLE_REDIRECT')

        url = f"https://appleid.apple.com/auth/token?grant_type=authorization_code&code={code}&client_id={client}&client_secret={secret}&redirect_uri={redirect}"
        response = requests.post(url)
        data = response.json()
        
        return data['access_token']
    
    def searchTracks(self, source): # Method to get the tracks from a playlist that is going to be converted to Apple Music

        tracks = [] # Create an empty array to store the tracks

        for song in source: #appends the songs from the source playlist

            query = f"{song['artist']} {song['title']}"

            print(f'Searching for: {query}')

            url = f"https://api.music.apple.com/v1/catalog/us/search?types=songs&term={query}"

            headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('APPLE_DEV_TOKEN')}",
            "Music-User-Token": f"{os.environ.get('APPLE_MUSIC_USER_TOKEN')}"
            }


            response = requests.get(url, headers = headers)

            data = response.json()

            if 'results' in data:

                result = data['results'] # Get the tracks, an array of objects

                if 'songs' in result:

                    item = result['songs']['data'][0]

                    track = {
                    'id': item['id'],
                    'title': item['attributes']['name'],
                    'artist': item['attributes']['artistName'],
                    'uri': item['attributes']['url']
                    }

                    tracks.append(track) # Append the track to the list

        return tracks
    

    def addImage(self, playlist):

        attributes = playlist['attributes']

        if 'artwork' in attributes: # If the playlist has an image, return the image url

            artwork = playlist['attributes']['artwork']

            w = artwork['width']

            h = artwork['height']

            return artwork['url'].replace('{w}', str(w)).replace('{h}', str(h))

        else:
            return None
        

    def addDescription(self, playlist):

        attributes = playlist['attributes']

        if 'description' in attributes: # If the playlist has an image, return the image url

            return playlist['attributes']['description']['standard']

        else:
            return None

    def addMore(self, list, url):

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('APPLE_DEV_TOKEN')}",
            "Music-User-Token": f"{os.environ.get('APPLE_MUSIC_USER_TOKEN')}"
            }

        response = requests.get(url, headers = headers)

        #print(response.content)

        if response.status_code == 200: # If the request is successful, return the playlists

            data = response.json()

            playlists = data['data'] # Get the playlists , an array of objects

            for playlist in playlists: # Loop through the playlists and get the tracks
                
                image = self.addImage(playlist)
                description  = self.addDescription(playlist)

                DATA = {
                'id': playlist['id'],
                'title': playlist['attributes']['name'],
                'image':  image,
                'description': description,
                'tracks': [], #getAppleTracks(playlists[i]['id'])
                'origin': 'Apple Music'
            }
                list.append(DATA) # Append the playlist to the list

            if 'next' in data and data['next'] is not None:
                url = f'https://api.music.apple.com{data["next"]}'
                list = self.addMore(list, url)

            return list
        

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
        'description': 'Playlist created by EZ-Shift',
        'public': False,
        'tracks': [track['uri'] for track in tracks] # array of tracks from the original playlist
        }

        new = sp.user_playlist_create(user_id, playlist['name'], playlist['public'], False, playlist['description'])

        sp.playlist_add_items(new['id'], playlist['tracks'])

        if source['image'] is not None:

            sp.playlist_upload_cover_image(new['id'], self.createCoverArt(source['image']))

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


    def searchTracks(self, source): # Method to get the tracks from a playlist that is going to be converted to spotify

        total = len(source)

        limit = 1

        errors = []

        tracks = [] # Create an empty array to store the tracks

        for song in source: #appends the songs from the source playlist

            query = f"{song['artist']} {song['title']}"

            data = sp.search(q=query, type='track', limit=limit)

            if data:

                if data['tracks']['items']:

                    item = data['tracks']['items'][0] # Get the tracks , an array of objects

                    track = {
                    'id': item['id'],
                    'title': item['name'],
                    'artist': item['artists'][0]['name'],
                    'uri': item['uri']
                    }

                    tracks.append(track) # Append the track to the list

            else:

                errors.append(query)

        if len(errors) > 0:
            print(f'Error transferring {errors}')


        return tracks

    def createCoverArt(self, image):
        data = requests.get(image).content
        image_base64 = base64.b64encode(data).decode('utf-8')
        return image_base64


# Youtube Music Manager
class YouTubeManager(MusicManager):
    def __init__(self):
        super().__init__() # Call the parent constructor



    def get(self):

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file("api/YoutubeSecret.json", scopes)
        flow.redirect_uri = os.environ.get('YOUTUBE_REDIRECT')

        credentials = flow.run_local_server(port=5000)
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials = credentials)

        request = youtube.playlists()

        response = request.execute()

        print(response)

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

