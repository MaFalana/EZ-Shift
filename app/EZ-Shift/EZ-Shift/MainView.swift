//
//  MainView.swift
//  EZ-Shift
//
//  Created by Malik Falana on 7/27/23.
//

import SwiftUI

struct MainView: View
{
    @StateObject var PM = PlatformManager.shared
    
    @State var selectedPlatform = PM.selectedSource
    
    var body: some View
    {
        Picker("Source", selection: $selectedPlatform).pickerStyle(.wheel)
        Text("Hello World")
        
        
    }
}

struct MainView_Previews: PreviewProvider {
    static var previews: some View {
        MainView()
    }
}
