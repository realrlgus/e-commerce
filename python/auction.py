import db
import time
import chrome_driver
from bs4 import BeautifulSoup


def auction_crawling():
    driver = chrome_driver.get_driver()

    BASE_URL = "http://browse.auction.co.kr/search"
    SORT = "s=4"
    crawling_site = "옥션"

    sql = db.mysql('localhost', 'root', '1234', 'crawler')
    query = "select distinct keyword from kmugstore_data order by idx asc"

    rows = sql.get_results(query)
    for column in rows:
        keyword = column[0]

        url = f"{BASE_URL}?keyword={keyword}&{SORT}"
        driver.get(url)
        time.sleep(2)
        result = driver.page_source
        soup = BeautifulSoup(result, 'html.parser')

        pages = soup.find("div", {"class": "component--pagination"}
                          ).find_all("a", {"class": "link--page"})

        for page in range(len(pages) + 1):
            page = page + 1
            if page != 1:
                driver.get(f"{url}&p={page}")
                time.sleep(2)
                result = driver.page_source
                soup = BeautifulSoup(result, "html.parser")

            box = soup.find("div", {"id": "section--inner_content_body_container"}).find(
                "div", {"module-design-id": "17"})
            components = box.find_all("div", {"class": "component"})
            for component in components:

                fee = soup.find("ul", {"class": "list--addinfo"}).find(
                    "span", {"class": "text--addinfo"}).get_text(strip=True).split(" ")[-1].replace("원", "").replace(",", "")
                if fee == "무료배송":
                    fee = 0
                elif type(fee) == str:
                    fee = 0
                else:
                    fee = int(fee)

                sub_url = component.find("div", {"class": "section--itemcard"}).find(
                    "div", {"class": "section--itemcard_img"}).find("a")["href"]
                driver.get(sub_url)
                sub_result = driver.page_source
                sub_soup = BeautifulSoup(sub_result, 'html.parser')
                price = int(sub_soup.find(
                    "strong", {"class": "price_real"}).get_text(strip=True).replace(",", "")[:-1])
                if price < 300000:
                    continue
                title = sub_soup.find(
                    "span", {"class": "text__item-title"}).get_text(strip=True)
                if '구매불가' in title:
                    continue
                saler = sub_soup.find(
                    "strong", {"class": "shop-title"}).get_text(strip=True)
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


auction_crawling()
