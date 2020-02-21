import db
import time
import chrome_driver
from bs4 import BeautifulSoup


def wemakeprice_crawling():
    driver = chrome_driver.get_driver()

    BASE_URL = "https://search.wemakeprice.com/search"
    SORT = "sort=cheap"
    crawling_site = "위메프"

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

        pages = soup.find("div", {"class": "paging_comm"}
                          ).find_all("a", {"class": "link_page"})

        for page in range(len(pages) + 1):
            page = page + 1
            if page != 1:
                driver.get(f"{url}&page={page}")
                time.sleep(2)
                result = driver.page_source
                soup = BeautifulSoup(result, "html.parser")
            box = soup.find("div", {"class": "search_box_imagedeal"})
            links = box.find_all("a")
            for link in links:
                sub_url = f"https:{link['href']}"

                driver.get(sub_url)

                sub_result = driver.page_source
                sub_soup = BeautifulSoup(sub_result, 'html.parser')
                price_div = sub_soup.find("strong", {"class": "sale_price"})
                if price_div is None:
                    continue
                price = int(price_div.find(
                    "em", {"class": "num"}).get_text(strip=True).replace(",", ""))
                if price < 190000:
                    continue
                title = sub_soup.find(
                    "h3", {"class": "deal_tit"}).get_text(strip=True)
                saler = None
                fee = sub_soup.find("dl", {"class": "shipping"}).find("em")

                if fee is None:
                    fee = 0
                elif type(fee.get_text(strip=True)) == str:
                    fee = 0
                else:
                    fee = int(fee.get_text(strip=True).replace(
                        ",", "").replace("원", ""))
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
