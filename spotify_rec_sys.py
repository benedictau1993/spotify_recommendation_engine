def get_user_cleaned_tracks(tracks_df):
    # input: Julian's tracks pandas df
    # output: txt file with dicts that has track info
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
           
        # replace artist_info_dict with artist_info_dict
        
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