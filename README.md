# Spotify Recommendation Engine

This is the repository for the final project for the Master's level Data Mining course at The University of Chicago. We are building an application to recommend tracks and curate new Spotify playlists with a variety of machine learning methods in Python. We aim to answer the following three questions:

1. Could we define music genres using unsupervised machine learning/clustering techniques?
2. Could we create content-based recommendation engine based on a user's music profile?
3. What are potential applications of our models?

## Project scope

There are five sections in our project:

#### 1. **Data acquisition.**

 The data used for this project is collected over the Spotify API. We created a pipeline that (i) handles OAuth 2.0 authorization protocol, (ii) complies a comprehensive profile for the user for their own edification, (iii) collect audio features and analysis data on the tracks within the user profile, and (iv) pushes two playlists into the user's Spotify account: one that contains all tracks in the profile, another contains a random selection of tracks from both the user profile and from the Spotify library. The latter playlist is accompanied with a spreadsheet that allows a test user to label whether they approve of the song (both binary and on a 1-5 star scale).

 We also created a function that searches for and scrapes 180,000 tracks from Spotify's library. It also collects album, artist information, as well as relevant audio features and analysis for each track. This serves as the sample of the Spotify library on which our recommendation engine would operate.

#### 2. **Data preparation.**



#### 3. **Genre clustering.**



#### 4. **Data modelling.**



#### 5. **Playlist publication.**

From the models in Section 3 and 4, we output three themed playlists with 10 tracks each for each of the above methods: Dance (danceability score > 0.7), Chill (tempo < 95, valence > 0.5), and Discover Unpopular (popularity < 60, artist popularity < 80).

We have create a similar pipeline that takes the aforementioned playlists (stored as .csv files), (i) encodes the names of the playlists so the user/beta-tester does not know the theme or the method, (ii) creates playlists in the user's Spotify account, (iii) creates an encoding dictionary that allows the user to rate/comment on each of the playlists.

## Files:

There are a set of notebooks for each sections. Each notebook is self-contained. See above.


## Getting Started

A pair of Spotify API keys (Client ID and Client SECRET) are required to run the notebooks. Visit the [Developer Dashboard](https://developer.spotify.com/dashboard/) for more. Create a file `client_info.py` that defines the variables CLIENT_ID and CLIENT_SECRET.

## Team
- **Benedict Au** - [Github](https://github.com/benedictau1993/)
- **Julian Kleindiek** - [Github](https://github.com/ju-kl)
- **Yannik Kumar** - [Github](https://github.com/yannikkumar)
- **Glory Scheel** - [Github](https://github.com/glorysch)
- **Abhishek Yadav** - [Github](https://github.com/to-abhi-yadav)
