
import sys
import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup

import WeiboEncode
import WeiboSearch

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
		self.url =  urllib2.urlopen(request).geturl()


class RenrenSpyder(LoginSpyder):
	def __init__(self, username, password):
		super(RenrenSpyder, self).__init__(username, password)
		self.domain = 'renren.com'
		self.loginUrl = 'http://www.renren.com/PLogin.do'
		self.loginParams = {'domain': self.loginUrl, 'email': self.username, 'password': self.password}


	def search_id(self, keyword, item = 10):	
		for tag in EngineSpyder(baseUrl = 'http://browse.renren.com/s/all?from=opensearch&q=', tag = 'list-mod').search(keyword, item, nextpage = False):
			yield {'name': tag.p.a.text, 'img':tag.a.img['data-src'], 'url': tag.a['href']}

	def person_timeline(self, person, y_range, m_range):
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
					request = urllib2.Request(full_url, headers = self.headers)
					html = urllib2.urlopen(request).read()
					soup = BeautifulSoup(html, 'html.parser')
					for tag in soup.find_all('section', class_ = 'tl-a-feed'):
						yield 
				except urllib2.URLError, e:
					pass

	def archive_page(self, ownerid, html, date):
		with open('G:/academics/spyder/'+ownerid+'/'+date+'.html', 'wb') as file_:
			print('Archiving '+ ownerid +', as of ' + date + '  ...')
			file_.write(html)

# Since Weibo changes encription ways, this maybe subject to change
class WeiboSpyder(LoginSpyder):
	def __init__(self, username, password):
		super(WeiboSpyder, self).__init__(username, password)
		self.loginUrl = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

	def login(self):
		# Prelogin
		data = {'entry': 'weibo', 'callback': 'sinaSSOController.preloginCallBack', 'rsakt': 'mod'}
		serverUrl = 'http://login.sina.com.cn/sso/prelogin.php?' + urllib.urlencode(data)
		serverData = urllib2.urlopen(serverUrl).read()
		serverTime, nonce, pubkey, rsakv = WeiboSearch.getServerData(serverData)
		self.loginParams = WeiboEncode.encodePost(self.username, self.password, serverTime, nonce, pubkey, rsakv)
		# Login
		request = urllib2.Request(self.loginUrl, urllib.urlencode(self.loginParams), headers = self.headers)
		text = urllib2.urlopen(request).read()
		try:
			urllib2.urlopen(WeiboSearch.getRedirectData(text))
			self.url = 'http://d.weibo.com/?from=signin'
		except:
			print('Login Weibo error!')


# a = WeiboSpyder('dianchen96@gmail.com', 'chendian6996')
# a.login()
# html = urllib2.urlopen(a.url).read()
# with open('G:/academics/spyder/1.html', 'wb') as file_:
# 	file_.write(html)

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

def renren_profile(keyword):
	a = RenrenSpyder('dianchen96@berkeley.edu', 'cczx691')
	a.login()
	for tag in a.person_timeline({'url': keyword}, range(2013, 2014), range(1, 13)):
		print(tag)

###################################
########## Tests  #################
###################################


###################################
##########  Utilities   ###########
###################################
