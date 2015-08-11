
import sys
import urllib
import urllib2
from bs4 import BeautifulSoup

import cookielib


###################################
########   Spyder Classes   #######
###################################

class Spyder(object):

	user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'  
	headers = {'User-Agent': user_agent}


###################################
####   Engine Spyder Classes   ####
###################################

class EngineSpyder(Spyder):

	def __init__(self):
		self.baseUrl = None
		self.tag = None
		self._nextUrl = None

	def search(self, keyword, item = 10):
		count = 0
		url = self.baseUrl + keyword
		try:
			while count < item:
				request = urllib2.Request(url, headers = self.headers)
				# print(url)
				html = urllib2.urlopen(request).read()
				# print(html)
				soup = BeautifulSoup(html, 'html.parser')
				for tag in soup.find_all('div', class_ = self.tag):
					count += 1
					# print(tag)
					yield tag
					if count >= item:
						return;
				url = self.baseUrl + keyword + self.nextUrl(count)
		except urllib2.URLError, e:
			if hasattr(e,"code"):
			    print e.code
			if hasattr(e,"reason"):
			    print e.reason

	def nextUrl(self, count):
		return self._nextUrl + str(count)


class GoogleSpyder(EngineSpyder):
	def __init__(self):
		self.baseUrl = 'https://www.google.com/search?q='
		self.tag = 'g'
		self._nextUrl = '&start='

	def search_results(self, keyword, item = 10):
		for tag in self.search(urllib.quote(keyword.decode('gbk').encode('utf-8')), item):
			yield {'title': tag.a.text, 'url': tag.a['href']}


class BaiduSpyder(EngineSpyder):
	def __init__(self):
		self.baseUrl = 'https://www.baidu.com/s?wd='
		self.tag = 'result'
		self._nextUrl = '&pn='

	def search_results(self, keyword, item = 10):
		for tag in self.search(urllib.quote(keyword.decode(sys.stdin.encoding).encode('gbk')), item):
			yield {'title': tag.h3.a.text, 'url': tag.h3.a['href']}

class TiebaSpyder(EngineSpyder):
	def __init__(self):
		self.base = 'http://tieba.baidu.com'
		self.baseUrl = self.base + '/f/search/res?qw='
		self.tag = 's_post'
		self._nextUrl = '&pn='

	def search_results(self, keyword, item = 10):
		for tag in self.search(keyword, item):
			yield {'title': tag.a.text, 'url': self.base + tag.a['href']}

	def nextUrl(self, count):
		return self._nextUrl + str((count / 10) + 1) 

class TiebaIDSpyder(TiebaSpyder):
	def __init__(self, item=10):
		self.item = item
		self.base = 'http://tieba.baidu.com'
		self.baseUrl = self.base + '/f/search/ures?sm=1&rn=' + str(self.item) +'&un='
		self.tag = 's_post'
		self._nextUrl = '&pn='

	def search_results(self, keyword):
		for tag in self.search(urllib.quote(keyword.decode(sys.stdin.encoding).encode('gbk')), self.item):
			yield {'title': tag.a.text, 'url': self.base + tag.a['href'], 'content': tag.div.text}


class LoginSpyder(Spyder):
	def __init__(self, username, password):
		# URL Related 
		self.url = None
		self.domain = None
		self.loginUrl = None
		# Info Related
		self.loginParams = None
		self.username = username
		self.password = password
		# Set Cookie Jar
		self.cookieJar = cookielib.LWPCookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
		urllib2.install_opener(self.opener)

	def login(self):
		request = urllib2.Request(self.loginUrl, urllib.urlencode(self.loginParams), headers = self.headers)
		return urllib2.urlopen(request).geturl()


class RenrenSpyder(LoginSpyder):
	def __init__(self, username, password):
		super(RenrenSpyder, self).__init__(username, password)
		self.domain = 'renren.com'
		self.loginUrl = 'http://www.renren.com/PLogin.do'
		self.loginParams = {'domain': self.loginUrl, 'email': self.username, 'password': self.password}



####################################
#######  Terminal Testing    #######
####################################

def google(keyword):
	for tag in GoogleSpyder().search_results(keyword):
		print(tag['title'])
		print(tag['url'])
		print('-'*50)

def baidu(keyword):
	for tag in BaiduSpyder().search_results(keyword, 20):
		print(tag['title'])
		print(tag['url'])
		print('-'*50)

def tieba(keyword):
	for tag in TiebaSpyder().search_results(keyword, 20):
		print(tag['title'])
		print(tag['url'])
		print('-'*50)

def tieba_id(keyword):
	for tag in TiebaIDSpyder(20).search_results(keyword):
		print(tag['title'])
		print(tag['url'])
		print(tag['content'])
		print('-'*50)


###################################
########## Tests  #################
###################################
a = RenrenSpyder('18672356725', 'chendian6996')
print(a.loginParams)
print(a.login())






###################################
##########  Utilities   ###########
###################################
