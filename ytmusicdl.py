"""
Written by Ethanscharlie
https://github.com/Ethanscharlie
"""

import concurrent.futures
import json
import os
import re
import time
import moviepy.editor as mp
import mutagen
import requests
import wget
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from PIL import Image
from pytube import Playlist, YouTube


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


VIDEO_FILE_EXT = "mp4"
AUDIO_FILE_EXT = "mp3"
DIRECTORY = os.path.dirname(__file__)
TEMPDIR = os.path.join(DIRECTORY, 'temp')
REQUESTED_INPUT_DATA =  {
         'playlist_url': "",
         'album': "",
         'artist': "",
         'cover_art': "",
         'cutoff': ""
    }

config_file = open('config.json')
CONFIG = json.load(config_file)
config_file.close()

queue = []
percent = 0
song_data = {}
counter = 0


def download_video(url: str, directory: str):
    # Downloads the YouTube video using the given link to the given directory

    global percent

    video = YouTube(url)
    filtered_video = video.streams.get_audio_only().download(directory)
    video_title = video.streams.filter(file_extension=VIDEO_FILE_EXT).first().default_filename.split('.')[0]
    print(video_title)
    file = f"{video_title}.{VIDEO_FILE_EXT}"

    # Convert video (mp4) to audio (mp3)
    if re.search(VIDEO_FILE_EXT, file):
        video_path = os.path.join(directory, file)
        audio_path = os.path.join(directory, f"{os.path.splitext(file)[0]}.{AUDIO_FILE_EXT}")

        new_file = mp.AudioFileClip(video_path)
        new_file.write_audiofile(audio_path)

        os.remove(video_path)

        return audio_path, video_title


def set_cover_art(audio_file_location: str, image_location: str):
    # Sets the album cover art of the file to the image

    audio = MP3(audio_file_location, ID3=ID3)

    audio.tags.add(APIC(
        mime='image/jpeg',
        type=3,
        desc=u'Cover',
        data=open(image_location, 'rb').read()
    ))

    audio.save()


def get_cover_art(input_cover_art: str, directory: str):
    # Grabs and downloads the cover art after figuring out if it's a location, or a web image

    target_location = os.path.join(directory, 'cover.jpg')

    # Tests for if the image is on the system
    if os.path.exists(input_cover_art):
        return input_cover_art

    # Tests if the image has already been downloaded onto the system
    if os.path.exists(target_location):
        return target_location

    else:
        try:
            # Downloads the image from the url
            if requests.get(input_cover_art).status_code:
                img_file = wget.download(input_cover_art, directory)
                image = Image.open(img_file)

                # Save
                image.save(target_location)
                os.remove(img_file)

                return target_location
        except:
            print('not web')

    print(f"{bcolors.FAIL}Image not found :({bcolors.ENDC}")
    return


def do_metadata(file: str, video_title: str, input_data: dict, index='1'):
    # Sets the metadata (album name, title, art, etc.) for the mp3 file

    global counter

    # Gets the audio in mutagen
    try:
        audio = EasyID3(file)
    except:
        try:
            audio = mutagen.File(file, easy=True)
            audio.add_tags()
        except:
            print(f"{bcolors.FAIL}There was an metadata error on {video_title}{bcolors.ENDC} -- {file}")
            return

    # Wipes and then sets each tag to the given input data
    audio.delete()
    audio['title'] = f"{video_title[int(input_data['cutoff']):]}"
    audio["album"] = input_data['album']
    audio['artist'] = input_data['artist']
    audio['tracknumber'] = str(index)
    audio.save()

    # Cover art
    img_file = get_cover_art(input_data['cover_art'], os.path.dirname(file))
    if img_file: set_cover_art(file, img_file)

    return audio


def remove_topic_stuff(string: str) -> str:
    # Removes dumb YouTube things in names like - Topic, or Album -

    for text in CONFIG['autoremove']:
        if text in string:
            string = string.replace(text, "")

    print(string)
    return string


def do_video(url: str, directory: str, input_data: dict, index='1'):
    # Downloads and then sets the metadata for the video
    
    global counter
    global percent

    file, video_title = download_video(url, directory)
    audio = do_metadata(file, video_title, input_data, index)

    # End
    print(input_data['cutoff'])
    print(video_title[int(input_data['cutoff']):])
    print(f"{bcolors.OKBLUE}Finished {audio['title']} | {input_data['album']} | {audio['artist']}{bcolors.ENDC}")

    counter += 1
    percent = (counter / len(playlist)) * 100
    print(f"{bcolors.OKCYAN}{counter} / {len(playlist)}{bcolors.ENDC}")


def create_dirs(artist: str, album: str) -> str:
    # Creates the directory's for the music files, Folder -> Artist -> Album/Single

    # Make new directory or wipe old one
    try:
        os.mkdir(os.path.join(CONFIG['download_dir'], artist))
    except:
        print("Artist folder already exists")

    # Make new directory or wipe old one
    try:
        os.mkdir(os.path.join(CONFIG['download_dir'], artist, album))
    except:
        print("Download folder already exists")
        # Wipe
        for i in os.listdir(os.path.join(CONFIG['download_dir'], artist, album)):
            os.remove(os.path.join(CONFIG['download_dir'], artist, album, i))

    return os.path.join(CONFIG['download_dir'], artist, album)


def autofill_input(input_data: dict, url_type, content) -> dict:
    # Autofill the possibly empty inputs with data taken from the playlist (Like the playlist name and channel name)
    for key, value in input_data.items():
        if value: continue
        if key == 'album':
            input_data[key] = remove_topic_stuff(content.title)
        elif key == 'artist':
            if url_type == 'playlist':
                input_data[key] = remove_topic_stuff(YouTube(content[0]).author)
            else:
                input_data[key] = remove_topic_stuff(content.author)

    return input_data


def download_playlist(playlist, input_data: dict, download_directory: str):
    # Download Videos
    if CONFIG['use_threading']:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = []
            for url in playlist:
                index = str(playlist.index(url) + 1)
                results.append(executor.submit(do_video, url, download_directory, input_data, index))

    else:
        " ---- When you don't want to use threading ---- "
        for url in playlist:
            index = str(playlist.index(url) + 1)
            do_video(url, download_directory, input_data, index)


def download_song(video_url: str, input_data: dict, download_directory: str):
    # Downloads a single song
    do_video(video_url, download_directory, input_data)


def download_content(input_data: dict):
    # Downloads a YouTube playlist as an album
    # {
    #     'playlist_url': "",
    #     'album': "",
    #     'artist': "",
    #     'cover_art': "",
    #     'cutoff': ""
    # }
    # input_data should be a dictionary and look like this

    global counter
    global playlist
    counter = 0

    start_time = time.perf_counter()

    # Checks if the url given is a Video or a Playlist
    try:
        content = YouTube(input_data['playlist_url'])
    except:
        try:
            content = Playlist(input_data['playlist_url'])
        except:
            return False, 'Invalid Url'
        else:
            url_type = 'playlist'
    else:
        url_type = 'video'

    print(content)
    print(url_type)
    input_data = autofill_input(input_data, url_type, content)
    print(input_data)

    # Gets the url for the YouTube thumbnail (if requested) so it can be downloaded later
    if input_data['cover_art'] == 'thumb':
        if url_type == 'playlist':
            input_data['cover_art'] = YouTube(content[0]).thumbnail_url
        else:
            input_data['cover_art'] = content.thumbnail_url

            # Make Dirs
    download_directory = create_dirs(input_data['artist'], input_data['album'])

    # Do the thing
    if url_type == 'playlist':
        download_playlist(content, input_data, download_directory)
    else:
        download_song(input_data['playlist_url'], input_data, download_directory)

    end_time = time.perf_counter()

    print(
        f"{bcolors.OKGREEN}Finished Downloading Content in {round(end_time - start_time)} second(s)! :){bcolors.ENDC}")


def get_download_title(url: str):
    # Gets the title of what a video will be called when it is downloaded

    # Make new directory or wipe old one
    try:
        os.mkdir(TEMPDIR)
    except:
        print("TEMPDIR folder already exists")

        for i in os.listdir(TEMPDIR):
            os.remove(os.path.join(TEMPDIR, i))

    print(url)
    video = YouTube(url)
    filtered_video = video.streams.get_audio_only().download(TEMPDIR)
    return video.streams.filter(file_extension=VIDEO_FILE_EXT).first().default_filename.split('.')[0]


def test_cutoff(playlist_url: str, cutoff):
    # Tests the title cutoff

    playlist = Playlist(playlist_url)
    print(playlist)

    videos = (playlist[0], playlist[-1])
    titles = [get_download_title(v) for v in videos]

    return [f'{titles[i]} --> "{titles[i][int(cutoff):]}"' for i, v in enumerate(videos)]
