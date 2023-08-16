/**************************************
TITLE: index.js							
AUTHOR: Malik Falana (MF)			
CREATE DATE: 07/21/2023	
PURPOSE: To use jquery and functions for index page
LAST MODIFIED ON: 07/25/2023
LAST MODIFIED BY: Malik Falana (MF)
MODIFICATION HISTORY:
07/21/2023: Original Build
07/22/2023: Worked on Spotify API code
07/24/2023: Added dropdown menu
07/25/2023: Added Youtube Music API code, encounterd ouath issue with Spotify API
08/08/2023: Made MusicManager parent class
08/09/2023: Worked on Spotify API code -> used Spotipy (Spotify API wrapper)
08/10/2023: 
***************************************/
//import getRecentGames from './intrests.js';
//import {getRecentGames, createGame} from './intrests.js';

$(document).ready(function() 
{
  async function authorize() 
  {
    const music = MusicKit.getInstance();
    await music.authorize();
    const token = music.musicUserToken;

    console.log("token is: " + token);
  }

  


    const platform = ["Apple", "Spotify", "Youtube"]; // Platforms to convert to

    var playlists = []; // Playlists to convert

    function fetchData(platform) {
        const url = `http://127.0.0.1:5000/${platform}/Playlist`;
        //const url = `https://ez-shift-server.vercel.app/${platform}/Playlist` // URL to test on vercel
        return new Promise(function (resolve, reject) {
          $.getJSON(url, function (data) {
            resolve(data);
          }).fail(function (error) {
            reject(error);
          });
        });
      }
      
    async function Start() {
      try {
        var selectedPlatform = $("#Source").val();
        console.log(`Platform: ${selectedPlatform}`);
        const data = await fetchData(selectedPlatform);
        playlists.push(...data); // Push the fetched data directly to the playlists array
        console.log(playlists);// Use the playlists data here or perform further actions
        populateMenu();
        
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }


    function selectPlaylist() // Selects playlist to convert
    {
        const selectedOption = $("#Plist").val();

        //console.log(`Selected Playlist: ${selectedOption}`);
    
        const source = playlists.find(item => item.id == selectedOption); // where selectedOption is the value of id in playlists array, set source to the playlist object

        //console.log(`Playlist: ${source.title}`); // Log the title of the playlist

        var html = `<div class = "card card${source.id}">`;
        html += `<div class="container">`;
        html += `<img src=${source.image} alt=${source.id}>`;
        html += `</div>`;
        html += `<div class="details">`;
        html += `<h3>${source.title}</h3>`;
        html += `<p>${source.description}</p>`;
        html += `</div>`;
        html += `</div>`;
        $("#Assignments div.master").html(html); //Append to Intrests Section

        return source;
    }

    function convert() // Converts playlist to other platform
    {
        const playlist = selectPlaylist();

        console.log(`playlist: ${playlist}`);

        const dest = $("#Destination").val();

        const source = $("#Source").val();

        console.log(`You attempted to convert a ${source} playlist to a ${dest} playlist`);

        const url = `http://127.0.0.1:5000/${dest}/Convert`;

        //const url = `https://ez-shift-server.vercel.app/${dest}/Convert` // URL to test on vercel

        //console.log(`Playlist: ${playlist}`);

        if(source == dest) // Checks if playlist is being converted to the same platform
        {
            alert("You cannot convert a playlist to the same platform");
            return;
        }

        // Inside the convert() function
        console.log(JSON.stringify({ playlist: playlist }));
        $.ajax({ type: "POST", url: url, data: JSON.stringify({ playlist: playlist }),
          contentType: "application/json", // Set the Content-Type header
          success: function (data, status) 
          {
            alert(`${playlist.title} was successfully transferred to ${dest}!`);
          },
          error: function (xhr, status, error) 
          {
            alert(`Error transferring ${playlist.title} to ${dest}`);
          }
        });
        
    }

    function login()
    {
        const source = $("#Source").val();

        console.log(`You attempted to convert a ${source} playlist to a ${dest} playlist`);

        const url = `http://127.0.0.1:5000/${source}/Callback`;

        //const url = `https://portfolio-server-omega-gray.vercel.app/${platform}/Convert` // URL to test on vercel

        //console.log(`Playlist: ${playlist}`);

        $.ajax({ type: "POST", url: url, data: JSON.stringify({ playlist: playlist }),
          contentType: "application/json", // Set the Content-Type header
          success: function (data, status) 
          {
            alert(`success!`);

            var html = `<a href="${data.auth_url}">Login to ${source}</a>`;

            $("#Assignments a").html(html);
          },
          error: function (xhr, status, error) 
          {
            alert(`Error`);
          }
        });
    }

    // Function to handle Apple Music login
  function loginToAppleMusic() {
    MusicKit.getInstance().authorize().then(function(response) {
      // Authentication succeeded, handle the response
      console.log('Apple Music authentication successful!');
      console.log('Music User Token:', response);
      
      // Send the Music User Token to your Python backend for further processing
      $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/Apple/Callback", // Replace with your actual endpoint
        data: JSON.stringify({ music_user_token: response.musicUserToken }),
        contentType: "application/json",
        success: function(data) {
          console.log('Successfully sent Music User Token to backend');
          // Handle any further actions after successful authentication if needed
        },
        error: function(xhr, status, error) {
          console.error('Error sending Music User Token to backend');
        }
      });
    }).catch(function(error) {
      // Authentication failed, handle the error
      console.error('Apple Music authentication failed:', error);
    });
  }


    for(var i = 0; i < platform.length; i++) // Populates Dropdown Menu for Source
    {
        var html = `<option value=${platform[i]}>${platform[i]}</option>`;
        $("#Source").append(html);
    }

    for(var i = 0; i < platform.length; i++) // Populates Dropdown Menu for Destination
    {
        var html = `<option value=${platform[i]}>${platform[i]}</option>`;
        $("#Destination").append(html);
    }

    function populateMenu() // Populates Dropdown Menu for Playlist to convert
    {
        for(var i = 0; i < playlists.length; i++)
        {
            var source = playlists[i]; // Grabs Playlist from array
            
            var ht = `<option value="${source.id}" data-description="${source.description}" data-image="${source.image}">${source.title}</option>`;
            $("#Plist").append(ht); //populate dropdown menu
            $("#Plist").on("change", selectPlaylist);
            
        }
    }

    function updateMenu() // Updates Dropdown Menu for Playlist to convert
    {
        playlists = [] // Empties array
        $("#Plist").empty(); // Empties dropdown menu
        Start() // Restarts function
        populateMenu(); // Populates dropdown menu
    }

    function onButtonClick()
    {
      console.log("button clicked");
      let music = MusicKit.getInstance();
  
      music.authorize()
      console.log("authorized");
      console.log("token is: " + token);
      
    }

    authorize();

    $("#Source").on("change", updateMenu);
    //$("#Plist").on("change", selectPlaylist);
    $("input[type=button]#Convert").on("click", convert);
    $("button#apple-music-authorize").on("click", onButtonClick);

});  // end of $(document).ready()