import pandas as pd
from deezer import Client


def find_deezer_link(song_title, artist_name):
    """
    Searches for a song on Deezer and returns the link if it matches accurately or closely.

    Parameters:
        song_title (str): The title of the song.
        artist_name (str): The name of the artist.

    Returns:
        str: Deezer link if a close match is found, otherwise None.
    """
    client = Client()
    search_results = client.search(f"{song_title} {artist_name}", strict=True)

    for track in search_results:
        return (
            track.link,
            # track.title,
            # track.artist,
        )  # Return the Deezer link if there's a close match
    return None  # No close match found


def process_csv(input_csv, output_csv):
    """
    Reads a CSV file, finds Deezer links for songs, and writes the results to a new CSV.

    Parameters:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file.
    """
    # Read the input CSV
    df = pd.read_csv(input_csv)

    # Ensure required columns are present
    if "Track Name" not in df.columns or "Artist Name(s)" not in df.columns:
        print(
            "Error: Input CSV must contain 'Track Name' and 'Artist Name(s)' columns."
        )
        return

    # Add a new column for Deezer links
    df["Deezer Link"] = df.apply(
        lambda row: find_deezer_link(row["Track Name"], row["Artist Name(s)"]),
        axis=1,
    )

    # Save the results to the output CSV
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")


if __name__ == "__main__":
    # Input and output CSV file paths
    input_csv_file = "test_input.csv"
    output_csv_file = "test_output.csv"

    process_csv(input_csv_file, output_csv_file)

# print(find_deezer_link("All About Us", "He Is We, Owl City"))
