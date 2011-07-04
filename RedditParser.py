#!/usr/bin/env python
from sys import exit, argv
import logging
from HTMLParser import HTMLParser
from httplib import HTTPConnection


_log = logging.getLogger(__name__)


class RedditHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.reset()

	def reset(self):
		HTMLParser.reset(self)
		self.Record = False
		self.RecordSub = False
		self.RecordLink = False
		self.Depth = 0
		self.Subscribers = 0
		self.Links = []
		self.LinkNames = []

	def handle_starttag(self, tag, attrs):
		if tag == 'div' and ('class', 'usertext-body') in attrs:
			self.Record = True
		if tag == 'span' and ('class', 'number') in attrs:
			self.RecordSub = True
		if not self.Record:
			return
		if tag == 'div':
			self.Depth += 1
		elif tag == 'a':
			for (attr, val) in attrs:
				if attr == 'href':
					self.RecordLink = True
					self.Links.append(val)

	def handle_data(self, data):
		if self.RecordSub:
			self.Subscribers = int(data.replace(',', ''))
		if self.RecordLink:
			self.LinkNames.append(data)
			self.RecordLink = False

	def handle_endtag(self, tag):
		if self.Record and tag == 'div':
			self.Depth -= 1
			self.Record = self.Depth != 0
		else:
			self.RecordSub = False

class RedditParser:
	def __init__(self):
		self.connection = HTTPConnection('www.reddit.com')
		self.parser = RedditHTMLParser()

	def get_info(self, subreddit):
		try:
			_log.debug('GET ' + '/r/%s/' % subreddit.lower())
			self.connection.request('GET', '/r/%s/' % subreddit.lower())
			html = self.connection.getresponse().read()
		except Exception as e:
			_log.error("Unable to get subreddit '%s'\n%s" % (subreddit, e))
			return
		self.parser.reset()
		self.parser.feed(html)
		reddits = set()
		for link, name in zip(self.parser.Links, self.parser.LinkNames):
			link = link.strip()
			name = name.strip()
			if link.find(' ') != -1:
				continue
			elif link.startswith('http://www.reddit.com/r/'):
				reddit = link[24:]
			elif link.startswith('/r/'):
				reddit = link[3:]
			elif name.find(' ') != -1:
				continue
			elif name.startswith('http://www.reddit.com/r/'):
				reddit = name[24:]
			elif name.startswith('www.reddit.com/r/'):
				reddit = name[17:]
			elif name.startswith('reddit.com/r/'):
				reddit = name[13:]
			elif name.startswith('/r/'):
				reddit = name[3:]
			elif name.startswith('r/'):
				reddit = name[2:]
			else:
				continue
			if reddit[-1] == '/':
				reddit = reddit[:-1]
			if reddit.find('/') == -1:
				_log.debug('Found subreddit: %s' % reddit.lower())
				reddits.add(reddit.lower())
		return reddits, self.parser.Subscribers

	def __del__(self):
		self.parser.close()
		self.connection.close()

def visit(subreddit, visited, tab):
	if subreddit in visited:
		return visited
	tabs = ''.join(['\t' for i in xrange(tab)])
	_log.debug(tabs + subreddit)
	visited.add(subreddit)
	info = parser.get_info(subreddit)
	if not info or len(info) < 1:
		return visited
	links, subs = info
	for l in links:
		visited = visit(l, visited, tab+1)
	return visited

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	_log = logging.getLogger("RedditParser")
	if len(argv) < 2 or (argv[1] == '-r' and len(argv) < 3):
		_log.error('No subreddit input found.\n'
				'Usage: %s subreddit [subreddit2 [...]]' % argv[0])
		exit(1)
	parser = RedditParser()
	rec = argv[1] == '-r'
	if rec:
		args = argv[2:]
	else:
		args = argv[1:]
	for subreddit in args:
		if rec:
			visit(subreddit, set(), 0)
		else:
			_log.debug('SUBREDDIT: %s' % subreddit)
			links, subscribers = parser.get_info(subreddit)
			_log.debug('\tSUBSCRIBERS: %s' % subscribers)
			if links:
				for link in links:
					_log.debug('\t%s' % link)
			_log.debug("")
