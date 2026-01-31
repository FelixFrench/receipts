import random, requests, spotipy
from io import BytesIO
from urllib.parse import quote
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from escpos.printer import Network
from PIL import Image, ImageFile

# Load environment variables
load_dotenv()

PRINTER_IP = "192.168.1.165"

# Spotify OAuth setup
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(scope="user-library-read")
)

def get_random_liked_song():
    """
    Choose a random liked song from the currently authenticated user's liked songs
    """

    # First call: get first 50 songs and total count metadata
    results = sp.current_user_saved_tracks(limit=50)
    total = results["total"]

    if total == 0:
        print("No liked songs found.")
        return None
    
    # Choose a random index
    random_index = random.randint(0, total - 1)
    
    # Random index in the first 50 - use data already received
    if random_index < 50:
        tracks = results["items"]
        track = tracks[random_index]["track"]

    # Random index > 50 - get that song specifically
    else:
        results = sp.current_user_saved_tracks(
            limit=1,
            offset=random_index
        )

        track = results["items"][0]["track"]

    name = track["name"]
    artists = ", ".join(artist["name"] for artist in track["artists"])
    uri = track["uri"]

    return name, artists, uri


def get_spotify_code(uri: str, width: int = 512, bg: str = "000000", fg: str = "white") -> ImageFile.ImageFile:
    """
    Creates a spotify code jpeg image (https://www.spotifycodes.com/) for a given spotify uri
    Parameters:
        uri: The spotify uri, like "spotify:track:2gn7anBRe9H5zzkRKtFIcN"
        width: The desired width of the spotify code
        bg: Background colour, can be any hex colour.
        fg: Foreground colour, can be 'black' or 'white'
    """
    
    # Encode URI for Spotify scannables endpoint
    encoded_uri = quote(uri, safe='')
    url = f"https://scannables.scdn.co/uri/plain/jpeg/{bg}/{fg}/{width}/{encoded_uri}"
    print(url)

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to download Spotify code")
        return

    # Load image into PIL from memory
    return Image.open(BytesIO(response.content))

def print_spotify_code(image: ImageFile.ImageFile, title: str, artists: str):
    """
    Prints song title, artist, and spotify code with call to action
    """

    # Connect to printer
    printer = Network(PRINTER_IP, profile="TM-T88IV")

    # Optional header text
    printer.set(align='center', bold=True)
    printer.text(title + "\n")

    printer.set(bold=False)
    printer.text(artists + "\n\n")

    printer.image(image)

    printer.text("\nScan to open in Spotify\n\n")
    printer.cut()

    printer.close()

if __name__ == "__main__":
    song = get_random_liked_song()

    if song:
        name, artists, uri = song

        print("Printing random liked song:")
        print(name, "-", artists)
        print(uri)

        image = get_spotify_code(uri)
        if image:
            print_spotify_code(image, name, artists)
