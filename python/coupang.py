import requests
from bs4 import BeautifulSoup

url = "https://www.coupang.com/np/search?q=MVVK2KH%2FA"

result = requests.get(url)
soup = BeautifulSoup(result.text, 'html.parser')

print(soup)
