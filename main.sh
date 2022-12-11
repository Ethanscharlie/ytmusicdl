#!/bin/bash

python3 -c "from ytmusicdl import download_content; download_content('$1', '$ALBUM', '$ARTIST', '$COVER_ART', '$CUTOFF')"
