import urllib
import base64  
import rsa  
import binascii 

########## Subject to change when encryption changes ########### 
def encodePost(username, password, serverTime, nonce, pubkey, rsakv):
	# Encode username
	usernameEncoded = base64.encodestring(urllib.quote(username))[:-1]  
  	key = rsa.PublicKey(int(pubkey, 16), 65537)
  	message = str(serverTime) + '\t' + str(nonce) + '\n' + str(password)   
  	# Encode password
  	pwdEncoded = binascii.b2a_hex(rsa.encrypt(message, key))   
  	postParams = {  
		'entry': 'weibo',  
		'gateway': '1',  
		'from': '',  
		'savestate': '7',  
		'userticket': '1',  
		'vsnf': '1',  
		'su': usernameEncoded,  
		'service': 'miniblog',  
		'servertime': serverTime,  
		'nonce': nonce,  
		'pwencode': 'rsa2',  
		'sp': pwdEncoded,  
		'encoding': 'UTF-8',  
		'prelt': '432',  
		'rsakv': rsakv,       
		'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',  
		'returntype': 'META'  
	}
	return postParams
