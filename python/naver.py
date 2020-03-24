import db
import requests
import time
from bs4 import BeautifulSoup


def naverstore_crawling():
    sql = db.mysql('localhost', 'root', '1234', 'crawler')

    query = "select product_partnum , product_naverlink, product_category from product_part order by idx asc"
    rows = sql.get_results(query)

    for column in rows:
        keyword = column[0]
        url = column[1]
        category = column[2]
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "html.parser")

        title = soup.find("div", {"class": "h_area"}).find(
            "h2").get_text(strip=True)

        items = soup.find("table", {"class": "tbl_lst"}).find_all(
            "tr", {"class": "_itemSection"}, limit=3)

        for item in items:
            mall = item.find("span", {"class": "mall"})
            mall_title = mall.get_text(strip=True)

            if mall_title == "":
                mall_title = mall.find("img", {"height": "15"})["alt"]
            price = item.find("a", {"data-eventtpcd": "spr*m.price"}).get_text().replace(
                "최저", "").replace(",", "").replace("원", "").strip()

            fee = item.find("td", {"class": "gift"}).get_text().replace(
                "최저", "").replace(",", "").replace("원", "").strip()

            if fee == "무료배송":
                fee = 0
            productUrl = item.find("a", {"class": "btn_buy"})["href"]
            now = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time()))
            insert_query = f"""
                                INSERT INTO ecommerce_data
                                SET productName = '{title}',
                                keyword = '{keyword}',
                                price = {price},
                                fee = {fee},
                                productUrl = '{productUrl}',
                                crawlingTime = '{now}',
                                crawlingSite = '{mall_title}',
                                saler = '{mall_title}'
                                """
            sql.query(insert_query)

    sql.close()
