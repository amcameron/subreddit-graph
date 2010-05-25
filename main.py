#!/usr/bin/env python
from sys import argv,stderr,exit

from yapgvb import Digraph, engines

from Parser import grab_links

#TODO: change this from a constant to a commandline argument
MAX_DEPTH = 10

# Print errors to console (kill if needed)
def lineError(s,k=None):
	stderr.write(argv[0]+': '+s+'\n')
	if k: exit(k)

if len(argv)<2:
	lineError('No subreddit input found')
	lineError('Usage: '+argv[0]+' subreddit [subreddit2 [...]]',1)

graph = Digraph('Subreddit connection graph starting with:\n' +
		', '.join(argv[1:]))

next_subs = set(subreddit.lower() for subreddit in argv[1:])
visited = set()

for current_depth in xrange(MAX_DEPTH):
	current_subs = next_subs
	visited.update(next_subs)
	next_subs = set()
	if len(current_subs) == 0:
		break

	for subreddit in current_subs:
		current_node = graph.add_node(subreddit)
		links = grab_links(subreddit)

		for link in links:
			if link not in visited:
				next_subs.add(link)
			new_node = graph.add_node(link)
			current_node >> new_node

graph.layout(engines.circo)
graph.render('output.png')
