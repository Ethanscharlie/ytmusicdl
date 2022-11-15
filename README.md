# <img width=50px height=50px src="https://github.com/Ethanscharlie/ytmusicdl/blob/main/icon.png"> ytmusicdl

Takes a youtube playlist and saves it as an album, 
make sure to set the download_dir in config.json
```
{
  "use_threading": true,
  "download_dir": "/home/ethanscharlie/Music", <-- THIS
  "default": {
      "artist": "",
      "album": "",
      "url": "",
      "art": "",
      "cutoff": 0
  },
  "autoremove": [
      "Album - ",
       " - Topic"
  ]
}
```

Make sure to also install the requirements.txt
```
pip install -r requirements.txt
```
You can use the `main.py` for the graphical version
<br>
or just run `download_playlist` from `ytmusicdl.py`
<br>
`download_playlist` should be given the following dictionary
```
{
  'playlist_url': "",
  'album': "",
  'artist': "",
  'cover_art': "",
  'cutoff': ""
}  
```
`cutoff` Just takes a number of characters away from the title of each song
Good for something like `Me - My Song`
You'd probably want to remove `Me - ` from the titles
