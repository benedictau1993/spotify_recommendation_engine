# Spotify Recommendation Engine

This is a work in progress for the Master's Data Mining course at the University of Chicago. We are building an application to curate new Spotify playlists with machine learning methods in Python and MySQL. We create a pipeline to compile user playback and library data through Spotify’s API with OAuth 2.0 authorization protocol. Then we predict the user’s affinity for songs in Spotify global library using clustering and neural network methods. Lastly, validate the model with user experimental trials and comparison against Spotify’s weekly recommended playlist.

## Files:

- `spotify_user_profile.py`: this script requests and wrangles the full user profile including playback and library data through the Spotify API and handles the OAuth 2.0 authorization protocol. Upon providing a Spotify API `Client ID`, it requests permissions from a target user, and requests their Spotify:
	- user profile
	- playback history (maximum history of 50)
	- list of public and private playlists
	- list of followed artists
	- list of top artists and tracks (within the recent month)
	- list of saved albums and tracks  

  Spotify API does not provide genres with albums as noted in [this thread on GitHub](https://github.com/spotify/web-api/issues/157). With the assumption that the artists album admits the same genre as the artist, the script populates the album genre field with the artist's genre. 
