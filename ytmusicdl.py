import json
import os
import sys
from dataclasses import dataclass


@dataclass
class Track:
    title: str
    url: str


@dataclass
class Album:
    album: str
    artist: str
    year: int
    tracks: list[Track]


def downloadCoverArt(url: str):
    pass


def getCoverArtUrlFromUrl(url: str) -> str:
    art_url = ""

    os.system(f"yt-dlp {url} --write-info-json --flat-playlist")

    filepath = ""
    for file in os.listdir("."):
        if not file.endswith(".info.json"):
            continue

        filepath = file

    with open(filepath, "r") as f:
        data = json.loads(f.read())
        cover_art_url = data["thumbnails"][1]["url"]
        art_url = cover_art_url

    os.remove(filepath)
    return art_url


def getTrackListFromFilestring(filedata: str) -> list[Track]:
    tracks = []
    items = filedata.split("\n")
    for item in items:
        if not item:
            continue

        data = json.loads(item)
        tracks.append(Track(data["title"], data["url"]))

    return tracks


def getAlbumFromURL(url: str) -> Album:
    os.system(f"yt-dlp {url} --print-json --flat-playlist > albuminfo.json")

    album = None
    with open("albuminfo.json", "r") as f:
        filestring = f.read()
        tracks = getTrackListFromFilestring(filestring)
        first_json = json.loads(filestring.split("\n")[0])

        album = Album(
            first_json["playlist"].replace("Album - ", ""),
            first_json["channel"],
            2020,
            tracks,
        )

    os.remove("albuminfo.json")
    return album


def main():
    # url = sys.argv[1]
    # folder = sys.argv[2]

    url = r"https://music.youtube.com/playlist?list=OLAK5uy_kUiWJFbgITN_YXTCrVPsH342xN9smXu4U"
    folder = "/tmp/"

    current_directory = os.getcwd()
    os.system(f"cd '{folder}'")

    album = getAlbumFromURL(url)
    cover_art_url = getCoverArtUrlFromUrl(url)
    print(cover_art_url)

    os.system(f"cd '{current_directory}'")


if __name__ == "__main__":
    main()
