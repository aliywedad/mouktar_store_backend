from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

mat = 30006
url = f"https://dec.education.gov.mr/bac-21/{mat}/info"

options = Options()
options.add_argument("--headless")  # headless mode
options.add_argument("--disable-gpu")  # usually needed in headless Linux
options.add_argument("--no-sandbox")   # needed for Docker
options.add_argument("--disable-dev-shm-usage")  # avoid limited /dev/shm issues

driver = webdriver.Chrome(options=options)

driver.get(url)

try:
    # Wait until the result appears (up to 15 sec)
    value = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.result"))
    )
    # Example selector for the name; adjust based on real HTML
    # name = driver.find_element(By.CSS_SELECTOR, "div.student-info span:first-child")
    
    print(f"name:  note: {value.text}")
except:
    print("Data not found")

driver.quit()
