#!/usr/bin/env python
from sys import argv, stderr, exit
from math import log, sqrt
import logging

from yapgvb import Digraph, engines

from RedditParser import RedditParser

#TODO: change this from a constant to a commandline argument
MAX_DEPTH = 3
WIDTH_NORMALIZER = 3


def width(num_subs):
	try:
		a = log(num_subs, WIDTH_NORMALIZER)
	except ValueError:
		a = 0
	if a < 3:
		a = 3
	return sqrt(a)


def make_graph(args, outfile):
	graph = Digraph('Subreddit connection graph starting with:\n' +
			', '.join(args))

	parser = RedditParser()
	next_subs = set(subreddit.lower() for subreddit in args)
	logging.debug("Received on commandline: " + ' '.join(next_subs))
	visited = set()

	for current_depth in xrange(MAX_DEPTH):
		current_subs = next_subs
		visited.update(next_subs)
		if len(current_subs) == 0:
			break
		next_subs = set()

		for subreddit in current_subs:
			logging.debug("Visiting: " + subreddit)
			info = parser.get_info(subreddit)
			if info:
				links, num_subs = info
			else:
				continue
			current_node = graph.add_node(subreddit, shape="circle",
					width=width(num_subs), fixedsize=True,
					label='\n'.join([subreddit, str(num_subs)]))
			logging.debug("Received links: " + ' '.join(links))

			for link in links:
				if link not in visited:
					next_subs.add(link)
				new_node = graph.add_node(link)
				current_node >> new_node

	logging.debug("Done main loop.  Remaining unvisited subs:\n" +
			'\n'.join(next_subs))
	# Style the subreddits we didn't visit due to maximum search depth being
	# reached.
	for link in next_subs:
		info = parser.get_info(link)
		if info:
			links, num_subs = info
		else:
			continue
		logging.debug("Updating properties for remaining subreddit: %s" % link)
		graph.add_node(link, shape="circle",
				width=width(num_subs), fixedsize=True,
				label='\n'.join([link, str(num_subs)]))

	graph.layout(engines.dot)
	graph.render(outfile)


if __name__=="__main__":
	logging.basicConfig(level=logging.WARN)
	if len(argv) < 2:
		logging.error('No subreddit input found')
		logging.error('Usage: ' + argv[0] + ' subreddit [subreddit2 [...]]')
		exit(1)
	make_graph(argv[1:], 'output.png')
