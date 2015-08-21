# Acknowlege: http://54rd.net/html/2015/python_0312/69.html\

import re
import json

def getServerData(serverData):
	p = re.compile('\((.*)\)')  
	jsonData = p.search(serverData).group(1)
	data = json.loads(jsonData) 
	serverTime = str(data['servertime'])  
	nonce = data['nonce']  
	pubkey = data['pubkey']  
	rsakv = data['rsakv']		
	return serverTime, nonce, pubkey, rsakv  	

def getRedirectData(text):
	p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')  
	loginUrl = p.search(text).group(1)  
	return loginUrl  

def getSearchedData(page_content, tag_expr, expr, tag = 'pid'):
	p = re.compile(expr, re.MULTILINE)
	tag_re = re.compile(tag_expr)
	for script in p.findall(page_content):
		view_json = json.loads(script)
		if 'html' in view_json and tag_re.match(view_json[tag]):
			return view_json['html']