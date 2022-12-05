import os
from time import sleep
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# User Parameters
b_url =  "https://rank.greeco-channel.com/diamtire/?pg=" # base_url
p_s = 1 # page_start
p_e = 1 # page_end

my_options = Options()
my_options.add_argument("--incognito") # use incognito mode/匿名モードでChromeを使う

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=my_options) # Set webdriver
driver.implicitly_wait(10) # Set implicit wait time/暗示的な待機時間を設定

for i in range(p_s, p_e+1):
    url = b_url + str(i)
    print(f"Accessing {url}...")
    driver.get(url)
    el_tbl = driver.find_element(By.XPATH, "//table[@class='rank_tbl']") # make driver find the table via xpath/ドライバにxpath経由でtblを探させる
    html_tbl = el_tbl.get_attribute('outerHTML') # get the html as string/htmlの文字列を取得する
    df = pd.read_html(html_tbl)[0] # cast the html as pd.DataFrame.
                                # If this raises error "ImportError: lxml not found, please install it", then use "pip3 install lxml"
                                # htmlをpd.DataFrameにキャストする。
                                # もし、"ImportError: lxml not found, please install it"というエラーが出たら"pip3 install lxml"を実行する
    df.to_csv("out.csv")
    #print(type(df))
    #print(len(df))
    #print(df.columns)
    #driver.save_screenshot(f"ss{str(i)}.png")
    sleep(1)
driver.quit()

a = '''
try:
    el = WebDriverWait(By.CSS_SELECTOR, timeout=3).until(lambda d:
        d.driver.find_element(By.LINK_TEXT, "次の10件"))
except:
    print("!!!Error")'''
