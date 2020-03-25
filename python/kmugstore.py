import db
import requests
import time
from bs4 import BeautifulSoup


def kmugstore_crawling():
    sql = db.mysql('localhost', 'root', '1234', 'crawler')

    query = "select url , category from kmugstore_url order by idx asc"
    rows = sql.get_results(query)

    BASE_URL = "https://shop.kmug.co.kr/shop"

    for column in rows:
        url = column[0]
        category = column[1]
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "html.parser")

        pages = soup.find_all("a", {"class": "navi"})
        for page in range(len(pages) + 1):
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

                default_price_span = sub_soup.find("span", {"id": "consumer"})

                if default_price_span is not None:
                    default_price = default_price_span.get_text(
                        strip=True).replace(",", "")
                else:
                    default_price = 0
                price = int(sub_soup.find("span", {"id": "price"}).get_text(
                    strip=True).replace(",", ""))
                fee_html = sub_soup.find(
                    "td", {"style": "font-size:15px; font-weight:normal;"})

                if fee_html is not None:
                    fee = fee_html.get_text(strip=True)
                else:
                    fee = 0

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
                                default_price = {default_price},
                                price = {price},
                                fee = {fee},
                                imgurl = '{image_url}',
                                crawlingTime = '{now}',
                                category = '{category}'
                                """
                sql.query(insert_query)

    sql.close()
