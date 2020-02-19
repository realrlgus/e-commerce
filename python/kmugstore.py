import pymysql
import requests
import time
from bs4 import BeautifulSoup

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    db='crawler',
    charset='utf8'
)

curs = conn.cursor()

query = "select url from kmugstore_url order by idx"
curs.execute(query)

rows = curs.fetchall()

BASE_URL = "https://shop.kmug.co.kr/shop"

for column in rows:
    for url in column:
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "html.parser")
        tables = soup.find_all(
            "td", {"style": "border-right:0px solid #e1e1e1;"})
        for table in tables:
            sub_link = table.find("a")["href"].replace("..", "")
            sub_result = requests.get(f"{BASE_URL}{sub_link}")
            sub_soup = BeautifulSoup(sub_result.text, "html.parser")
            title = sub_soup.find("div", {
                "style": "font-size:17px; font-weight:bold; line-height:48px; border-bottom:solid 2px #e0e0e0;"}).get_text(strip=True).replace("'", "\\'")
            part_number_idx = title.find("/A")
            if not part_number_idx == -1:
                part_number_idx_start = part_number_idx - 7
                part_number_idx_end = part_number_idx + 2
                part_number = title[part_number_idx_start:part_number_idx_end]
            else:
                part_number = None
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
                            SET productname = '{title}',
                             partnumber = '{part_number}',
                             price = {price},
                             fee = {fee},
                             imgurl = '{image_url}',
                             crawling_time = '{now}'
                             """

            curs.execute(insert_query)
            conn.commit()


conn.close()
