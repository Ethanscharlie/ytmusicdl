# <img width=50px height=50px src="https://github.com/Ethanscharlie/ytmusicdl/blob/main/icon.png"> ytmusicdl

Takes a youtube playlist and saves it as an album, 

Run the `ytmusicdl.sh` with
```
-u          Sets the url (required)
-a          Sets the Album Name
-r          Sets the Artist Name
-c          Sets the cover art (Can be a location or url)
-s          Sets the cutoff (cuts a length of the front of each title) (A number)
```
EX: 
```
./ytmusicdl.sh -u https://music.youtube.com/playlist?list=OLAK5uy_nmDUsWOMoEcz0SsVqUwir0oxu-k1oUyXE -a "A Funny Little thing" -c https://i.ytimg.com/vi/j4U-Yutgvi0/maxresdefault.jpg
```

Make sure to set the download_dir in config.json
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
