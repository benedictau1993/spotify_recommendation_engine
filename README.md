# Flexible content-based music recommendations using Spotify

[![School](https://img.shields.io/badge/UChicago-MSCA-red)]() [![Course](https://img.shields.io/badge/Course-DataMining-lightgray)]()  [![Contributors](https://img.shields.io/badge/Contributors-5-green)]() [![Repo Size](https://img.shields.io/github/commit-activity/y/benedictau1993/spotify_recommendation_engine.svg)]()

### *Tapping into the streaming giant’s wealth of data to create personal, configurable recommender systems*


This is the repository for the final project for the Master's level Data Mining course at The University of Chicago. We are building an application to recommend tracks and curate new Spotify playlists with a variety of machine learning methods in Python. We aim to answer the following three questions:

1. Could we define music genres using unsupervised machine learning/clustering techniques?
2. Could we create content-based recommendation engine based on a user's music profile?
3. What are potential applications of our models?

## Project scope

There are five sections in our project:

#### 1. **Data acquisition.**

 The data used for this project is collected over the Spotify API. We created a pipeline that (i) handles OAuth 2.0 authorization protocol, (ii) complies a comprehensive profile for the user for their own edification, (iii) collect audio features and analysis data on the tracks within the user profile, and (iv) pushes two playlists into the user's Spotify account: one that contains all tracks in the profile, another contains a random selection of tracks from both the user profile and from the Spotify library. The latter playlist is accompanied with a spreadsheet that allows a test user to label whether they approve of the song (both binary and on a 1-5 star scale).

 We also created a function that searches for and scrapes 180,000 tracks from Spotify's library. It also collects album, artist information, as well as relevant audio features and analysis for each track. This serves as the sample of the Spotify library on which our recommendation engine would operate.

#### 2. **Data preparation & feature engineering.**

As a first step, we concatenate tracks collected from the user profile with tracks scraped from the Spotify library. Spotify provides their data in a rather clean format, so that data cleaning is limited to dropping duplicate tracks and unnecessary features as well as converting features to the appropriate data types. We decided to drop rows with missing data, given the limited number of missing values in relation to our dataset.

This notebook also covers functions we developed for feature engineering such as categorizing the album label, transforming the release date, converting duration to minutes, and extracting section values. Spotify provides genre information on a very granular level. In order for us to be able to validate our clusters later in the analysis, we had to aggregate those sub-genres into higher-level genres. In order to do so, we converted the list of sub-genres into a string, applied the TdidfVectorizer on the string, reduced the dimensionality of the resulting matrix applying TruncatedSVD, and finally clustered the resulting data using K-Means into 13 genres.

Because our dataset consists of data from multiple users, we wrote a function to drop remaining duplicates specifying a target user. As a final step, dummy variables are created for all categorical features.

#### 3. **Clustering for Genre Creation.**

The purpose of this notebook is to apply different clustering techniques to create clusters based on the audio features of tracks to define and validate music genres. We apply techniques such as t-SNE, DBSCAN, Agglomerative Clustering, and K-Means, explore their respective results, and finally evaluate their performance and applicability for our business problem.

#### 4. **Data modelling.**

For our recommendation systems, we approach the problem from four different angles.
1. Classification models

    Using classification modelling this notebook explores the predictive power of Spotify track features using labeled data, whether the user liked the song or not. After picking the model with the best testing and cross validation score we can:
    - predict whether the user would like a song or not and give the probability of the user liking or disliking the song, on some global data frame.
    - create three playlists of songs we predict the user will like
    - each playlist is under a "theme" or mood that is determined by audio features such as tempo, etc.

2. Regression models
    This notebook trains classical, tree-based, bagging and boosting regression models using a user rated playlist and predicts reviews on a global Spotify dataset to further create playlists based on audio attributes.

3. Track-based recommendation system

    This notebook contains a function generating themed playlists based on songs a user likes or has listened to in the past. The function offers the user the ability to take the following approaches to receive recommendations:
    -	It recommends new songs based on the audio features of a user's single favorite song.
    -	It recommends new songs based on the average of the audio features of all songs a user has in its profile.
    -	It recommends new songs based on the average of the audio features of any given list of songs the user specifies.

4. Cluster-based recommendation system

    This notebook contains data preparation steps and two functions: one which finds the best clustering parameters for a user’s data, and two which produces three playlists based on the user’s data. Recommendations are based on songs that are closest to cluster centroids.

#### 5. **Playlist publication.**

From the models in Section 3 and 4, we output three themed playlists with 10 tracks each for each of the above methods: Dance (danceability score > 0.7), Chill (tempo < 95, valence > 0.5), and Discover Unpopular (popularity < 60, artist popularity < 80).

We have create a similar pipeline that takes the aforementioned playlists (stored as .csv files), (i) encodes the names of the playlists so the user/beta-tester does not know the theme or the method, (ii) creates playlists in the user's Spotify account, (iii) creates an encoding dictionary that allows the user to rate/comment on each of the playlists.

Finally we provide a script that creates a playlist in a user's Spotify account, upon parsing the name of the desired playlist as well as a list of Spotify track URIs into the function.

## Files:

There are a set of notebooks for each sections. Each notebook is self-contained. See above.


## Getting Started

A pair of Spotify API keys (Client ID and Client SECRET) are required to run the notebooks. Visit the [Developer Dashboard](https://developer.spotify.com/dashboard/) for more. Create a file `client_info.py` that defines the variables CLIENT_ID and CLIENT_SECRET.

If you would like a representative sample of our Spotify sample library scraped using the Section (1) notebook, please reach out to us.

## Team
- **Benedict Au** - [Github](https://github.com/benedictau1993/)
- **Julian Kleindiek** - [Github](https://github.com/ju-kl)
- **Yannik Kumar** - [Github](https://github.com/yannikkumar)
- **Glory Scheel** - [Github](https://github.com/glorysch)
- **Abhishek Yadav** - [Github](https://github.com/to-abhi-yadav)
