#!/usr/bin/env python
from sys import exit,argv
from logging import error
from HTMLParser import HTMLParser
from httplib import HTTPConnection

class RedditHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.reset2()
	
	def reset2(self):
		self.Record = False
		self.RecordSub = False
		self.RecordLink = False
		self.Depth = 0
		self.Subscribers = 0
		self.Links = []
		self.LinkNames = []
	
	def reset3(self):
		self.reset()
		self.reset2()
	
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

class RedditParser:
	def __init__(self):
		self.c = HTTPConnection('www.reddit.com')
		self.r = RedditHTMLParser()
	
	def get_info(self,subreddit):
		try:
			self.c.request('GET','/r/%s/' % subreddit.lower())
			html = self.c.getresponse().read()
		except Exception as e:
			error("Unable to get subreddit '%s'\n%s" % (subreddit,e))
			return
		self.r.reset3()
		self.r.feed(html)
		reddits = set()
		for link,name in zip(self.r.Links,self.r.LinkNames):
			link = link.strip()
			name = name.strip()
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
			if reddit.find('/')==-1: reddits.add(reddit.lower())
		return reddits,self.r.Subscribers
	
	def __del__(self):
		self.r.close()
		self.c.close()

def visit(subreddit,visited,tab):
	if subreddit in visited: return visited
	tabs = ''.join(['\t' for i in xrange(tab)])
	print tabs+subreddit
	visited.add(subreddit)
	i = r.get_info(subreddit)
	if not i or len(i)<1: return visited
	ls,s = i
	for l in ls: visited = visit(l,visited,tab+1)
	return visited

if __name__=="__main__":
	if len(argv)<2 or (argv[1]=='-r' and len(argv)<3):
		error('No subreddit input found.\n'+
				'Usage: %s subreddit [subreddit2 [...]]' % argv[0])
		exit(1)
	r = RedditParser()
	rec = argv[1]=='-r'
	if rec: args = argv[2:]
	else: args = argv[1:]
	for subreddit in args:
		if rec: visit(subreddit,set(),0)
		else:
			print 'SUBREDDIT: %s' % subreddit
			links,subscribers = r.get_info(subreddit)
			print '\tSUBSCRIBERS: %s' % subscribers
			if links:
				for link in links: print '\t%s' % link
			print 
