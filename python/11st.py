import db
from selenium import webdriver
import time
from bs4 import BeautifulSoup

driver_path = "/Users/chromedriver.exe"
driver = webdriver.Chrome(driver_path)

BASE_URL = "http://search.11st.co.kr/Search.tmall"
SORT = "ab=A#sortCd%%L"
crawling_site = "11번가"

sql = db.mysql('localhost', 'root', '1234', 'crawler')
query = "select distinct keyword, category from kmugstore_data where category = 'AppleWatch' order by idx asc"


rows = sql.get_results(query)
for column in rows:
    keyword = column[0]
    category = column[1]

    url = f"{BASE_URL}?kwd={keyword}&{SORT}"
    driver.get(url)
    time.sleep(2)
    result = driver.page_source
    soup = BeautifulSoup(result, 'html.parser')

    pages = soup.find("div", {"id": "list_paging"}).find_all("a")

    for page in range(len(pages) + 1):
        page = page + 1
        if page != 1:
            driver.get(f"{url}$$pageNum%%{page}")
            time.sleep(2)
            result = driver.page_source
            soup = BeautifulSoup(result, "html.parser")
        box = soup.find("div", {"id": "product_listing"}).find(
            "ul", {"class": "tt_listbox"})
        lists = box.find_all("li")
        for li in lists:
            sub_url = li.find("div", {"class": "list_info"}).find(
                "p", {"class": "info_tit"}).find("a")["href"]

            driver.get(sub_url)
            sub_result = driver.page_source
            sub_soup = BeautifulSoup(sub_result, 'html.parser')
            price = int(sub_soup.find("div", {"class": "prdc_default_info"}).find(
                "strong", {"class": "sale_price"}).get_text(strip=True).replace(",", ""))
            if price < 190000:
                continue
            title = sub_soup.find("div", {"class": "heading"}).find(
                "h2").get_text(strip=True)
            saler = sub_soup.find(
                "a", {"class": "seller_nickname"}).get_text(strip=True)
            fee = sub_soup.find("div", {"class": "row"}).find(
                "div", {"class": "col"}).get_text(strip=True).split(" ")[2].replace(",", "").replace("원", "")
            if fee == "무료":
                fee = 0
            else:
                fee = int(fee)
            product_url = sub_url
            now = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time()))

            insert_query = f"""
                            INSERT INTO ecommerce_data
                            SET productName = '{title}',
                            keyword = '{keyword}',
                            price = {price},
                            fee = {fee},
                            productUrl = '{product_url}',
                            crawlingTime = '{now}',
                            crawlingSite = '{crawling_site}',
                            saler = '{saler}'
                            """
            sql.query(insert_query)
sql.close()
driver.close()
driver.quit()
