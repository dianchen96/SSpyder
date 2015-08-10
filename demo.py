import sys
import urllib
import urllib2
from bs4 import BeautifulSoup


###################################
########   Spyder Classes   #######
###################################

class Spyder:

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

	def search(self, keyword, item = 10, baseUrl = self.baseUrl, ):
		count = 0
		url = baseUrl + keyword
		try:
			while count < item:
				request = urllib2.Request(url, headers = self.headers)
				html = urllib2.urlopen(request).read()
				soup = BeautifulSoup(html, 'html.parser')
				for tag in soup.find_all('div', class_ = self.tag):
					count += 1
					# print(tag)
					yield tag
					if count >= item:
						return;
				url = baseUrl + keyword + self.nextUrl(count)
				print(url)
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

	def search_id(self, id):
		url = ''
		request = urllib2.Request(url, headers = self.headers)
		html = urllib2.urlopen(request).read()
		soup = BeautifulSoup(html, 'html.parser')

class TiebaSpyder(EngineSpyder):
	def __init__(self):
		self.base = 'http://tieba.baidu.com'
		self.baseUrl = self.base + '/f/search/res?qw='
		self.tag = 's_post'
		self._nextUrl = '&pn='

	def search_results(self, keyword, item = 10):
		for tag in self.search(keyword, item):
			yield {'title': tag.a.text, 'url': self.base + tag.a['href']}

	def search_id(self, keyword):
		url = 'http://tieba.baidu.com/f/search/ures?sm=1&un=' + urllib.quote(keyword.decode(sys.stdin.encoding).encode('gbk'))
		request = urllib2.Request(url, headers = self.headers)
		html = urllib2.urlopen(request).read()
		soup = BeautifulSoup(html, 'html.parser')
		for tag in soup.find_all('div', class_ = self.tag):
			yield {'title': tag.a.text}

	def nextUrl(self, count):
		return self._nextUrl + str((count / 10) + 1) 


####################################
#######  Terminal Testing    #######
####################################

def google(keyword):
	for tag in GoogleSpyder().search_results(keyword):
		print(tag['title'])
		print(tag['url'])
		print('-'*50)

def baidu(keyword):
	for tag in BaiduSpyder().search_results(keyword):
		print(tag['title'])
		print(tag['url'])
		print('-'*50)

def tieba(keyword):
	for tag in TiebaSpyder().search_results(keyword, 20):
		print(tag['title'])
		print(tag['url'])
		print('-'*50)




###################################
##########  Utilities   ###########
###################################
