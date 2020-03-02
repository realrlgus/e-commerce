import time
import chrome_driver
import requests
import json
from bs4 import BeautifulSoup

API_URL = "http://localhost:3001/api"
headers = {'Content-Type': 'application/json; charset=utf-8'}


def wemakeprice_crawling():
    driver = chrome_driver.get_driver()

    BASE_URL = "https://search.wemakeprice.com/search"
    SORT = "sort=cheap"
    crawling_site = "위메프"
    response = requests.get(url=f"{API_URL}/keyword")

    rows = response.json()
    for column in rows:
        keyword = column['keyword']
        url = f"{BASE_URL}?keyword={keyword}&{SORT}"
        driver.get(url)
        time.sleep(2)
        result = driver.page_source
        soup = BeautifulSoup(result, 'html.parser')

        is_exists = soup.find("span", {"class": "t_block"})

        if is_exists is not None:
            continue
        last_pages = soup.find("a", {"class": "btn_lst"})["data-page"]
        if last_pages is None:
            pages = soup.find("div", {"class": "paging_comm"}).find_all(
                "a", {"class": "link_page"})
            pages = len(pages)
            for_page = range(len(pages) + 1)
        else:
            pages = int(last_pages)
            for_page = range(pages)
        for page in for_page:
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
                    "em", {"class": "num"}).get_text(strip=True).replace(",", "").replace("원", ""))
                if price < 190000:
                    continue
                title = sub_soup.find(
                    "h3", {"class": "deal_tit"}).get_text(strip=True)
                saler = "null"
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

                params = {"productName": title, "keyword": keyword, "price": price, "fee": fee,
                          "productUrl": product_url, "crawlingTime": now, "crawlingSite": crawling_site, "saler": saler}

                requests.post(url=f"{API_URL}/items", data=json.dumps(
                    params), headers=headers)

    driver.close()
    driver.quit()
