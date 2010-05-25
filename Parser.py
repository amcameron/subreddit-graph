#!/usr/bin/env python
from sys import exit,argv
from logging import error
from urllib2 import urlopen
from HTMLParser import HTMLParser

class RedditParser(HTMLParser):
	
	def __init__(self):
		HTMLParser.__init__(self)
		self.Record = False
		self.RecordSub = False
		self.RecordLink = False
		self.Depth = 0
		self.Subscribers = 0
		self.Links = []
		self.LinkNames = []
	
	def handle_starttag(self,tag,attrs):
		if tag=='div' and ('class','usertext-body') in attrs: self.Record = True
		if tag=='span' and ('class','number') in attrs: self.RecordSub = True
		if not self.Record: return
		if tag=='div': self.Depth += 1
		elif tag=='a':
			for (a,v) in attrs:
				if a=='href':
					self.RecordLink = True
					self.Links.append(v)
	
	def handle_data(self,data):
		if self.RecordSub: self.Subscribers = int(data.replace(',',''))
		if self.RecordLink:
			self.LinkNames.append(data)
			self.RecordLink = False
	
	def handle_endtag(self,tag):
		if self.Record and tag=='div':
			self.Depth -= 1
			self.Record = self.Depth!=0
		else: self.RecordSub = False

def get_info(subreddit):
	site = 'http://www.reddit.com/r/%s/' % subreddit.lower()
	try: html = urlopen(site).read()
	except Exception as e:
		error("Unable to get subreddit '%s'\n%s" % (subreddit,e))
		return
	parser = RedditParser()
	parser.feed(html)
	reddits = set()
	for link,name in zip(parser.Links,parser.LinkNames):
		link = link.strip()
		if link.find(' ')!=-1: continue
		elif link[:24]=='http://www.reddit.com/r/': reddit = link[24:]
		elif link[:3]=='/r/': reddit = link[3:]
		elif name.find(' ')!=-1: continue
		elif name[:24]=='http://www.reddit.com/r/': reddit = name[24:]
		elif name[:17]=='www.reddit.com/r/': reddit = name[17:]
		elif name[:13]=='reddit.com/r/': reddit = name[13:]
		elif name[:3]=='/r/': reddit = name[3:]
		elif name[:2]=='r/': reddit = name[2:]
		else: continue
		if reddit[-1]=='/': reddit = reddit[:-1]
		if reddit.find('/')!=-1: continue
		reddits.add(reddit.lower())
	return reddits,parser.Subscribers

if __name__=="__main__":
	if len(argv)<2:
		error('No subreddit input found.\n' +
				'Usage: %s subreddit [subreddit2 [...]]' % argv[0])
		exit(1)
	for subreddit in argv[1:]:
		print 'SUBREDDIT: %s' % subreddit
		links,subscribers = get_info(subreddit)
		print '\tSUBSCRIBERS: %s' % subscribers
		if links:
			for link in links: print '\t%s' % link
		print 
