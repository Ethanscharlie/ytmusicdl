import concurrent.futures
import json
import os
import re
import time

import moviepy.editor as MP
import mutagen
import requests
import wget
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from PIL import Image
from pytube import Playlist, YouTube
from termcolor import colored, cprint


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

config_file = open('config.json')
CONFIG = json.load(config_file)
config_file.close()

queue = []
percent = 0
song_data = {}

def autofill(input_data):
    # Auto-fills the empty inputs
    for key, value in input_data.items():
        if value: continue
        if key == 'album':
            input_data[key] = removeTopicStuff(playlist.title)
        elif key == 'artist':
            input_data[key] = removeTopicStuff(YouTube(playlist[0]).author)

    return input_data

def createDirs(artist, album):
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

def downloadVideo(url, directory, index, input_data):
    global counter
    global playlist
    global percent

    video = YouTube(url)
    filtered_video = video.streams.get_audio_only().download(directory)
    video_title = video.streams.filter(file_extension=VIDEO_FILE_EXT).first().default_filename.split('.')[0]
    print(video_title)
    file = f"{video_title}.{VIDEO_FILE_EXT}"

    # Convert to audio
    if re.search(VIDEO_FILE_EXT, file):
        video_path = os.path.join(directory, file)
        audio_path = os.path.join(directory, f"{os.path.splitext(file)[0]}.{AUDIO_FILE_EXT}")

        new_file = MP.AudioFileClip(video_path)
        new_file.write_audiofile(audio_path)

        os.remove(video_path)

        file = audio_path

    doMetadata(file, video_title, input_data, index)


def setCoverArt(audio_file_location, image_location):
    audio = MP3(audio_file_location, ID3=ID3)

    audio.tags.add(APIC(
        mime='image/jpeg',
        type=3,
        desc=u'Cover',
        data=open(image_location, 'rb').read()
    ))

    audio.save()


def doMetadata(file, video_title, input_data, index):
    global counter

    # Metadatafile
    try:
        audio = EasyID3(file)
    except:
        try:
            audio = mutagen.File(file, easy=True)
            audio.add_tags()
        except:
            print(f"{bcolors.FAIL}There was an metadata error on {video_title}{bcolors.ENDC} -- {file}")
            return

    audio.delete()
    audio['title'] = f"{video_title[int(input_data['cutoff']):]}"
    audio["album"] = input_data['album']
    audio['artist'] = input_data['artist']
    audio['tracknumber'] = str(index)

    audio.save()

    # Cover Art
    img_file = ''
    target_location = os.path.join(os.path.dirname(file), 'cover.jpg')

    if os.path.exists(input_data['cover_art']): img_file = input_data['cover_art']

    if os.path.exists(target_location):
        img_file = target_location

    else:
        try:
            if requests.get(input_data['cover_art']).status_code:
                img_file = wget.download(input_data['cover_art'], os.path.dirname(file))
                image = Image.open(img_file)

                # Save
                image.save(target_location)
                os.remove(img_file)

                img_file = target_location

        except:
            print('not web')

    if img_file: setCoverArt(file, img_file)

    # End
    print(input_data['cutoff'])
    print(video_title[int(input_data['cutoff']):])
    print(f"{bcolors.OKBLUE}Finished {audio['title']} | {input_data['album']} | {audio['artist']}{bcolors.ENDC}")

    counter += 1
    percent = (counter / len(playlist)) * 100
    print(f"{bcolors.OKCYAN}{counter} / {len(playlist)}{bcolors.ENDC}")

def removeTopicStuff(string):
    for text in CONFIG['autoremove']:
        if text in string:
            string = string.replace(text, "")

    print(string)
    return string

def downloadPlaylist(input_data):
    global counter
    global playlist
    counter = 0

    start_time = time.perf_counter()

    try:
        playlist = Playlist(input_data['playlist_url'])
    except:
        try:
            video = YouTube(input_data['playlist_url'])
        except:
            return
        else:
            input_type = 'video'
    else:
        input_type = 'playlist'

    main_directory = os.path.join(CONFIG['download_dir'])
    

    input_data = autofill(input_data)

    print(input_data)

    if input_data['cover_art'] == 'thumb':
        
        input_data['cover_art'] = YouTube(playlist[0]).thumbnail_url

    download_directory = createDirs(input_data['artist'], input_data['album'])

    # Download Videos
    if CONFIG['use_threading']:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = []
            for url in playlist:
                index = str(playlist.index(url) + 1)
                results.append(executor.submit(downloadVideo, url, download_directory, index, input_data))

    else:
        " ---- When you don't want to use threading ---- "
        for url in playlist:
            index = str(playlist.index(url) + 1)
            downloadVideo(url, download_directory, index, input_data)

    end_time = time.perf_counter()

    print(
        f"{bcolors.OKGREEN}Finished Downloading Content in {round(end_time - start_time)} second(s)! :){bcolors.ENDC}")


def getDownloadTitle(url):
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

    # video = YouTube(url)
    # return video.streams[0].default_filename


def testCutoff(playlist_url, cutoff):
    playlist = Playlist(playlist_url)
    print(playlist)

    videos = (playlist[0], playlist[-1])
    titles = [getDownloadTitle(v) for v in videos]

    return [f'{titles[i]} --> "{titles[i][int(cutoff):]}"' for i, v in enumerate(videos)]
