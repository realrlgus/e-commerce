import db
import requests
import time
from bs4 import BeautifulSoup


def kmugstore_crawling():
    sql = db.mysql('localhost', 'root', '1234', 'crawler')

    query = "select product_partnum, product_category from product_part"
    rows = sql.get_results(query)

    BASE_URL = "http://www.theashop.co.kr/shop/goods/goods_search.php?searched=Y&skey=all&"

    for column in rows:
        partnum = column[0]
        category = column[1]
        url = f"{BASE_URL}&sword={partnum}"
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "html.parser")

        items = soup.find_all("td", {"class": "padding:15 0"})
        for item in items:
            # TODO
            page = page + 1
            if page != 1:
                result = requests.get(f"{url}&page={page}")
                soup = BeautifulSoup(result.text, "html.parser")
            tables = soup.find_all(
                "td", {"style": "border-right:0px solid #e1e1e1;"})
            for table in tables:
                sub_link = table.find("a")["href"].replace("..", "")
                sub_result = requests.get(f"{BASE_URL}{sub_link}")
                sub_soup = BeautifulSoup(sub_result.text, "html.parser")
                title = sub_soup.find("div", {
                    "style": "font-size:17px; font-weight:bold; line-height:48px; border-bottom:solid 2px #e0e0e0;"}).get_text(strip=True).replace("'", "\\'")
                keyword_idx = title.find("/A")
                if not keyword_idx == -1:
                    keyword_idx_start = keyword_idx - 7
                    keyword_idx_end = keyword_idx + 2
                    keyword = title[keyword_idx_start:keyword_idx_end]
                else:
                    if category == "iPhone":
                        keyword = title.split("-")[-1].strip()
                    else:
                        continue
                price = int(sub_soup.find("span", {"id": "price"}).get_text(
                    strip=True).replace(",", ""))
                fee = sub_soup.find(
                    "td", {"style": "font-size:15px; font-weight:normal;"}).get_text(strip=True)

                if fee == "무료배송":
                    fee = 0
                else:
                    fee = int(fee)
                image_url = sub_soup.find("img", {"id": "objImg"})["src"]
                if image_url.find("../") != -1:
                    replace_image_url = image_url.replace("..", "")
                    image_url = f"{BASE_URL}{replace_image_url}"
                image_url = image_url.replace(
                    "http://", "https://").replace("'", "\\'")

                now = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time()))

                insert_query = f"""
                                INSERT INTO kmugstore_data
                                SET productName = '{title}',
                                keyword = '{keyword}',
                                price = {price},
                                fee = {fee},
                                imgurl = '{image_url}',
                                crawlingTime = '{now}',
                                category = '{category}'
                                """
                sql.query(insert_query)

    sql.close()
