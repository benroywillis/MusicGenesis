# Music Genesis
Music Genesis pulls music for free from youtube videos and injects ID3 metadata and album art into the resulting mp3.
Album art is retrived on [apple music](music.apple.com).
[Here](https://docs.google.com/spreadsheets/d/10gzH_82USuDUPUejgedm8s6WQZ8FnlakuW6jZOTzwIQ/edit?usp=sharing) is an example input file for the driver.

## Dependencies
* youtube_dl
* eyed3
* get_album_art
* ffmpeg (doesn't come in windows out of the box)

## Installation
Install python (for windows use the Microsoft store), vscode and git

Open a terminal in vscode ([at the top left] Terminal->New Terminal)
Install the required packages in powershell:

PS<> python3 -m pip install youtube_dl eyed3 get_cover_art argparse datetime

To see options for the script
PS<> python3 Driver.py -h

Run the script in your terminal
PS<> python3 Driver.py -i SongsForDownload.csv

BUG: windows does not come with ffmpeg out of the box... The binaries are not straightforward to download.
