#!/bin/bash

URL=''
ALBUM=''
ARTIST=''
COVER_ART=''
CUTOFF=''

while getopts 'u:a:r:c:s:' flag
do
    case "${flag}" in
	u) URL=${OPTARG};;
	a) ALBUM=${OPTARG};;
	r) ARTIST=${OPTARG};;
	c) COVER_ART=${OPTARG};;
	s) CUTOFF=${OPTARG};;
    esac
done

python3 -c "from ytmusicdl import download_content; download_content('$URL', '$ALBUM', '$ARTIST', '$COVER_ART', '$CUTOFF')"
