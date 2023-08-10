//
//  Platforms.swift
//  EZ-Shift
//
//  Created by Malik Falana on 7/27/23.
//

import Foundation

protocol Platform
{
    var name: String {get set}
    
    var playlists: [Playlist] {get set}
    
    func Authorize()
    
    func getPlaylists() //Populates Playlists array
    
    func Convert(destination: Platform, playlist: Playlist) //Converts playlist to another platform
    
}

final class Spotify: Platform
{
    var name: String = "Spotify"
    
    var playlists: [Playlist] = []
    
    func Authorize() {
        <#code#>
    }
    
    func getPlaylists()
    {
        <#code#>
    }
    
    
    
    func Convert(destination: Platform, playlist: Playlist)
    {
        let title = playlist.title // Take name, image, description
        
        let image = playlist.image
        
        let description = playlist.description //"Playlist created with EZ-Shift"
        
        var Tracks: [Track] = [] //Create an empty array to store tracks
        
        for track in playlist.tracks // in a loop
        {
            var query = "\(track.artist) \(track.title)" // create a string using the name and title of each track
            
            var track = searchTracks(query: query)
            
            Tracks.append(track) // add tracks
        }
        
        
        //POST request
    }
    
    func getTracks(id: String, key: String) async -> [Track] // Method to get the tracks from a playlist
    {
        let limit = 50
        
        var offset = 0
        
        var tracks: [Track] = [] // Create an empty array to store the tracks
        
        guard let url = createUrl(id: id) else
        {
            print("Invalid URL.")
            return []
        }
        
        var request = URLRequest(url: url)
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        
        do
        {
            let (data, _) = try await URLSession.shared.data(for: request)
            
            // decode data
            //let decodedResponse = try? JSONDecoder().decode(Track.self, from: data)
            let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
            
            if let items = json?["items"] as? [[String: Any]]
            {
                for item in items // Loop through the tracks and get the track name and artist name
                {
                    var source = item["track"] as! [String: Any]
                    var artistData = source["artists"] as! [[String: Any]]
                    
                    var trackID = source["id"] as! String
                    var title = source["name"] as! String
                    var artist = artistData.first?["name"] as! String
                    var uri = source["uri"] as! String
                    var track = Track(id: trackID, title: title, artist: artist)
                    tracks.append(track) // Append the track to the list
                }
                
                return tracks
            }
        }
        catch let error
        {
            print("ERROR = \(error.localizedDescription)")
        }
    
    }
    
    func searchTracks(query: String) -> Track
    {
        
    }
    
    func createUrl(id: String) -> URL? //Create url to get tracks
    {
        var components = URLComponents()
        components.scheme = "https"
        components.host = "api.spotify.com"
        components.path = "/v1/playlists/\(id)/tracks"
        components.queryItems =
        [
            URLQueryItem(name: "market", value: "US"),
            URLQueryItem(name: "limit", value: "\(50)"),
            URLQueryItem(name: "offset", value: "\(0)")
        ]
        
        let url = components.url // create url
                
        return url
    }
    
}


final class Youtube: Platform
{
    var name: String = "Youtube"
    
    var playlists: [Playlist] = []
    
    func Authorize()
    {
        <#code#>
    }
    
    func getPlaylists()
    {
        <#code#>
    }
    
    func Convert(destination: Platform, playlist: Playlist)
    {
        <#code#>
    }
    
}
