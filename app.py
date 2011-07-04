#!/usr/bin/env python
"""A web interface on a parser which generates a digraph depicting
interconnections between subreddits, based on links in the sidebar
descriptions."""

import logging
from math import log

from flask import Flask, jsonify, render_template, request

from RedditParser import RedditParser

app = Flask(__name__)

_log = logging.getLogger(__name__)

parser = RedditParser()

@app.route('/<subs>/')
def show_graph(subs):
	subreddits = subs.split('+')
	return render_template('graphview.html', subreddits=subreddits)

@app.route('/_get_subs')
def get_subs():
	parent = request.args.get('parent', 'reddit.com')
	_log.info("Requesting information for /r/" + parent)
	subreddits, subscribers = parser.get_info(parent)
	size = log(subscribers)
	return jsonify(subreddit=subreddits.pop(), size=size)

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	_log.info("Starting app.")
	app.run(debug=True)
