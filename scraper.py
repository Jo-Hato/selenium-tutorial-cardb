import os
import random
from time import sleep
import pandas as pd
import sqlite3 as sl

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Selenium User Parameters
b_url =  "https://rank.greeco-channel.com/diamtire/?pg=" # base_url
p_s = 1 # page_start
p_e = 431 # page_end
slp_t = 15 # sleep_time

my_options = Options()
my_options.add_argument("--incognito") # use incognito mode/匿名モードでChromeを使う

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=my_options) # Set webdriver
driver.implicitly_wait(10) # Set implicit wait time/暗示的な待機時間を設定

# Log
e_log = ""
n_try = 0
n_good = 0

# Random Time Generator
def my_rand(seconds):
    mu = seconds
    sigma = seconds * 0.33 # secondsの33パーセント
    wait_sec = random.gauss(mu, sigma)
    return seconds if (wait_sec < 0) else seconds

# SQLite3
db_name = "car.db"
con = sl.connect(db_name)
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS car_tire(
        Id          INTEGER PRIMARY KEY AUTOINCREMENT,
        PostDate    TEXT,
        ImgUrl      TEXT,
        Mfr         TEXT NOT NULL,
        MdlCode     TEXT,
        Name        TEXT NOT NULL,
        Grade       TEXT,
        T_OD_mm     INTEGER,
        T_Width     INTEGER,
        T_Ratio     INTEGER,
        T_SR_Cnst   INTEGER,
        RimR_in     INTEGER,
        GrndClr_mm  INTEGER,
        Archetype   TEXT,
        UNIQUE(Name, MdlCode, Grade)
    );
""")
con.commit()

# Crawling
for page in range(p_s, p_e+1):
    url = b_url + str(page)
    try:
        driver.get(url)
        e_tbls = driver.find_elements(By.XPATH, "//tr[contains(@class,'line27')]/td") # make driver find the table via xpath/ドライバにxpath経由でtbl>trを探させる
        keys = ["PostDate", "ImgUrl", "Mfr", "MdlCode", "Name", "Grade", "T_OD_mm", "T_Width", "T_Ratio", "T_SR_Cnst", "RimR_in", "GrndClr_mm", "Archetype"]
        dicts = []
        for (i, tbl) in enumerate(e_tbls):
            txts = tbl.text.split("\n")
            if (i%5==0):   # 2 "製造元", "型番(省略)"
                data = dict.fromkeys(keys, "-") # Initialize emtpy dict/空の辞書を用意する
                data["Mfr"] = "".join(txts[:-1])
            elif (i%5==1): # 1 "画像url"
                e_c = tbl.find_element(By.XPATH, './*') # e_c = element_child = 要素_子
                txts = [e_c.get_attribute("src")]
                data["ImgUrl"] = txts[0]
            elif (i%5==2): # 4 "投稿日", "車名", "グレード", "型番(Full)"
                data["PostDate"] = txts[0]
                data["Name"] = txts[1].replace(" ","") # Remove space/スペースを排除
                data["Grade"] = txts[2]
                data["MdlCode"] = "-" if (txts[3] == "型式不明") else txts[3][1:-1]
            elif (i%5==3): # 4 "外径”, “タイヤサイズ(mm/ratio/inch)", "地上高", "RPM(100kmph)"
                data["T_OD_mm"] = "-" if (txts[0] == "-") else int(txts[0][:-2])
                tire = txts[1]
                w, r, sc, rrad = tire[:3], tire[4:6], tire[6:-2], tire[-2:]
                data["T_Width"] = int(w)
                data["T_Ratio"] = int(r)
                data["T_SR_Cnst"] = sc
                data["RimR_in"] = int(rrad)
                data["GrndClr_mm"] = "-" if (txts[2]=="-") else int(txts[2][1:-3])
            elif (i%5==4): # 4 "エンジン名", "排気量/吸気方式", "ドライブ/ギア数", "車種"
                data["Archetype"] = txts[3]
                dicts.append(data)
        #df = pd.DataFrame(dicts)
        #df.drop(df.columns, axis=1, inplace=True)
        #print(df)
        # DB処理
        for (i, d) in enumerate(dicts):
            n_try += 1
            tup = tuple(d.values()) # dict.valuesをtupleにキャストする
            try:
                con.execute("""
                    INSERT INTO car_tire(PostDate, ImgUrl, Mfr, MdlCode, Name, Grade,
                    T_OD_mm, T_Width, T_Ratio, T_SR_Cnst, RimR_in, GrndClr_mm, Archetype)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, tup)
                con.commit()
                n_good += 1
            except Exception as e:
                e_line = f"!!!INSERTION FAILED AT: page = {page}, row = {i} ||| ERROR CODE: {str(e)} ||| DETAIL: {tup}"
                print(e_line)
                e_log += e_line+"\n"
    except Exception as e:
            n_try += 10
            e_line = f"!!!SOMETHING WENT WRONG AT (may be bad url): page = {page}, url = {url} ||| ERROR CODE: {str(e)}"
            print(e_line)
            e_log += e_line+"\n"
    print(f"PROGRESS (aprox.): {n_try / (p_e+1 - p_s) * 10}")
    sleep(my_rand(slp_t))
cur.close()
con.close()
driver.quit()
print(f"SUCCESS RATE (passes/tries): {n_good}/{n_try}. FAILED: {n_try - n_good}")
if (len(e_log)>0):
    with open('error_log.txt', 'w') as f:
        header = f"START PAGE: {p_s}, END PAGE: {p_e}\n"
        f.write(header + e_log)
