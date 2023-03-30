# ripped from https://dev.to/stokry/download-youtube-video-to-mp3-with-python-26p
# further explanation of how youtube_dl works can be found at https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script
# if you encounter a 403 error, run (on the command line) youtube-dl --rm-cache-dir and that should resolve the issue

import youtube_dl
import eyed3
from get_cover_art import CoverFinder
import argparse
from datetime import datetime
import os

targetHeaders = { "Title", "Album", "Artist", "Genre", "Year", "Link", "Date Added" }

def Parse_Args():
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("-i", "--input", default="songs.csv", help="Input csv file with a column called \"Links\"")
	arg_parser.add_argument("--offset", default=0, help="Row number in which to start using links for download.")
	arg_parser.add_argument("--force-album", action="store_true", help="Force the album art finder to find new album art.")
	arg_parser.add_argument("--today", action="store_true", help="Only process entries in the input csv that were added today. This argument trumps other date arguments.")
	arg_parser.add_argument("--start-date", default=None, help="Date at which to start the reading of the input csv. Input must be in yyyymmdd format. The input will be interpreted as the date to start the search and includes the date input. Defaults to the first date in the input csv.")
	arg_parser.add_argument("--end-date", default=None, help="Date at which to end the reading of the input csv. Input must be in yyyymmdd format. The input will be interpreted as the date to search the search and includes the date input. Defaults to the last date in the csv.")
	arg_parser.add_argument("--output", default="", help="Output location to store the results. Defaults to the current date.")
	arg_parser.add_argument("--cookies", default="", help="Point to a cookie file for bypassing youtube video age restrictions. This file must be an absolute path.")
	arg_parser.add_argument("--cache", default="./", help="Folder for youtube_dl to dump its cache data. Defaults to the current directory.")
	args = arg_parser.parse_args()
	# arg post processing
	args.offset = int(args.offset)
	if args.start_date:
		args.start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
	else:
		args.start_date = datetime.min.date()
	if args.end_date:
		args.end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
	else:
		args.end_date = datetime.max.date()
	if not len(args.output):
		args.output = str(datetime.today().date())
	if not os.path.isdir(args.output):
		os.mkdir(args.output)
	return args

def readInput(args):
	"""
	Input file should contain the following column headers (with exactly this spelling, all others will be ignored):
	Title,Album,Artist,Genre,Year,Link,Date Added
	"""
	try:
		with open(args.input, "r") as f:
			inputCSV = f.read()
	except FileNotFoundError:
		print("Could not read input file "+args.input)
		return {}
	# turn the csv text into an array
	targetColumns = {}
	date_col = 0
	i_c = 0
	for header in inputCSV.split("\n")[0].split(","):
		if header in targetHeaders:
			targetColumns[header] = i_c
		i_c += 1

	# process each line, we use "" to support names with commas in them
	csvArray = []
	for line in inputCSV.split("\n")[1:]:
		entries = line.split(",")
		lineList = []
		quotedEntry = ""
		for i in range(len(entries)):
			if "\"" in entries[i]:
				if entries[i].startswith("\""):
					quotedEntry = entries[i]
				elif entries[i].endswith("\""):
					quotedEntry += entries[i]
					lineList.append(quotedEntry)
					quotedEntry = ""
				else:
					raise Exception("Could not handle position of quote in csv entry!")
			elif (len(entries[i]) == 0) and (i == targetColumns["Link"]):
				# skip, there is no video available for this entry
				print("Found empty link in line "+str(lineList))
				continue
			else:
				if len(quotedEntry):
					quotedEntry += entries[i]
				else:
					lineList.append(entries[i])
		csvArray.append(lineList)

	# maps a link to song info (Title, Album, Artist, Genre)
	songInfo = {}
	for line in csvArray:
		if len(line) != len(targetHeaders) + 3:
			# this skips entries with incomplete data
			continue
		songInfo[ line[targetColumns["Link"]] ] = { "Title"  : line[targetColumns["Title"]], \
													"Album"  : line[targetColumns["Album"]], \
													"Artist" : line[targetColumns["Artist"]],\
													"Genre"  : line[targetColumns["Genre"]], \
													"Year"   : line[targetColumns["Year"]], \
												    "Date"   : datetime.strptime(line[targetColumns["Date Added"]], '%Y-%m-%d').date()
												  }
	return songInfo

def Pull(s, album_art_finder, args):
	"""
	@brief 	Pulls down the video encoded within the tuple s
	@param[in]	s	Key-value pair: "Link": { "Title": ... , "Album": ..., "Artist": ..., "Genre": ... }
	"""
	video_info     = youtube_dl.YoutubeDL().extract_info( url=s[0], download=False)	
	filename_root = args.output+"/"+str(video_info["title"]).replace(" ","").replace("(","_").replace(")","").replace("'","").replace("&","and").replace(":","").replace("[","_").replace("]","").replace("/","").replace("\"","").replace("|","_").replace("%","PERCENT")
	filename_video = filename_root+".WebM"
	filename_audio = filename_root+".mp3"
	# "rm_cachedir": True seems to break the script by getting rid of evidence of the download
	options = { "format": "bestaudio/best", "keepvideo": False, "outtmpl": filename_video, "cookiefile": args.cookies, 
				"verbose": True, "cachedir": args.cache, "rm_cachedir": True, "postprocessors": [{ "key": "FFmpegExtractAudio",\
										  											               "preferredcodec": "mp3",\
										  											               "preferredquality": "192",\
										  											               "nopostoverwrites": False }],\
				"ignoreerrors": True
			  }
	# check to see if we already have this file, if we do then skip the download
	download = False
	try:
		with open(filename_audio, "r") as f:
			print("Already found "+filename_audio+". Skipping download...")
	except FileNotFoundError:
		print("Could not find "+filename_audio+". Downloading...")
		download = True
	if download:
		try:
			with youtube_dl.YoutubeDL(options) as ydl:
				ydl.download( [video_info["webpage_url"]] )
				print("Downloaded "+filename_video)
		except Exception as e:
			print("Error downloading "+filename_video+": "+str(e))

	# mp3 information injection: Title, Album, Artist, Genre, Cover Art
	f = eyed3.load(filename_audio)
	if f is None:
		print(filename_audio+": File format not recognized")
		print()
		return "Format"
	else:
		if f.tag is None:
			f.initTag()
		f.tag.title  = s[1]["Title"]
		f.tag.album  = s[1]["Album"]
		f.tag.artist = s[1]["Artist"]
		f.tag.genre  = s[1]["Genre"]
		# according to eyed3 documentation, applications use either of these fields to determine the "year" of the mp3
		f.tag.recording_date = s[1]["Year"]
		f.tag.release_date = s[1]["Year"]
		f.tag.save()
		print("Injected ID3 data for "+filename_audio)

		# album art finder
		album_art_finder.scan_file(filename_audio)
	print()
	return "Success"

def DownLoadPlayList(songInfo):
	"""
	Downloads a series of songs from an input playlist (see readInput()) and returns errors
	"""
	# album art finder 
	album_art_finder = CoverFinder( { "verbose": True , "force": args.force_album } )

	# keeps track of outcomes
	errors = { "Success": [], "Download": [], "Format": [] }

	for s in songInfo.items():
		if args.today:
			if s[1]["Date"] == datetime.today().date():
				e = Pull(s, album_art_finder, args)
				errors[e].append( s )
		elif (args.start_date <= s[1]["Date"]) and (s[1]["Date"] <= args.end_date):
			e = Pull(s, album_art_finder, args)
			errors[e].append( s )

	print("Successful downloads:")
	for success in errors["Success"]:
		print(success[1]["Artist"]+" - "+success[1]["Title"])
	print()
	print("Failed downloads:")
	for success in errors["Download"]:
		print(success[1]["Artist"]+" - "+success[1]["Title"])
	print()
	print("Failed formats:")
	for success in errors["Format"]:
		print(success[1]["Artist"]+" - "+success[1]["Title"])
	print()

args = Parse_Args()
songInfo = readInput(args)
DownLoadPlayList(songInfo)
