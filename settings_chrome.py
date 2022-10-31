from selenium import webdriver

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--incognito")

driver = webdriver.Chrome(
    executable_path="./chromedriver",
    options=options
)
