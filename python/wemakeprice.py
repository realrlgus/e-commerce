import db
import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "https://search.wemakeprice.com/search"
SORT = "sort=cheap"

sql = db.mysql('localhost', 'root', '1234', 'crawler')
query = "select keyword, category from kmugstore_data order by idx asc LIMIT 0, 1"


rows = sql.get_results(query)

for column in rows:
    keyword = column[0]
    category = column[1]

    url = f"{BASE_URL}?keyword={keyword}&{SORT}"
    print(url)
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    box = soup.find("ul", {"class": "tt_listbox"})
    print(box)
