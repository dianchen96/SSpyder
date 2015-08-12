
import sys
import urllib
import urllib2
from bs4 import BeautifulSoup

import cookielib
import re
import os

## Archiving ##
# import codecs

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

	def __init__(self, baseUrl = None, tag = None, _nextUrl = None):
		self.baseUrl = baseUrl
		self.tag = tag
		self._nextUrl = _nextUrl

	def search(self, keyword, item = 10, nextpage = True):
		count = 0
		url = self.baseUrl + keyword
		try:
			while count < item:
				request = urllib2.Request(url, headers = self.headers)
				html = urllib2.urlopen(request).read()
				soup = BeautifulSoup(html, 'html.parser')
				results = soup.find_all('div', class_ = self.tag)
				if len(results) == 0:
					return 
				for tag in results:
					count += 1
					yield tag
					if count >= item:
						return;
				if nextpage:
					url = self.baseUrl + keyword + self.nextUrl(count)
				else:
					return
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
		self.url = urllib2.urlopen(request).geturl()


class RenrenSpyder(LoginSpyder):
	def __init__(self, username, password):
		super(RenrenSpyder, self).__init__(username, password)
		self.domain = 'renren.com'
		self.loginUrl = 'http://www.renren.com/PLogin.do'
		self.loginParams = {'domain': self.loginUrl, 'email': self.username, 'password': self.password}


	def search_id(self, keyword, item = 10):	
		for tag in EngineSpyder(baseUrl = 'http://browse.renren.com/s/all?from=opensearch&q=', tag = 'list-mod').search(keyword, item, nextpage = False):
			yield {'name': tag.p.a.text, 'img':tag.a.img['data-src'], 'url': tag.a['href']}

	def archive_person(self, person, y_range, m_range):
		url = 'http://www.renren.com/timelinefeedretrieve.do?'
		ownerid = re.compile(r"\d{9}").search(person['url']).group(0)
		# print(ownerid)
		data = {'ownerid': ownerid, 'render': '0', 'begin': '0', 'limit': 30, 'isAdmin': 'true'}
		for year in y_range:
			data['year'] = str(year)
			for month in m_range:
				data['month'] = str(month)
				try:
					full_url = url + urllib.urlencode(data)
					# print(full_url)
					request = urllib2.Request(full_url, headers = self.headers)
					html = urllib2.urlopen(request).read()
					self.archive_page(ownerid, html, str(year)+'-'+str(month))
				except urllib2.URLError, e:
					pass

	def archive_page(self, ownerid, html, date):
		with open('G:/academics/spyder/'+ownerid+'/'+date+'.html', 'wb') as file_:
			print('Archiving '+ ownerid +', as of ' + date + '  ...')
			file_.write(html)
		# soup = BeautifulSoup(html)
		# return [{} for tag in soup.find_all('sec')]



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

def renren_id(keyword):
	a = RenrenSpyder('dianchen96@berkeley.edu', 'cczx691')
	a.login()
	for tag in a.search_id(keyword):
		print(tag['name'])
		print(tag['img'])
		print('-'*50)

def main():
	a = RenrenSpyder('dianchen96@berkeley.edu', 'cczx691')
	a.login()
	print "\nWelcome to Renren Archiver\n"
	ownerid =raw_input("Enter the Renren profile ID: ")
	path = raw_input("Enter the directory you want to archive: ")
	start = raw_input("Enter the start year you want to archive: ")
	end = raw_input("Enter the end year you want to archive: ")
	try:
		os.stat(path)
	except:
		os.mkdir(path)   
	a.archive_person({'url': ownerid}, range(int(start), int(end)+1), range(1, 13))
	print('Done ')

main()

###################################
########## Tests  #################
###################################

def renren_archive():
	url = 'http://www.renren.com/361513136/profile?ref=searchresult_0&q=\u9648\u7EFF\u7B71|p=|s=0|u=470629775&act=name&rt=user&in=0&ft=2&hh=1'







###################################
##########  Utilities   ###########
###################################
