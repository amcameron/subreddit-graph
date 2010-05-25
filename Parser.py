#!/usr/bin/env python
from sys import exit,stderr,argv
import logging
from urllib2 import urlopen
from HTMLParser import HTMLParser

class RedditParser(HTMLParser):
	
	def __init__(self):
		HTMLParser.__init__(self)
		self.Record = False
		self.Depth = 0
		self.Links = []
	
	def handle_starttag(self,tag,attrs):
		if tag=='div' and ('class','usertext-body') in attrs: self.Record = True
		if not self.Record: return
		if tag=='div': self.Depth += 1
		elif tag=='a':
			for (a,v) in attrs:
				if a=='href': self.Links.append(v)
	
	def handle_endtag(self,tag):
		if self.Record and tag=='div':
			self.Depth -= 1
			self.Record = self.Depth!=0

def grab_links(subreddit):
	site = 'http://www.reddit.com/r/%s/' % subreddit.lower()
	try: html = urlopen(site).read()
	except Exception,e:
		logging.error("Unable to get subreddit '%s'" % subreddit)
		return set()
	parser = RedditParser()
	parser.feed(html)
	reddits = set()
	for link in parser.Links:
		found = False
		if link[:24]=='http://www.reddit.com/r/':
			reddit = link[24:]
			found = True
		elif link[:3]=='/r/':
			reddit = link[3:]
			found = True
		if found:
			if reddit[-1]=='/': reddit = reddit[:-1]
			if reddit.find('/')!=-1: continue
			reddits.add(reddit.lower())
	return reddits

if __name__=="__main__":
	if len(argv)<2:
		logging.error('No subreddit input found.\n' +
				'Usage: %s subreddit [subreddit2 [...]]')
		import sys
		sys.exit(1)
	for subreddit in argv[1:]:
		print 'SUBREDDIT: %s' % subreddit
		for link in grab_links(subreddit):
			print '\t%s' % link
		print 
