import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import requests
import json
import random
from random import choice, randrange
import urllib
import urllib.parse
from pprint import pprint
import webbrowser
import base64
from collections import MutableMapping 
import string
import os
import time
from math import floor

# Global variables
from client_info import * # .py file that includes CLIENT_ID and CLIENT_LIMIT

redirect_uri = "https://example.com/callback"
scopes_list = ["ugc-image-upload", 
    "user-read-playback-state", 
    "user-modify-playback-state", 
    "user-read-currently-playing", 
    "streaming", 
    "app-remote-control", 
    "user-read-email",                
    "user-read-private", 
    "playlist-read-collaborative", 
    "playlist-modify-public", 
    "playlist-read-private", 
    "playlist-modify-private", 
    "user-library-modify", 
    "user-library-read", 
    "user-top-read", 
    "user-read-recently-played", 
    "user-follow-read", 
    "user-follow-modify"
]
scope_string = '%20'.join(scopes_list)
# user_data_dict endpoint:"https://api.spotify.com/v1/me/"
user_data_dict = {
    "profile":"",
    "playlists":"playlists?limit=50",
    "top_artists":"top/artists?limit=50&time_range=short_term",
    "top_tracks":"top/tracks?limit=50&time_range=short_term",
    "followed_artists":"following?type=artist&limit=50",
    "recently_played":"player/recently-played?limit=50",
    "saved_albums":"albums?limit=50",
    "saved_tracks":"tracks?limit=50"
}

def convert_flatten(d, parent_key ='', sep ='_'):
    # flattens dict:input dict, returns dict
    items = [] 
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k 
        if isinstance(v, MutableMapping):
            items.extend(convert_flatten(v, new_key, sep = sep).items()) 
        else:
            items.append((new_key, v)) 
    return dict(items) 

def user_auth():
    # request user authorization and request refresh and access tokens
    options_dict = {"client_id":CLIENT_ID,
        "response_type":"code",
        "redirect_uri":urllib.parse.quote_plus(redirect_uri),
        "state":str(random.getrandbits(128)),
        "scope":scope_string,
        "show_dialog":"true"
        }
    endpoint = "https://accounts.spotify.com/authorize"
    r = requests.get(endpoint + "?" + "&".join([key + "=" + value for key, value in options_dict.items()]), allow_redirects=True)
    webbrowser.open(r.url) 
    callback_url = input("Enter the callback URL provided upon authentication: ")
    code = callback_url.strip("https://example.com/callback?code=").split("&state=")[0]
    state = callback_url.strip("https://example.com/callback?code=").split("&state=")[1]
    auth_str = '{}:{}'.format(CLIENT_ID, CLIENT_SECRET)
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    header = {'Authorization':'Basic {}'.format(b64_auth_str)}
    data = {
        'grant_type':'authorization_code',
        'code':code,
        'redirect_uri':redirect_uri
        }
    auth = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
    global auth_json
    auth_json = json.loads(auth.text)

def get_token(auth_json):
    # request new tokens using refresh_token
    client_auth_str = '{}:{}'.format(CLIENT_ID, CLIENT_SECRET)
    b64_client_auth_str = base64.b64encode(client_auth_str.encode()).decode()
    header = {'Authorization':'Basic {}'.format(b64_client_auth_str)}
    data = {"grant_type":"refresh_token", "refresh_token":auth_json["refresh_token"]}
    global refresh
    refresh = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
    refresh_json = json.loads(refresh.text)
    global refreshed_token
    refreshed_token = refresh_json["access_token"]

def get_user_data(user_element):
    # request an aspect of user data
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    endpoint = "https://api.spotify.com/v1/me/"
    url = endpoint + user_data_dict[user_element]
    user_info = requests.get(url=url, headers=headers)
    user_info_dict = json.loads(user_info.text)
    if "next" in user_info_dict and user_info_dict["next"] is not None:
        more_user_info_url = user_info_dict["next"] 
        while  more_user_info_url is not None:
            get_token(auth_json)
            # grab more user data if total > limit=50
            headers = {
                'Accept':'application/json',
                'Content-Type':'application/json',
                'Authorization':'Bearer {}'.format(refreshed_token)
                }
            more_user_info = requests.get(url=more_user_info_url, headers=headers) #
            more_user_info_dict = json.loads(more_user_info.text) # 
            more_user_info_url = more_user_info_dict["next"] #
            user_info_dict["items"].extend(more_user_info_dict["items"]) 
    return user_info_dict

def get_master_user_profile():
    # request all user data and assemble dict
    global master_user_profile
    master_user_profile = {key:get_user_data(key) for key in user_data_dict}

def clean_master_user_profile():
    # cleans master user profile dict
    profile = {
        key:val for key, val in master_user_profile["profile"].items() 
               if key in ["country", "explicit_content", "uri"]
    } 
    playlists = [
        {
            key:val for key, val in convert_flatten(playlist).items() 
            if key in ["description", "owner_display_name", "name", "uri"]
        } 
        for playlist in master_user_profile["playlists"]["items"]
    ]
    top_artists = [
        {
            key:val for key, val in convert_flatten(artist).items() 
            if key in ["genres", "name", "followers_total", "popularity", "uri"]
        } 
        for artist in master_user_profile["top_artists"]["items"]
    ]
    top_tracks = [
        {
            key:val for key, val in convert_flatten(track).items() 
            if key in [
                "album_release_date", "album_name", "album_uri", "artists", "duration_ms", 
                "explicit", "name", "popularity", "track_number", "uri"
            ]
        } 
        for track in master_user_profile["top_tracks"]["items"]
    ]
    for i in range(len(top_tracks)):
        top_tracks[i]["artist_name"] = top_tracks[i]["artists"][0]["name"]
        top_tracks[i]["artist_uri"] = top_tracks[i]["artists"][0]["uri"]
    top_tracks = [
        {
            key:val for key, val in track.items() 
            if key not in ["artists"]
        } 
        for track in top_tracks
    ]
    followed_artists = [
        {
            key:val for key, val in convert_flatten(artist).items() 
            if key in ["genres", "name", "followers_total", "popularity", "uri"]
        } 
        for artist in master_user_profile["top_artists"]["items"]
    ]
    recently_played = [
        {
            key:val for key, val in convert_flatten(track).items() 
            if key in [
                "track_album_release_date", "track_album_name", "track_album_uri", "track_artists", "track_duration_ms", 
                "track_explicit", "track_name", "track_popularity", "track_track_number", "track_uri", "played_at"
            ]
        } 
        for track in master_user_profile["recently_played"]["items"]
    ]
    for i in range(len(recently_played)):
        recently_played[i]["artist_name"] = recently_played[i]["track_artists"][0]["name"]
        recently_played[i]["artist_uri"] = recently_played[i]["track_artists"][0]["uri"]
    recently_played = [
        {
            key.replace('track_', ''):val for key, val in track.items() 
            if key not in ["track_artists"]
        } 
        for track in recently_played
    ]
    saved_albums = [
        {
            key:val for key, val in convert_flatten(track).items() 
            if key in ["added_at", "album_release_date", "album_name", "album_genres", 
                       "album_label", "album_popularity", "album_uri", "album_artists"
                      ]
        } 
        for track in master_user_profile["saved_albums"]["items"]
    ]
    for i in range(len(saved_albums)):
        saved_albums[i]["artist_name"] = saved_albums[i]["album_artists"][0]["name"]
        saved_albums[i]["artist_uri"] = saved_albums[i]["album_artists"][0]["uri"]
    saved_albums = [
        {
            key.replace('album_', ''):val 
            for key, val in album.items() if key not in ["album_artists"]
        } 
        for album in saved_albums
    ]
    saved_tracks = [
        {
            key:val for key, val in convert_flatten(track).items() 
            if key in [
                "added_at", "track_album_release_date", "track_album_name", "track_album_uri", "track_artists", "track_duration_ms", 
                "track_explicit", "track_name", "track_popularity", "track_track_number", "track_uri"]
        } 
        for track in master_user_profile["saved_tracks"]["items"]
    ]
    for i in range(len(saved_tracks)):
        saved_tracks[i]["artist_name"] = saved_tracks[i]["track_artists"][0]["name"]
        saved_tracks[i]["artist_uri"] = saved_tracks[i]["track_artists"][0]["uri"]
    
    saved_tracks = [
        {
            key.replace('track_', ''):val 
            for key, val in track.items() if key not in ["track_artists"]
        } 
        for track in saved_tracks
    ]
    global cleaned_master_user_profile
    cleaned_master_user_profile = {
        'profile':profile, 
        'playlists':playlists, 
        'top_artists':top_artists, 
        'top_tracks':top_tracks, 
        'followed_artists':followed_artists, 
        'recently_played':recently_played, 
        'saved_albums':saved_albums, 
        'saved_tracks':saved_tracks
    }

def populate_album_genres(cleaned_master_user_profile):
    # populates the list of saved_albums within cleaned_master_user_profile dict with
    # a list of the first artist's genres
    for album in cleaned_master_user_profile["saved_albums"]:
        get_token(auth_json)
        headers = {
            'Accept':'application/json',
            'Content-Type':'application/json',
            'Authorization':'Bearer {}'.format(refreshed_token)
            }
        album_endpoint = "https://api.spotify.com/v1/albums/"
        album_url = album_endpoint + album["uri"].split(":")[2]
        album_info = requests.get(url=album_url, headers=headers)
        album_info_dict = json.loads(album_info.text)
        album_artist_uri = album_info_dict["artists"][0]["uri"]
        artist_enpoint = "https://api.spotify.com/v1/artists/"
        artist_url = artist_enpoint + album_artist_uri.split(":")[2]
        artist_info =  requests.get(url=artist_url, headers=headers)
        artist_info_dict = json.loads(artist_info.text)
        artist_genres = artist_info_dict["genres"]
        album.update(genres = artist_genres) 

def get_categories_list():
    # request list of categories
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    endpoint = "https://api.spotify.com/v1/browse/categories?limit=50"
    url = endpoint
    categories = requests.get(url=url, headers=headers)
    categories_dict = json.loads(categories.text)
    if "next" in categories_dict and categories_dict["next"] is not None:
        more_categories_url = categories_dict["next"] 
        while  more_categories_url is not None:
            get_token(auth_json)
            # grab more categories if total > limit=50
            headers = {
                'Accept':'application/json',
                'Content-Type':'application/json',
                'Authorization':'Bearer {}'.format(refreshed_token)
                }
            more_categories = requests.get(url=more_categories_url, headers=headers) #
            more_categories_dict = json.loads(more_categories.text) # 
            more_categories_url = more_categories_dict["next"] 
            categories_dict["items"].extend(more_categories_dict["items"])
    global categories_list
    categories_list = [item["id"] for item in categories_dict["categories"]["items"]]

def get_genres_list():
    # request list of categories
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    endpoint = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    url = endpoint
    genres = requests.get(url=url, headers=headers)
    global genres_list
    genres_list = json.loads(genres.text)["genres"]
    
def get_random_track_info():
    # returns all relevant info of ONE song
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    search_endpoint = "https://api.spotify.com/v1/search"
    search_param = {
        "q":"%" + choice(string.ascii_letters) + "%",
        "type":"track",
        "market":"from_token",
        "limit":"1",
        "offset":str(randrange(5000)+1)
    }
    track_url = search_endpoint + "?" + "&".join([key+"="+val for key, val in search_param.items()])
    random_track = requests.get(url=track_url, headers=headers)
    global random_track_dict
    random_track_dict = json.loads(random_track.text)
    
    # get album info
    album_endpoint = "https://api.spotify.com/v1/albums/"
    album_url = album_endpoint + random_track_dict["tracks"]["items"][0]["album"]["uri"].split(":")[2]
    album_info = requests.get(url=album_url, headers=headers)
    album_info_dict = json.loads(album_info.text)
    
    # get artist info
    album_artist_uri = random_track_dict["tracks"]["items"][0]["artists"][0]["uri"]
    artist_enpoint = "https://api.spotify.com/v1/artists/"
    artist_url = artist_enpoint + album_artist_uri.split(":")[2]
    artist_info =  requests.get(url=artist_url, headers=headers)
    artist_info_dict = json.loads(artist_info.text)

    # get track audio features
    track_uri = random_track_dict["tracks"]["items"][0]["uri"].split(":")[2]
    audio_features_endpoint = "https://api.spotify.com/v1/audio-features/"
    audio_features_url = audio_features_endpoint + track_uri
    audio_features = requests.get(url=audio_features_url, headers=headers)
    global audio_features_dict
    audio_features_dict = json.loads(audio_features.text)
    
    # get track audio analysis
    audio_analysis_endpoint = "https://api.spotify.com/v1/audio-analysis/"
    audio_analysis_url = audio_analysis_endpoint + track_uri
    audio_analysis = requests.get(url=audio_analysis_url, headers=headers)
    global audio_analysis_dict
    audio_analysis_dict = json.loads(audio_analysis.text)    
    
    cleaned_random_track_dict = {
        "name":random_track_dict["tracks"]["items"][0]["name"],
        "uri":random_track_dict["tracks"]["items"][0]["uri"],
        "album_uri":random_track_dict["tracks"]["items"][0]["album"]["uri"],
        "album_label":album_info_dict["label"],
        "album_name":album_info_dict["name"],
        "album_popularity":album_info_dict["popularity"],
        "album_release_date":album_info_dict["release_date"],
        "artist_uri":random_track_dict["tracks"]["items"][0]["artists"][0]["uri"],
        "artist_name":artist_info_dict["name"],
        "artist_popularity":artist_info_dict["popularity"],
        "artist_followers":artist_info_dict["followers"]["total"],
        "duration_ms":random_track_dict["tracks"]["items"][0]["duration_ms"],
        "explicit":random_track_dict["tracks"]["items"][0]["explicit"],
        "popularity":random_track_dict["tracks"]["items"][0]["popularity"],
        "track_number":random_track_dict["tracks"]["items"][0]["track_number"],
        "genre":artist_info_dict["genres"],
        "acousticness":audio_features_dict["acousticness"],
        "danceability":audio_features_dict["danceability"],
        "energy":audio_features_dict["energy"],
        "instrumentalness":audio_features_dict["instrumentalness"],
        "liveness":audio_features_dict["liveness"],
        "loudness":audio_features_dict["loudness"],
        "speechiness":audio_features_dict["speechiness"],
        "valence":audio_features_dict["valence"],
        "tempo":audio_features_dict["tempo"],
        "tempo_confidence":audio_analysis_dict["track"]["tempo_confidence"],
        "overall_key":audio_features_dict["key"],
        "overall_key_confidence":audio_analysis_dict["track"]["key_confidence"],
        "mode":audio_features_dict["mode"],
        "mode_confidence":audio_analysis_dict["track"]["mode_confidence"],
        "time_signature":audio_features_dict["time_signature"],
        "time_signature_confidence":audio_analysis_dict["track"]["time_signature_confidence"],
        "num_of_sections":len(audio_analysis_dict["sections"]),
        "section_durations":[section["duration"] for section in audio_analysis_dict["sections"]],
        "section_loudnesses":[section["loudness"] for section in audio_analysis_dict["sections"]],
        "section_tempos":[section["tempo"] for section in audio_analysis_dict["sections"]],
        "section_tempo_confidences":[section["tempo_confidence"] for section in audio_analysis_dict["sections"]],
        "num_of_keys":len(set([section["key"] for section in audio_analysis_dict["sections"]])),
        "section_keys":[section["key"] for section in audio_analysis_dict["sections"]],
        "section_key_confidences":[section["key_confidence"] for section in audio_analysis_dict["sections"]],
        "num_of_modes":len(set([section["mode"] for section in audio_analysis_dict["sections"]])),
        "section_modes":[section["mode"] for section in audio_analysis_dict["sections"]],
        "section_mode_confidences":[section["mode_confidence"] for section in audio_analysis_dict["sections"]],
        "num_of_time_signatures": len(set([section["time_signature"] for section in audio_analysis_dict["sections"]])),
        "section_time_signatures":[section["time_signature"] for section in audio_analysis_dict["sections"]],
        "section_time_signature_confidences":[section["time_signature_confidence"] for section in audio_analysis_dict["sections"]]
    }
    return cleaned_random_track_dict

def get_20_random_tracks_info(requests_counter_init):
    # returns all relevant info of TWENTY songs
    get_token(auth_json)
    requests_counter = 0 + requests_counter_init
    requests_counter += 1
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    search_endpoint = "https://api.spotify.com/v1/search"
    search_param = {
        "q":"%" + choice(string.ascii_letters) + "%",
        "type":"track",
        "market":"from_token",
        "limit":"20",
        "offset":str(randrange(4980))
    }
    global track_url
    track_url = search_endpoint + "?" + "&".join([key+"="+val for key, val in search_param.items()])
    global random_track
    random_track = requests.get(url=track_url, headers=headers)
    requests_counter += 1
    if random_track.status_code != 200:
        print("Exception: Response", random_track.status_code, "at requests_counter =", requests_counter, "at random_track")
        print("Track url in question:", track_url)
        print(json.loads(random_track.text))
        raise
    global random_track_dict
    random_track_dict = json.loads(random_track.text)
    # get album info
    album_endpoint = "https://api.spotify.com/v1/albums/"
    album_uri_string = ",".join([track["album"]["uri"].split(":")[2] for track in random_track_dict["tracks"]["items"]])
    album_url = album_endpoint + "?ids=" + album_uri_string
    global album_info
    album_info = requests.get(url=album_url, headers=headers)
    requests_counter += 1
    if album_info.status_code != 200:
        print("Exception: Response", album_info.status_code, "at requests_counter =", requests_counter, "at album_info")
        raise
    global album_info_dict
    album_info_dict = json.loads(album_info.text)
    # get artist info
    artist_enpoint = "https://api.spotify.com/v1/artists/"
    artist_uri_string = ",".join([track["artists"][0]["uri"].split(":")[2] for track in random_track_dict["tracks"]["items"]])
    artist_url = artist_enpoint + "?ids=" + artist_uri_string
    global artist_info
    artist_info =  requests.get(url=artist_url, headers=headers)
    requests_counter += 1
    if artist_info.status_code != 200:
        print("Exception: Response", artist_info.status_code, "at requests_counter =", requests_counter, "at artist_info")
        raise
    global artist_info_dict
    artist_info_dict = json.loads(artist_info.text)
    # get track audio features
    audio_features_endpoint = "https://api.spotify.com/v1/audio-features/"
    global track_uri_string
    track_uri_string = ",".join([track["uri"].split(":")[2] for track in random_track_dict["tracks"]["items"]])
    audio_features_url = audio_features_endpoint + "?ids=" + track_uri_string
    global audio_features
    audio_features = requests.get(url=audio_features_url, headers=headers)
    requests_counter += 1
    if audio_features.status_code != 200:
        print("Exception: Response", audio_features.status_code, "at requests_counter =", requests_counter, "at audio_features")
        raise
    global audio_features_dict
    audio_features_dict = json.loads(audio_features.text)
  
    cleaned_20_random_track_dicts_list = []
    for i in range(20):
        # get track audio analysis
        audio_analysis_endpoint = "https://api.spotify.com/v1/audio-analysis/"
        audio_analysis_url = audio_analysis_endpoint + track_uri_string.split(",")[i]
        global audio_analysis
        audio_analysis = requests.get(url=audio_analysis_url, headers=headers)
        requests_counter += 1
        global audio_analysis_dict
        if audio_analysis.status_code == 404:
            audio_analysis_dict = None
        elif audio_analysis.status_code == 429:
            print("Exception: Response", audio_analysis.status_code, "at requests_counter =", requests_counter, "at audio_analysis, with track_uri =", track_uri_string.split(",")[i])
            raise
        else: 
            audio_analysis_dict = json.loads(audio_analysis.text)  
        
        cleaned_random_track_dict = {
            "name":random_track_dict["tracks"]["items"][i]["name"],
            "uri":random_track_dict["tracks"]["items"][i]["uri"],
            "album_uri":random_track_dict["tracks"]["items"][i]["album"]["uri"],
            "album_label":album_info_dict["albums"][i]["label"],
            "album_name":album_info_dict["albums"][i]["name"],
            "album_popularity":album_info_dict["albums"][i]["popularity"],
            "album_release_date":album_info_dict["albums"][i]["release_date"],
            "artist_uri":random_track_dict["tracks"]["items"][i]["artists"][0]["uri"],
            "artist_name":artist_info_dict["artists"][i]["name"],
            "artist_popularity":artist_info_dict["artists"][i]["popularity"],
            "artist_followers":artist_info_dict["artists"][i]["followers"]["total"],
            "duration_ms":random_track_dict["tracks"]["items"][i]["duration_ms"],
            "explicit":random_track_dict["tracks"]["items"][i]["explicit"],
            "popularity":random_track_dict["tracks"]["items"][i]["popularity"],
            "track_number":random_track_dict["tracks"]["items"][i]["track_number"],
            "genre":artist_info_dict["artists"][i]["genres"],
            "acousticness":audio_features_dict["audio_features"][i]["acousticness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "danceability":audio_features_dict["audio_features"][i]["danceability"] if audio_features_dict["audio_features"][i] is not None else "None",
            "energy":audio_features_dict["audio_features"][i]["energy"] if audio_features_dict["audio_features"][i] is not None else "None",
            "instrumentalness":audio_features_dict["audio_features"][i]["instrumentalness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "liveness":audio_features_dict["audio_features"][i]["liveness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "loudness":audio_features_dict["audio_features"][i]["loudness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "speechiness":audio_features_dict["audio_features"][i]["speechiness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "valence":audio_features_dict["audio_features"][i]["valence"] if audio_features_dict["audio_features"][i] is not None else "None",
            "tempo":audio_features_dict["audio_features"][i]["tempo"] if audio_features_dict["audio_features"][i] is not None else "None",
            "tempo_confidence":audio_analysis_dict["track"]["tempo_confidence"] if audio_analysis_dict is not None else "None",
            "overall_key":audio_features_dict["audio_features"][i]["key"] if audio_features_dict["audio_features"][i] is not None else "None",
            "overall_key_confidence":audio_analysis_dict["track"]["key_confidence"] if audio_analysis_dict is not None else "None",
            "mode":audio_features_dict["audio_features"][i]["mode"] if audio_features_dict["audio_features"][i] is not None else "None",
            "mode_confidence":audio_analysis_dict["track"]["mode_confidence"] if audio_analysis_dict is not None else "None",
            "time_signature":audio_features_dict["audio_features"][i]["time_signature"] if audio_features_dict["audio_features"][i] is not None else "None",
            "time_signature_confidence":audio_analysis_dict["track"]["time_signature_confidence"] if audio_analysis_dict is not None else "None",
            "num_of_sections":len(audio_analysis_dict["sections"]) if audio_analysis_dict is not None else "None",
            "section_durations":[section["duration"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_loudnesses":[section["loudness"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_tempos":[section["tempo"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_tempo_confidences":[section["tempo_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_keys":len(set([section["key"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_keys":[section["key"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_key_confidences":[section["key_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_modes":len(set([section["mode"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_modes":[section["mode"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_mode_confidences":[section["mode_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_time_signatures":len(set([section["time_signature"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_time_signatures":[section["time_signature"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_time_signature_confidences":[section["time_signature_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None"
        }
        cleaned_20_random_track_dicts_list.append(cleaned_random_track_dict)
        
    return requests_counter, cleaned_20_random_track_dicts_list


def run_get_20_random_tracks_info():
    print("Sampling tracks from Spotify's library:\n")
    start_time = time.time()
    requests_counter_init = 0
    tracks_collection = []
    i = 0
    while True:
        split_time = time.time()
        print("\033[FIteration:", i, "    Sampled Tracks:", i*20, "    Total Requests:", requests_counter_init, "    Runtime (min):", floor((split_time - start_time)/60))
        requests_counter_init, tracks_info = get_20_random_tracks_info(requests_counter_init)
        with open('scraped_tracks.txt', 'a') as f:
            for item in tracks_info:
                f.write("%s\n" % item)
        i += 1

def scrape_search_tracks_info(requests_counter_init, alphanum, offset):
    # returns all relevant info of TWENTY songs
    get_token(auth_json)
    requests_counter = 0 + requests_counter_init
    requests_counter += 1
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    search_endpoint = "https://api.spotify.com/v1/search"
    search_param = {
        "q":alphanum,
        "type":"track",
        "market":"from_token",
        "limit":"20",
        "offset":offset
    }
    global track_url
    track_url = search_endpoint + "?" + "&".join([key+"="+val for key, val in search_param.items()])
    global random_track
    random_track = requests.get(url=track_url, headers=headers)
    requests_counter += 1
    if random_track.status_code != 200:
        print("Exception: Response", random_track.status_code, "at requests_counter =", requests_counter, "at random_track")
        print("Track url in question:", track_url)
        print(json.loads(random_track.text))
        raise
    global random_track_dict
    random_track_dict = json.loads(random_track.text)
    # get album info
    album_endpoint = "https://api.spotify.com/v1/albums/"
    album_uri_string = ",".join([track["album"]["uri"].split(":")[2] for track in random_track_dict["tracks"]["items"]])
    album_url = album_endpoint + "?ids=" + album_uri_string
    global album_info
    album_info = requests.get(url=album_url, headers=headers)
    requests_counter += 1
    if album_info.status_code != 200:
        print("Exception: Response", album_info.status_code, "at requests_counter =", requests_counter, "at album_info")
        raise
    global album_info_dict
    album_info_dict = json.loads(album_info.text)
    # get artist info
    artist_enpoint = "https://api.spotify.com/v1/artists/"
    artist_uri_string = ",".join([track["artists"][0]["uri"].split(":")[2] for track in random_track_dict["tracks"]["items"]])
    artist_url = artist_enpoint + "?ids=" + artist_uri_string
    global artist_info
    artist_info =  requests.get(url=artist_url, headers=headers)
    requests_counter += 1
    if artist_info.status_code != 200:
        print("Exception: Response", artist_info.status_code, "at requests_counter =", requests_counter, "at artist_info")
        raise
    global artist_info_dict
    artist_info_dict = json.loads(artist_info.text)
    # get track audio features
    audio_features_endpoint = "https://api.spotify.com/v1/audio-features/"
    global track_uri_string
    track_uri_string = ",".join([track["uri"].split(":")[2] for track in random_track_dict["tracks"]["items"]])
    audio_features_url = audio_features_endpoint + "?ids=" + track_uri_string
    global audio_features
    audio_features = requests.get(url=audio_features_url, headers=headers)
    requests_counter += 1
    if audio_features.status_code != 200:
        print("Exception: Response", audio_features.status_code, "at requests_counter =", requests_counter, "at audio_features")
        raise
    global audio_features_dict
    audio_features_dict = json.loads(audio_features.text)
  
    cleaned_20_random_track_dicts_list = []
    for i in range(20):
        # get track audio analysis
        audio_analysis_endpoint = "https://api.spotify.com/v1/audio-analysis/"
        audio_analysis_url = audio_analysis_endpoint + track_uri_string.split(",")[i]
        global audio_analysis
        audio_analysis = requests.get(url=audio_analysis_url, headers=headers)
        requests_counter += 1
        global audio_analysis_dict
        if audio_analysis.status_code == 404:
            audio_analysis_dict = None
        elif audio_analysis.status_code == 429:
            print("Exception: Response", audio_analysis.status_code, "at requests_counter =", requests_counter, "at audio_analysis, with track_uri =", track_uri_string.split(",")[i])
            raise
        else: 
            audio_analysis_dict = json.loads(audio_analysis.text)  
        
        cleaned_random_track_dict = {
            "name":random_track_dict["tracks"]["items"][i]["name"],
            "uri":random_track_dict["tracks"]["items"][i]["uri"],
            "album_uri":random_track_dict["tracks"]["items"][i]["album"]["uri"],
            "album_label":album_info_dict["albums"][i]["label"],
            "album_name":album_info_dict["albums"][i]["name"],
            "album_popularity":album_info_dict["albums"][i]["popularity"],
            "album_release_date":album_info_dict["albums"][i]["release_date"],
            "artist_uri":random_track_dict["tracks"]["items"][i]["artists"][0]["uri"],
            "artist_name":artist_info_dict["artists"][i]["name"],
            "artist_popularity":artist_info_dict["artists"][i]["popularity"],
            "artist_followers":artist_info_dict["artists"][i]["followers"]["total"],
            "duration_ms":random_track_dict["tracks"]["items"][i]["duration_ms"],
            "explicit":random_track_dict["tracks"]["items"][i]["explicit"],
            "popularity":random_track_dict["tracks"]["items"][i]["popularity"],
            "track_number":random_track_dict["tracks"]["items"][i]["track_number"],
            "genre":artist_info_dict["artists"][i]["genres"],
            "acousticness":audio_features_dict["audio_features"][i]["acousticness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "danceability":audio_features_dict["audio_features"][i]["danceability"] if audio_features_dict["audio_features"][i] is not None else "None",
            "energy":audio_features_dict["audio_features"][i]["energy"] if audio_features_dict["audio_features"][i] is not None else "None",
            "instrumentalness":audio_features_dict["audio_features"][i]["instrumentalness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "liveness":audio_features_dict["audio_features"][i]["liveness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "loudness":audio_features_dict["audio_features"][i]["loudness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "speechiness":audio_features_dict["audio_features"][i]["speechiness"] if audio_features_dict["audio_features"][i] is not None else "None",
            "valence":audio_features_dict["audio_features"][i]["valence"] if audio_features_dict["audio_features"][i] is not None else "None",
            "tempo":audio_features_dict["audio_features"][i]["tempo"] if audio_features_dict["audio_features"][i] is not None else "None",
            "tempo_confidence":audio_analysis_dict["track"]["tempo_confidence"] if audio_analysis_dict is not None else "None",
            "overall_key":audio_features_dict["audio_features"][i]["key"] if audio_features_dict["audio_features"][i] is not None else "None",
            "overall_key_confidence":audio_analysis_dict["track"]["key_confidence"] if audio_analysis_dict is not None else "None",
            "mode":audio_features_dict["audio_features"][i]["mode"] if audio_features_dict["audio_features"][i] is not None else "None",
            "mode_confidence":audio_analysis_dict["track"]["mode_confidence"] if audio_analysis_dict is not None else "None",
            "time_signature":audio_features_dict["audio_features"][i]["time_signature"] if audio_features_dict["audio_features"][i] is not None else "None",
            "time_signature_confidence":audio_analysis_dict["track"]["time_signature_confidence"] if audio_analysis_dict is not None else "None",
            "num_of_sections":len(audio_analysis_dict["sections"]) if audio_analysis_dict is not None else "None",
            "section_durations":[section["duration"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_loudnesses":[section["loudness"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_tempos":[section["tempo"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_tempo_confidences":[section["tempo_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_keys":len(set([section["key"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_keys":[section["key"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_key_confidences":[section["key_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_modes":len(set([section["mode"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_modes":[section["mode"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_mode_confidences":[section["mode_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_time_signatures":len(set([section["time_signature"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_time_signatures":[section["time_signature"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_time_signature_confidences":[section["time_signature_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None"
        }
        cleaned_20_random_track_dicts_list.append(cleaned_random_track_dict)
    return requests_counter, cleaned_20_random_track_dicts_list

def run_scrape_search_tracks_info():
    print("Sampling tracks from Spotify's library:\n")
    alphanums = (string.ascii_lowercase + string.digits)
    offsets = list(map(str, np.arange(0,5000, 20).tolist())) 
    requests_counter_init = 0
    start_time = time.time()
    i = 0
    counter = 0
    tracks_collection = []
    for alphanum in alphanums:
        for offset in offsets: 
            split_time = time.time()
            requests_counter_init, tracks_info = scrape_search_tracks_info(requests_counter_init, alphanum, offset)
            counter += len_random_track_list
            print("\033[FIteration:", i, alphanum, offset, 
                  "  Sampled Tracks:", counter, 
                  "  Total Requests:", requests_counter_init, 
                  "  Runtime (min):", floor((split_time - start_time)/60)
                 )
            with open('scraped_search_tracks.txt', 'a') as f:
                for item in tracks_info:
                    f.write("%s\n" % item)
            i += 1

def read_row_dicts(file):
    # reads text file with a dictionaries separated with "\n"
    # all dicts have same keys; outputs pandas df
    # 100 MB data (54K x46 col)
    import ast 
    with open(file, encoding='utf-8') as f:
        line = f.readline()
        keys = list(ast.literal_eval(line.rstrip("\n")).keys())
        data_list = []
        while line:
            data_list.append(list(ast.literal_eval(line.rstrip("\n")).values()))
            line = f.readline()
    df = pd.DataFrame(data_list, columns=keys)  
    return df

def my_tracks_uri():
    # grabs the uris from top_tracks, saved_tracks, and recently_played and puts them into a dataframe
    # prerequisite is that the object clean_master_user_profile is loaded in the kernel prior to runing this function
    # initiate lists
    top_tracks = []
    saved_tracks = []
    recently_played = []
    # pull top_tracks
    for i in range(len(cleaned_master_user_profile["top_tracks"])):
        top_tracks.append(cleaned_master_user_profile["top_tracks"][i]["uri"])
    # pull saved_tracks
    for i in range(len(cleaned_master_user_profile["saved_tracks"])):
        saved_tracks.append(cleaned_master_user_profile["saved_tracks"][i]["uri"])    
    # pull recently_played
    for i in range(len(cleaned_master_user_profile["recently_played"])):
        recently_played.append(cleaned_master_user_profile["recently_played"][i]["uri"])
    # create dataframe for top_tracks
    top_tracks_df = pd.DataFrame(top_tracks)
    top_tracks_df = top_tracks_df.rename(columns = {0:"uri"})
    top_tracks_df["type"] = "top_tracks"
    # create dataframe for saved_tracks
    saved_tracks_df = pd.DataFrame(saved_tracks)
    saved_tracks_df = saved_tracks_df.rename(columns = {0:"uri"})
    saved_tracks_df["type"] = "saved_tracks"
    # create dataframe for saved_tracks
    recently_played_df = pd.DataFrame(recently_played)
    recently_played_df = recently_played_df.rename(columns = {0:"uri"})
    recently_played_df["type"] = "recently_played"
    # concat dataframes
    global tracks_df
    tracks_df = pd.concat([top_tracks_df, saved_tracks_df, recently_played_df], axis = 0)
    # get dummies from type
    tracks_df = pd.concat([tracks_df.drop("type", axis = 1), pd.get_dummies(tracks_df["type"])], axis = 1)
    # reset the index
    tracks_df = tracks_df.reset_index(drop=True)
    # print result
    # print("The dataframe tracks is loaded into your kernel now and looks like this:", "\n", tracks_df.head())

def get_user_cleaned_tracks():
    # input: Julian's tracks pandas df
    # output: txt file with dicts that has track info
    global user_cleaned_tracks_fname
    user_cleaned_tracks_fname = "user_cleaned_tracks.txt"
    tracks_uri_list = [track.split(':')[2] for track in list(tracks_df["uri"].values)]
    
    for track in tracks_uri_list:
        global track_uri
        track_uri = track
        get_token(auth_json)
        headers = {
            'Accept':'application/json',
            'Content-Type':'application/json',
            'Authorization':'Bearer {}'.format(refreshed_token)
            }
        # get track info 
        track_endpoint = "https://api.spotify.com/v1/tracks/"
        track_uri_string = track_uri
        track_url = track_endpoint + track_uri_string
        global track_info
        track_info = requests.get(url=track_url, headers=headers)
        if track_info.status_code != 200:
            print("Exception: Response", track_info.status_code, "at track_info")
            raise
        track_info_dict = json.loads(track_info.text)
        global album_uri
        album_uri = track_info_dict["album"]["uri"].split(':')[2]
        artist_uri = track_info_dict["artists"][0]["uri"].split(':')[2]

        # get album info        
        album_endpoint = "https://api.spotify.com/v1/albums/"
        album_uri_string = album_uri
        album_url = album_endpoint + album_uri_string
        album_info = requests.get(url=album_url, headers=headers)
        if album_info.status_code != 200:
            print("Exception: Response", album_info.status_code, "at album_info")
            raise
        album_info_dict = json.loads(album_info.text)

        # get artist info
        artist_enpoint = "https://api.spotify.com/v1/artists/"
        artist_uri_string = artist_uri
        artist_url = artist_enpoint + artist_uri_string
        global artist_info
        artist_info =  requests.get(url=artist_url, headers=headers)
        if artist_info.status_code != 200:
            print("Exception: Response", artist_info.status_code, "at artist_info")
            raise
        artist_info_dict = json.loads(artist_info.text)

        # get track audio features
        audio_features_endpoint = "https://api.spotify.com/v1/audio-features/"
        track_uri_string = track_uri
        audio_features_url = audio_features_endpoint + track_uri_string
        audio_features = requests.get(url=audio_features_url, headers=headers)
        if audio_features.status_code != 200:
            print("Exception: Response", audio_features.status_code, "at audio_features")
            raise
        audio_features_dict = json.loads(audio_features.text)
              
        # get track audio analysis
        audio_analysis_endpoint = "https://api.spotify.com/v1/audio-analysis/"
        audio_analysis_url = audio_analysis_endpoint + track_uri
        audio_analysis = requests.get(url=audio_analysis_url, headers=headers)
        if audio_analysis.status_code == 404:
            audio_analysis_dict = None
        elif audio_analysis.status_code == 429:
            print("Exception: Response", audio_analysis.status_code, "at audio_analysis, with track_uri =", track_uri_string.split(",")[i])
            raise
        else: 
            audio_analysis_dict = json.loads(audio_analysis.text) 
             
        cleaned_track_dict = {
            "name":track_info_dict["name"],
            "uri":track_info_dict["uri"],
            "album_uri":track_info_dict["album"]["uri"],
            "album_label":album_info_dict["label"],
            "album_name":album_info_dict["name"],
            "album_popularity":album_info_dict["popularity"],
            "album_release_date":album_info_dict["release_date"],
            "artist_uri":track_info_dict["artists"][0]["uri"],
            "artist_name":artist_info_dict["name"],
            "artist_popularity":artist_info_dict["popularity"],
            "artist_followers":artist_info_dict["followers"]["total"],
            "duration_ms":track_info_dict["duration_ms"],
            "explicit":track_info_dict["explicit"],
            "popularity":track_info_dict["popularity"],
            "track_number":track_info_dict["track_number"],
            "genre":artist_info_dict["genres"],
            "acousticness":audio_features_dict["acousticness"] if audio_features_dict is not None else "None",
            "danceability":audio_features_dict["danceability"] if audio_features_dict is not None else "None",
            "energy":audio_features_dict["energy"] if audio_features_dict is not None else "None",
            "instrumentalness":audio_features_dict["instrumentalness"] if audio_features_dict is not None else "None",
            "liveness":audio_features_dict["liveness"] if audio_features_dict is not None else "None",
            "loudness":audio_features_dict["loudness"] if audio_features_dict is not None else "None",
            "speechiness":audio_features_dict["speechiness"] if audio_features_dict is not None else "None",
            "valence":audio_features_dict["valence"] if audio_features_dict is not None else "None",
            "tempo":audio_features_dict["tempo"] if audio_features_dict is not None else "None",
            "tempo_confidence":audio_analysis_dict["track"]["tempo_confidence"] if audio_analysis_dict is not None else "None",
            "overall_key":audio_features_dict["key"] if audio_features_dict is not None else "None",
            "overall_key_confidence":audio_analysis_dict["track"]["key_confidence"] if audio_analysis_dict is not None else "None",
            "mode":audio_features_dict["mode"] if audio_features_dict is not None else "None",
            "mode_confidence":audio_analysis_dict["track"]["mode_confidence"] if audio_analysis_dict is not None else "None",
            "time_signature":audio_features_dict["time_signature"] if audio_features_dict is not None else "None",
            "time_signature_confidence":audio_analysis_dict["track"]["time_signature_confidence"] if audio_analysis_dict is not None else "None",
            "num_of_sections":len(audio_analysis_dict["sections"]) if audio_analysis_dict is not None else "None",
            "section_durations":[section["duration"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_loudnesses":[section["loudness"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_tempos":[section["tempo"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_tempo_confidences":[section["tempo_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_keys":len(set([section["key"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_keys":[section["key"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_key_confidences":[section["key_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_modes":len(set([section["mode"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_modes":[section["mode"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_mode_confidences":[section["mode_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "num_of_time_signatures":len(set([section["time_signature"] for section in audio_analysis_dict["sections"]])) if audio_analysis_dict is not None else "None",
            "section_time_signatures":[section["time_signature"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None",
            "section_time_signature_confidences":[section["time_signature_confidence"] for section in audio_analysis_dict["sections"]] if audio_analysis_dict is not None else "None"
        }
        
        with open('user_cleaned_tracks.txt', 'a') as f:
            f.write("%s\n" % cleaned_track_dict)

def make_user_profile_spotify_playlist():
    user_auth()
    get_token(auth_json)
    get_master_user_profile()
    clean_master_user_profile()
    print("Acquired your Spotify user profile.")
    my_tracks_uri()
    print("Your Spotify user profile has {} featured tracks.".format(len(tracks_df)))
    print("Collecting audio features and audio analysis metadata to your favourite tracks. This should should take less than {} minutes.".format(round(len(tracks_df)*1.5/60)))
    get_user_cleaned_tracks()
    print("Collected all audio features and audio analysis metadata to your favourite tracks.")
    print("Your user profile is saved as 'user_cleaned_tracks.txt'.")
    global master_featured_tracks 
    master_featured_tracks = read_row_dicts(user_cleaned_tracks_fname)
    print("Your user profile is loaded as a pandas df 'master_featured_tracks'.")    
    master_featured_tracks_uri_list = list(master_featured_tracks["uri"].values)
    len_master_featured_tracks_uri_list = len(master_featured_tracks_uri_list)
    user_id = cleaned_master_user_profile["profile"]["uri"].split(":")[2]
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    create_playlist_endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
    create_playlist_param = {
        "name":"MyFeaturedTracks",
        "description":"BA@UChicagoMSCA"
    }
    create_playlist = requests.post(create_playlist_endpoint, headers=headers, data=json.dumps(create_playlist_param))
    create_playlist_dict = json.loads(create_playlist.text)
    created_playlist_uri = create_playlist_dict["uri"].split(":")[2]  
    master_featured_tracks_uri_list_chunks = [master_featured_tracks_uri_list[i*50:(i+1)* 50] 
            for i in range((len(master_featured_tracks_uri_list)+50-1)//50)
    ]
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    add_tracks_to_playlist_endpoint = "https://api.spotify.com/v1/playlists/{}/tracks".format(created_playlist_uri)
    for chunk in master_featured_tracks_uri_list_chunks:
        add_tracks_param = {
                "uris":chunk
        }
        add_tracks = requests.post(add_tracks_to_playlist_endpoint, headers=headers, data=json.dumps(add_tracks_param))
        add_tracks_dict = json.loads(add_tracks.text)

    # create playlist of 400 songs, with max 200 random songs from user profile, and 400-max(200) random songs from global playlist
    # then shuffle, then push into a another new playlist
    global_song_list = read_row_dicts("scraped_search_tracks.txt")
    # get total of 400 songs
    if len_master_featured_tracks_uri_list > 100:
        master_featured_tracks_sample = master_featured_tracks.sample(n = 100) 
        global_song_list_sample = global_song_list.sample(n = 300) 
        combined_sample = pd.concat([master_featured_tracks_sample, global_song_list_sample], sort=False).sample(frac=1).reset_index(drop=True)
    else: 
        master_featured_tracks_sample = master_featured_tracks.sample(n = len_master_featured_tracks_uri_list) 
        global_song_list_sample = global_song_list.sample(n = 400-len_master_featured_tracks_uri_list) 
        combined_sample = pd.concat([master_featured_tracks_sample, global_song_list_sample], sort=False).sample(frac=1).reset_index(drop=True)
    combined_sample_uri_list = list(combined_sample["uri"].values)

    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    create_playlist_endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
    create_playlist_param = {
        "name":"TestSample",
        "description":"BA@UChicagoMSCA"
    }
    create_playlist = requests.post(create_playlist_endpoint, headers=headers, data=json.dumps(create_playlist_param))
    create_playlist_dict = json.loads(create_playlist.text)
    created_playlist_uri = create_playlist_dict["uri"].split(":")[2]  

    combined_sample_uri_list_chunks = [combined_sample_uri_list[i*50:(i+1)* 50] 
            for i in range((len(combined_sample_uri_list)+50-1)//50)
    ]
    get_token(auth_json)
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization':'Bearer {}'.format(refreshed_token)
        }
    add_tracks_to_playlist_endpoint = "https://api.spotify.com/v1/playlists/{}/tracks".format(created_playlist_uri)
    for chunk in combined_sample_uri_list_chunks:
        add_tracks_param = {
                "uris":chunk
        }
        add_tracks = requests.post(add_tracks_to_playlist_endpoint, headers=headers, data=json.dumps(add_tracks_param))
        add_tracks_dict = json.loads(add_tracks.text)

    combined_sample["recently_played"] = [uri in list(tracks_df.loc[tracks_df["recently_played"]==1]["uri"].values) for uri in combined_sample["uri"]]
    combined_sample["saved_tracks"] = [uri in list(tracks_df.loc[tracks_df["saved_tracks"]==1]["uri"].values) for uri in combined_sample["uri"]]
    combined_sample["top_tracks"] = [uri in list(tracks_df.loc[tracks_df["top_tracks"]==1]["uri"].values) for uri in combined_sample["uri"]]    

    combined_sample["Rating01"] = None
    combined_sample["Rating0-5"] = None
    combined_sample.to_csv("combined_sample.csv")

