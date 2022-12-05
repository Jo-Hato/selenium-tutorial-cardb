import requests
import bs4 as bs
url = 'https://rank.greeco-channel.com/diamtire/'
 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
r = requests.get(url, headers=headers)
 
print(r.status_code)
