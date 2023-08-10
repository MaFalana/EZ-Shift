//
//  EZ_ShiftApp.swift
//  EZ-Shift
//
//  Created by Malik Falana on 7/27/23.
//

import SwiftUI

@main
struct EZ_ShiftApp: App
{
    @StateObject var platformManager = PlatformManager.shared
    
    var body: some Scene {
        WindowGroup {
            MainView()
                .environmentObject(platformManager)
        }
    }
}
