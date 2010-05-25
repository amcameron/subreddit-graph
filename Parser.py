#!/usr/bin/env python
from sys import exit,stderr,argv
from urllib2 import urlopen
from HTMLParser import HTMLParser

def lineError(s,k=None):
	stderr.write(argv[0]+': '+s+'\n')
	if k: exit(k)

class RedditParser(HTMLParser):
	Record = False
	Depth = 0
	Links = []
	
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
		lineError('Unable to get subreddit "%s"' % subreddit)
		lineError(e,1)
	html = html[html.find('>')+1:]
	parser = RedditParser()
	parser.feed(html)
	reddits = []
	for link in parser.Links:
		if link[:24]=='http://www.reddit.com/r/':
			reddit = link[24:]
			if reddit[-1]=='/': reddit = reddit[:-1]
			reddits.append(reddit.lower())
	return reddits

if __name__=="__main__":
	if len(argv)<2:
		lineError('No subreddit input found')
		lineError('Usage: %s subreddit [subreddit2 [...]]',1)
	for subreddit in argv[1:]:
		print 'SUBREDDIT: %s' % subreddit
		for link in grab_links(subreddit):
			print '\t%s' % link
		print 
