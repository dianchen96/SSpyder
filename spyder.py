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

	user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36' 
	# user_agent = 'Magic Browser' 
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
				print(url)
				request = urllib2.Request(url, headers = self.headers)
				html = urllib2.urlopen(request).read()
				soup = BeautifulSoup(html, 'lxml')
				results = soup.find_all('div', class_ = self.tag)
				if len(results) == 0:
					return 
				for tag in results:
					count += 1
					print(tag)
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
					print('[Renren] Error retrieving data from '+ ownerid +' '+str(year) + '-' + str(month))
					pass

	def archive_page(self, ownerid, html, date):
		with open('G:/academics/spyder/'+ownerid+'/'+date+'.html', 'wb') as file_:
			print('Archiving '+ ownerid +', as of ' + date + '  ...')
			file_.write(html)

# Since Weibo changes encryption ways, this maybe subject to change
class WeiboSpyder(LoginSpyder):
	def __init__(self, username, password):
		super(WeiboSpyder, self).__init__(username, password)
		## Below is for logging into web Weibo
		# self.loginUrl = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
		self.loginUrl = 'http://login.weibo.cn'
		# Prelogin
		login_html = urllib2.urlopen(urllib2.Request('http://login.weibo.cn', headers = self.headers)).read()
		print(login_html)
		login_soup = BeautifulSoup(login_html)
		# password_key = login_soup.find('input', type_ = 'password')
		print(password_key)
		vk = login_soup.find('input', attr = {'name': 'vk'})['value']
		self.loginParams = {'mobile': self.username, 
												password_key: self.password, 
												'remember': 'on',
												'vk': vk,
												'backURL': 'http%3A%2F%2Fweibo.cn',
												'backTitle': '%E6%89%8B%E6%9C%BA%E6%96%B0%E6%B5%AA%E7%BD%91',
												'submit': '%E7%99%BB%E5%BD%95'
												}
		


	def search_user(self, keyword, gender = None, region = None, age = None, item = 10):
		keyword = urllib.quote(keyword.decode(sys.stdin.encoding).encode('utf-8'))
		if region:
			keyword = keyword + '&region=' + region
		if gender:
			keyword = keyword + '&gender=' + gender
		if age:
			keyword = keyword + 'age=' + age 
		html = WeiboSearch.getSearchedData(urllib2.urlopen('http://s.weibo.com/user/' + keyword).read(), 'pl_user_feedList', '<script>STK && STK.pageletM && STK.pageletM.view\((.*)\)</script>')
		soup = BeautifulSoup(html, 'lxml')
		for tag in soup.find_all('div', class_ = 'list_person'):
			desr = tag.find('div', class_ = 'person_info').text.splitlines()[2].strip(' \t\n\r')
			img = tag.img['src']
			name = tag.p.a.text.strip()
			uid = tag.p.a['uid']
			tags = [[subsubtag.text.strip() for subsubtag in subtag.findAll('a')] for subtag in tag.findAll('p', class_ = 'person_label')]
			yield {'img': img, 'name': name, 'uid': uid, 'desr': desr, 'tags': tags}

	def search_timeline(self, uid, item = 50):
		for tag in EngineSpyder(baseUrl = 'http://weibo.cn/u/', tag = 'c').search(uid, item, nextpage = True):
			# Content of Weibo 
			content = tag.find('span', class_ = 'ctt').text
			# Repost of Weibo
			repost = tag.find('span', class_ = 'cmt')
			text = repost.text if repost else None
			info = tag.find('span', class_ = 'ct')
			date = tag.find(' span', )
			yield {'content': content, 'repost': repost, 'device': device}



####################################
#######   Terminal Testing    ######
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

def weibo_user(keyword):
	a = WeiboSpyder('dianchen96@gmail.com', 'chendian6996')
	a.login()
	for tag in a.search_user(keyword):
		print(tag['name'])
		print(tag['uid'])
		print(tag['desr'])
		print(tag['img'])
		for a in tag['tags']:
			for b in a:
				print(b)
		print('-'*50)

a = WeiboSpyder('dianchen96@gmail.com', 'chendian6996')
a.login()

# url = 'http://weibo.cn'
# b = urllib2.Request(url, headers = Spyder.headers)
# print(urllib2.urlopen(b).read())
for tag in a.search_timeline('4aadcom'):
	print(tag['content'])
	print(tag['repost'])
	print(tag['date'])
	print(tag['device'])
	print('-'*50)

###################################
########## Tests  #################
###################################

