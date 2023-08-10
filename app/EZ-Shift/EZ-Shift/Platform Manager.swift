//
//  Platform Manager.swift
//  EZ-Shift
//
//  Created by Malik Falana on 7/27/23.
//

import Foundation
import SwiftUI


class PlatformManager: ObservableObject
{
    @AppStorage("selectedSource") var sourceSelected = 0
    
    static let shared = PlatformManager() // Single shared instance of class
    
    public var platforms: [Platform] = [Spotify(), Youtube()]
    
    @Published var selectedSource: Platform = Spotify() //Source Platform
    
    @Published var selectedDestination: Platform = Youtube() //Destination Platform
    
    init(){ getSource() }
    
    public func updateSource(_ source: Int)
    {
        self.selectedSource = self.platforms[source]
        self.sourceSelected = source
        getCollection()
    }
    
    func getSource()
    {
        self.selectedSource = self.platforms[sourceSelected]
        getCollection()
    }
    
    func Convert() //Method to Convert songs from one platform to another
    {
        selectedSource.Convert(destination: selectedDestination)
    }
    
    func getCollection() //Gets playlists for selected source
    {
        selectedSource.playlists.removeAll()// I'll need to clear the array of playlists first
        print(self.selectedSource.name)
        selectedSource.getPlaylists()// Then i'll need to repopulate the array with the new playlists
    }
    
    
}


