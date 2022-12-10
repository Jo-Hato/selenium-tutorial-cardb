import os
from time import sleep
from tabulate import tabulate
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
p_e = 3 # page_end

my_options = Options()
my_options.add_argument("--incognito") # use incognito mode/匿名モードでChromeを使う

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=my_options) # Set webdriver
driver.implicitly_wait(10) # Set implicit wait time/暗示的な待機時間を設定

# Log
e_log = ""

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
        MdlCode     TEXT UNIQUE,
        Name        TEXT NOT NULL,
        Grade       TEXT,
        T_OD_mm     INTEGER,
        T_Width     INTEGER,
        T_Ratio     INTEGER,
        T_SR_Cnst   INTEGER,
        RimR_in     INTEGER,
        GrndClr_mm  INTEGER,
        Archetype   TEXT
    );
""")
con.commit()

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
                data["T_OD_mm"] = None if (txts[0] == None) else int(txts[0][:-2])
                tire = txts[1]
                w, r, sc, rrad = tire[:3], tire[4:6], tire[6:-2], tire[-2:]
                data["T_Width"] = int(w)
                data["T_Ratio"] = int(r)
                data["T_SR_Cnst"] = sc
                data["RimR_in"] = int(rrad)
                data["GrndClr_mm"] = None if (txts[2]=="-") else int(txts[2][1:-3])
            elif (i%5==4): # 4 "エンジン名", "排気量/吸気方式", "ドライブ/ギア数", "車種"
                data["Archetype"] = txts[3]
                dicts.append(data)
        #df = pd.DataFrame(dicts)
        #df.drop(df.columns, axis=1, inplace=True)
        #print(df)
        # DB処理
        for d in dicts:
            # python.dict -> python.tuple (keysの順番通り)にデータ型をキャスト
            # 現在、レコードはDict型「{"key_a": "val_1", ..., "key_N" = "val_N"}」
            # ただし、SQLiteはレコードを挿入する時Tuple型「("val_1", ..., "val_N")」を好む
            #
            # よって、
            # 1. keys = ["PostDate", "ImgUrl", "Mfr", ..., "Archetype"]を
            # 順番にループして、対応するdict["key_name"]を入れてリストにappendする。
            # ["20XX/XX", "www.abc.com/xyz.png", "トヨタ", ..., "クーペ"]
            #
            # 2. List型ではSQLiteでレコード挿入できないのでTuple型にキャストする
            arr = []
            for key in keys: # 1
                arr.append(d[key])
            tup = tuple(arr) # 2
            con.execute("""
                INSERT INTO car_tire(PostDate, ImgUrl, Mfr, MdlCode, Name, Grade,
                T_OD_mm, T_Width, T_Ratio, T_SR_Cnst, RimR_in, GrndClr_mm, Archetype)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, tup)
            con.commit()
            print(f"page {page}|{tup}")
    except Exception as e:
        e_line = f"!!!{page}|||" + str(e)
        print(e_line)
        e_log += e_line+"\n"
    sleep(3)
cur.close()
con.close()
driver.quit()
if (len(e_log)>0):
    with open('error_log.txt', 'w') as f:
        f.write()
