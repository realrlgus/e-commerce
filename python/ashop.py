import time
import db
import requests
import requests
from bs4 import BeautifulSoup


def ashopstore_crawling():
    sql = db.mysql('localhost', 'root', '1234', 'crawler')
    query = "select product_partnum, product_category from product_part"
    rows = sql.get_results(query)

    BASE_URL = "http://www.theashop.co.kr/shop"

    for column in rows:
        keyword = column[0]
        category = column[1]
        print(f"Crawling {keyword}...")
        site = "에이샵"
        url = f"{BASE_URL}/goods/goods_search.php?searched=Y&skey=all&sword={keyword}"
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "html.parser")
        items = soup.find("td", {"style": "padding:15 0"}).find("table", {"width": "1100px"}).find(
            "tr").find_all("td")
        if items is not None:
            for item in items:
                sub_item = item.find(
                    "div", {"style": "padding:5 16"}).find("a")
                title = sub_item.get_text(strip=True).replace("'", "\\'")
                sub_a = sub_item["href"].replace("..", "")
                sub_link = f"{BASE_URL}{sub_a}"

                sub_result = requests.get(sub_link)
                sub_soup = BeautifulSoup(sub_result.text, "html.parser")

                price = int(sub_soup.find("span", {"id": "price"}).get_text(
                    strip=True).replace(",", ""))
                fee = 0
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
