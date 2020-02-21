from selenium import webdriver


def get_driver():
    driver_path = "/Users/chromedriver.exe"
    return webdriver.Chrome(driver_path)
