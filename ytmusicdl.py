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

    with open("albuminfo.json", "r") as f:
        filestring = f.read()
        tracks = getTrackListFromFilestring(filestring)
        first_json = json.loads(filestring.split("\n")[0])

        return Album(
            first_json["playlist"].replace("Album - ", ""),
            first_json["channel"],
            2020,
            tracks,
        )


def main():
    # url = sys.argv[1]
    # folder = sys.argv[2]

    url = r"https://music.youtube.com/playlist?list=OLAK5uy_kUiWJFbgITN_YXTCrVPsH342xN9smXu4U"
    folder = "/tmp/"

    current_directory = os.getcwd()
    os.system(f"cd '{folder}'")

    album = getAlbumFromURL(url)
    print(album.album)

    os.system(f"cd '{current_directory}'")


if __name__ == "__main__":
    main()
