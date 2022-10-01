# Music Genesis
Install python (for windows use the Microsoft store), vscode and git

Open a terminal in vscode ([at the top left] Terminal->New Terminal)
Install the required packages in powershell:

PS<> python3 -m pip install youtube_dl eyed3 get_cover_art argparse datetime

To see options for the script
PS<> python3 Driver.py -h

Run the script in your terminal
PS<> python3 Driver.py -i SongsForDownload.csv

BUG: windows does not come with ffmpeg out of the box... The binaries are not straightforward to download.