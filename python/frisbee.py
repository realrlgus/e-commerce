import time
import db
import requests
import requests
from bs4 import BeautifulSoup


def frisbeestore_crawling():
    sql = db.mysql('localhost', 'root', '1234', 'crawler')
    query = "select product_partnum, product_category from product_part"
    rows = sql.get_results(query)

    BASE_URL = "https://www.frisbeekorea.com"

    for column in rows:
        keyword = column[0]
        category = column[1]
        print(f"Crawling {keyword}...")
        site = "프리스비"
        url = f"{BASE_URL}/goods/goods_search.php?keyword={keyword}"
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "html.parser")
        items = soup.find("div", {"class": "list"}).find_all("li")
        if items is not None:
            for item in items:
                sub_item = item.find("div", {"class": "txt"}).find("a")
                title = sub_item.find("strong").get_text(
                    strip=True).replace("'", "\\'")
                price = item.find("span", {"class": "cost"}).find(
                    "strong").get_text(strip=True).replace(",", "").replace("원", "")
                sub_a = sub_item["href"].replace("..", "")
                sub_link = f"{BASE_URL}{sub_a}"

                sub_result = requests.get(sub_link)
                sub_soup = BeautifulSoup(sub_result.text, "html.parser")

                fee = int(sub_soup.find("li", {"class": "delivery"}).find("div").find(
                    "span").get_text(strip=True).replace(",", "").replace("원", ""))
                now = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time()))
                insert_query = f"""
                                    INSERT INTO crawling_data
                                    SET productName = '{title}',
                                    keyword = '{keyword}',
                                    price = {price},
                                    fee = {fee},
                                    category = '{category}',
                                    productUrl = '{sub_link}',
                                    crawlingTime = '{now}',
                                    crawlingSite = '{site}'
                                    """
                sql.query(insert_query)
        print(f"Crawling {keyword} Complete!")

    sql.close()
