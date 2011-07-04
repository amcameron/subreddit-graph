#!/usr/bin/env python
from sys import argv, exit
from logging import error, basicConfig, WARN

from RedditGrapher import make_graph

if __name__ == '__main__':
	basicConfig(level=WARN)
	if len(argv) < 2:
		error('No subreddit input found')
		error('Usage: ' + argv[0] + ' subreddit [subreddit2 [...]]')
		exit(1)
	make_graph(argv[1:], 'output.png')
