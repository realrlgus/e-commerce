import time
import chrome_driver
import requests
import json
from bs4 import BeautifulSoup

API_URL = "http://localhost:3001/api"
headers = {'Content-Type': 'application/json; charset=utf-8'}


def auction_crawling():
    driver = chrome_driver.get_driver()

    BASE_URL = "http://browse.auction.co.kr/search"
    SORT = "s=4"
    crawling_site = "옥션"

    response = requests.get(url=f"{API_URL}/keyword")

    rows = response.json()
    for column in rows:
        keyword = column['keyword']

        url = f"{BASE_URL}?keyword={keyword}&{SORT}"
        driver.get(url)
        time.sleep(2)
        result = driver.page_source
        soup = BeautifulSoup(result, 'html.parser')

        no_results = soup.find("div", {"class": "component--no_result"})
        if no_results:
            continue

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
                price = sub_soup.find("strong", {"class": "price_real"})
                if price is None:
                    continue
                price = int(price.get_text(strip=True).replace(",", "")[:-1])
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

                params = {"productName": title, "keyword": keyword, "price": price, "fee": fee,
                          "productUrl": product_url, "crawlingTime": now, "crawlingSite": crawling_site, "saler": saler}

                requests.post(url=f"{API_URL}/items", data=json.dumps(
                    params), headers=headers)

    driver.close()
    driver.quit()
