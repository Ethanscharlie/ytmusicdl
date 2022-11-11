from unittest import registerResult
from formlayout import fedit
from formlayout import QLineEdit
import formlayout as fl
import json
import ytmusicdl

queue = []

def resToDict(res):
    return {
        'playlist_url': res[0],
        'album': res[1],
        'artist': res[2],
        'cover_art': res[3],
        'cutoff': res[5]
    }  

def fancyQueue(): return '\n\n'.join([str(json.dumps(i, indent=4, sort_keys=True)) for i in queue])

def testCutoff(result, widgets):
    current = resToDict(result)
    print(current)
    cuts = [str(s) for s in ytmusicdl.testCutoff(current['playlist_url'], current['cutoff'])]

    if isinstance(widgets[5], fl.QLineEdit):
        widgets[5].setText(
            f'{cuts}'
        )

playlistAdd = [
        ('Playlist url', 'https://www.youtube.com/playlist?list=PL71E19E7A8803384C'),
        ('Album Title', 'Zelda 1 OST'),
        ('Artist', 'Nintendo'),
        ('Cover Art \n(location, url, \nor "thumb"', 'thumb'),
        (None, None),
        ('test', 'To test cutoff here'),
        ('Cutoff', 34),
        (None, [('Test Cutoff', testCutoff)])
        ]



queue.append(resToDict(['Example' for _ in range(10)]))

def addPlaylist(result, widgets): 
    queue.append(resToDict(
        fedit(playlistAdd, title="YT Music DL: Add Playlist", comment=' '.join(['-' for _ in range(200)]))
    ))

    for widget in widgets:
        if isinstance(widget, fl.QTextEdit):
            widget.setText(
                fancyQueue()
            )

    print(
        fancyQueue()
    )


mainQueue = [
        ('Queue', fancyQueue()),
        (None, [('Add Playlist', addPlaylist)])
        ]

queue.pop(0)

res = fedit(mainQueue, title="YT Music DL", comment=' '.join(['-' for _ in range(200)]))

print("result:", res)

while len(queue) > 0:
        if len(queue) > 0:
            ytmusicdl.downloadPlaylist(queue[0])
            queue.pop(0)