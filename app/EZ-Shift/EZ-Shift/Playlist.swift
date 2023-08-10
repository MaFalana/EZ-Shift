//
//  Playlist.swift
//  EZ-Shift
//
//  Created by Malik Falana on 7/27/23.
//

import Foundation

struct Playlist: Codable
{
    var id: String
    
    var title: String
    
    var image: String
    
    var description: String
    
    var tracks: [Track]
}


struct Track: Codable
{
    var id: String
    
    var title: String
    
    var artist: String
}
