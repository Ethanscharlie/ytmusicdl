from pytube import YouTube, Playlist
import re

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

import wget
import moviepy.editor as MP
from PIL import Image
import requests
import time
import concurrent.futures
import os
from termcolor import colored, cprint
import json

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

    if os.path.exists(input_data['cover_art']): img_file = input_data['cover_art']

    try:
        if requests.get(input_data['cover_art']).status_code: 
            img_file = wget.download(input_data['cover_art'], os.path.dirname(file))
            Image.open(img_file).save(os.path.join(os.path.dirname(file), 'cover.jpg'))
            os.remove(img_file)
            img_file = os.path.join(os.path.dirname(file), 'cover.jpg')
    except:
        print('not web')
    
    if img_file: setCoverArt(file, img_file)
    
    # End
    print(input_data['cutoff'])
    print(video_title[int(input_data['cutoff']):])
    print(f"{bcolors.OKBLUE}Finished {audio['title']} | {input_data['album']} | {audio['artist']}{bcolors.ENDC}")

    counter += 1
    percent = (counter/len(playlist)) * 100
    print(f"{bcolors.OKCYAN}{counter} / {len(playlist)}{bcolors.ENDC}")

def downloadPlaylist(input_data):
    global counter
    global playlist
    counter = 0

    start_time = time.perf_counter()

    main_directory = os.path.join(CONFIG['download_dir'])
    playlist = Playlist(input_data['playlist_url'])

    print(input_data)

    if input_data['cover_art'] == 'thumb':
        input_data['cover_art'] = YouTube(playlist[1]).thumbnail_url

    # Make new directory or wipe old one
    try:
        os.mkdir(os.path.join(main_directory, input_data['artist']))
    except:
        print("Artist folder already exists")

    # Make new directory or wipe old one
    try:
        os.mkdir(os.path.join(main_directory, input_data['artist'], input_data['album']))
    except:
        print("Download folder already exists")
        # Wipe
        for i in os.listdir(os.path.join(main_directory, input_data['artist'], input_data['album'])):
            os.remove(os.path.join(main_directory, input_data['artist'], input_data['album'], i))

    download_directory = os.path.join(main_directory, input_data['artist'], input_data['album'])

    # Download Videos
    if CONFIG['use_threading']:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = []
            for url in playlist:
                index = str(playlist.index(url)+1)
                results.append(executor.submit(downloadVideo, url, download_directory, index, input_data))

    else:
        " ---- When you don't want to use threading ---- "
        for url in playlist:
            index = str(playlist.index(url)+1)
            downloadVideo(url, download_directory, index, input_data)

    end_time = time.perf_counter()

    print(f"{bcolors.OKGREEN}Finished Downloading Content in {round(end_time - start_time)} second(s)! :){bcolors.ENDC}")

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