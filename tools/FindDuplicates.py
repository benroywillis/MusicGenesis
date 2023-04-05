
import os

# get all paths to all files that end in mp3
mp3s = {}
for root, dirs, files in os.walk(".", topdown=False):
	for name in files:
		if name.endswith(".mp3"):
			if mp3s.get(name) is None:
				mp3s[name] = set()
			mp3s[name].add(root)
for name, paths in mp3s.items():
	if len(paths) > 1:
		print(f"Duplicate: {name} - in paths {list(paths)}")
