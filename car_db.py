import os
from time import sleep
import pandas as pd
from tabulate import tabulate 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# User Parameters
b_url =  "https://rank.greeco-channel.com/diamtire/?pg=" # base_url
p_s = 1 # page_start
p_e = 10 # page_end

my_options = Options()
my_options.add_argument("--incognito") # use incognito mode/匿名モードでChromeを使う

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=my_options) # Set webdriver
driver.implicitly_wait(10) # Set implicit wait time/暗示的な待機時間を設定

for i in range(p_s, p_e+1):
    url = b_url + str(i)
    print(f"Accessing {url}...")
    driver.get(url)
    e_tbls = driver.find_elements(By.XPATH, "//tr[contains(@class,'line27')]/td") # make driver find the table via xpath/ドライバにxpath経由でtblを探させる
    keys = ["PostDate", "ImgUrl", "Mfr", "MdlCode", "Name", "Grade", "T-OD(mm)", "T-Width", "T-Ratio(%)", "T-[SR]Cnst", "RimR(in)", "GrndClr(mm)", "Archetype"]
    dicts = []
    for (i, tbl) in enumerate(e_tbls):
        txts = tbl.text.split("\n")
        if (i%5==0):   # 2 "製造元", "型番(省略)"
            data = dict.fromkeys(keys, None) # Initialize emtpy dict/空の辞書を用意する
            data["Mfr"] = "".join(txts[:-1])
        elif (i%5==1): # 1 "画像url"
            e_c = tbl.find_element(By.XPATH, './*') # e_c = element_child = 要素_子
            txts = [e_c.get_attribute("src")]
            data["ImgUrl"] = txts[0]
        elif (i%5==2): # 4 "投稿日", "車名", "グレード", "型番(Full)"
            data["PostDate"] = txts[0]
            data["Name"] = txts[1].replace(" ","") # Remove space/スペースを排除
            data["Grade"] = txts[2]
            data["MdlCode"] = None if (txts[3] == "型式不明") else txts[3][1:-1]
        elif (i%5==3): # 4 "外径”, “タイヤサイズ(mm/ratio/inch)", "地上高", "RPM(100kmph)"
            data["T-OD(mm)"] = None if (txts[0] == None) else int(txts[0][:-2])
            tire = txts[1]
            w, r, sc, rrad = tire[:3], tire[4:6], tire[6:-2], tire[-2:]
            data["T-Width"] = int(w)
            data["T-Ratio(%)"] = int(r)
            data["T-[SR]Cnst"] = sc
            data["RimR(in)"] = int(rrad)
            data["GrndClr(mm)"] = None if (txts[2]=="-") else int(txts[2][1:-3])
        elif (i%5==4): # 4 "エンジン名", "排気量/吸気方式", "ドライブ/ギア数", "車種"
            data["Archetype"] = txts[3]
            dicts.append(data)
    df = pd.DataFrame(dicts)
    print(df)
    sleep(3)
driver.quit()

a = '''
try:
    el = WebDriverWait(By.CSS_SELECTOR, timeout=3).until(lambda d:
        d.driver.find_element(By.LINK_TEXT, "次の10件"))
except:
    print("!!!Error")'''
