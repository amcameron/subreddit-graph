#!/usr/bin/env python
from sys import argv,stderr,exit
from Parser import grab_links

# Print errors to console (kill if needed)
def lineError(s,k=None):
	stderr.write(argv[0]+': '+s+'\n')
	if k: exit(k)

if len(argv)<2:
	lineError('No subreddit input found')
	lineError('Usage: '+argv[0]+' subreddit [subreddit2 [...]]',1)

for subreddit in argv[1:]:
	links = grab_links(subreddit)
