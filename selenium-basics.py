from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(ChromeDriverManager().install())

url = 'http://github.com'
driver.get(url)
driver.maximize_window()
driver.save_screenshot('github.com-home.png')

url = 'http://github.com/gurofti'
driver.get(url)
time.sleep(2)
print(driver.title)
driver.back()

time.sleep(2)
driver.close()