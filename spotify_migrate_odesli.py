"""
Export spotify playlists: https://github.com/watsonbox/exportify
Fetch song informations: https://odesli.co
Easily migrate away from Spotify to Tidal, Deezer, Youtube
"""

import os
import time

import pandas as pd
import requests

# File paths
LIKED_SONGS_FILE = "liked_songs.csv"
OUTPUT_FILE = "liked_songs_links.csv"
PROGRESS_FILE = "liked_songs_progress.csv"

# Load the liked_songs CSV
liked_songs = pd.read_csv(LIKED_SONGS_FILE)

# Ensure columns have no extra spaces
liked_songs.columns = liked_songs.columns.str.strip()

# Load the progress CSV if it exists, to resume where we left off
if os.path.exists(PROGRESS_FILE):
    print("Loading progress from previous run...")
    progress_df = pd.read_csv(PROGRESS_FILE)
else:
    # Create the initial progress DataFrame with additional columns
    progress_df = liked_songs[
        ["Track URI", "Track Name", "Artist Name(s)", "Album Name"]
    ].copy()
    progress_df["Tidal Link"] = None
    progress_df["Deezer Link"] = None
    progress_df["YouTube Link"] = None
    progress_df["isProcessed"] = False

# Base URL for the Odesli API (SongLink)
ODESLI_API_URL = "https://api.song.link/v1-alpha.1/links"


# Function to query Odesli API and extract platform links
def get_platform_links(spotify_uri):
    if pd.isna(spotify_uri):  # Skip if the URI is missing
        return None, None, None

    try:
        # Make a request to the Odesli API
        response = requests.get(ODESLI_API_URL, params={"url": spotify_uri})
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        data = response.json()

        # Extract the links for Tidal, Deezer, and YouTube
        tidal_url = data.get("linksByPlatform", {}).get("tidal", {}).get("url")
        deezer_url = data.get("linksByPlatform", {}).get("deezer", {}).get("url")
        youtube_url = data.get("linksByPlatform", {}).get("youtube", {}).get("url")

        return tidal_url, deezer_url, youtube_url

    except requests.RequestException as e:
        print(f"Error querying Odesli API for URI {spotify_uri}: {e}")
        # If an error occurs, return None for all links, indicating processing failure
        return None, None, None


# Process the rows and add the links
def process_songs():
    new_rows = []

    for idx, row in progress_df.iterrows():
        # Skip already processed rows
        if row["isProcessed"]:
            continue

        spotify_uri = row["Track URI"]
        track_name = row["Track Name"]
        artist_name = row["Artist Name(s)"]
        album_name = row["Album Name"]

        # Get the platform links
        tidal_url, deezer_url, youtube_url = get_platform_links(spotify_uri)

        # If all links are None (meaning API error), mark as unprocessed
        if tidal_url is None and deezer_url is None and youtube_url is None:
            progress_df.at[idx, "isProcessed"] = False
            print(f"Error processing song {track_name}. Marked as unprocessed.")
        else:
            # Update the progress DataFrame with the new links
            progress_df.at[idx, "Tidal Link"] = tidal_url
            progress_df.at[idx, "Deezer Link"] = deezer_url
            progress_df.at[idx, "YouTube Link"] = youtube_url
            progress_df.at[idx, "isProcessed"] = True

            # Append the row to the list for final output
            new_rows.append(
                {
                    "spotify uri": spotify_uri,
                    "title": track_name,
                    "artist": artist_name,
                    "album": album_name,
                    "tidal link": tidal_url,
                    "deezer link": deezer_url,
                    "youtube link": youtube_url,
                    "isProcessed": True,
                }
            )

        # Periodically save progress to a CSV
        if idx % 10 == 0:  # Every 10 rows
            print(f"Saving progress at row {idx}...")
            progress_df.to_csv(PROGRESS_FILE, index=False)
            time.sleep(6)  # Sleep to respect the rate limit of 10 songs per minute

    # Convert the list of new rows to a DataFrame and save to output CSV
    output_df = pd.DataFrame(new_rows)
    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"New CSV file created: {OUTPUT_FILE}")


# Start the song processing
process_songs()

# Final save of progress after completion
progress_df.to_csv(PROGRESS_FILE, index=False)
print("Final progress saved.")
