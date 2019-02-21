# 一、把取得的html純文字送給BeautifulSoup，產生BeautifulSoup類別
from bs4 import BeautifulSoup
import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import time
start_time = time.time()
# from selenium.common.exceptions import TimeoutException
import random
import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')


# 設定參數=================================================================
nation="United States"
exclude_word=["internation edition",]
include_word=["international ship","ship internation"]
income_diff=10
timeout = 20
order = 2000
# ========================================================================

# 測試參數=================================================================
# isbn_lib = []
# isbn_lib = ["9780321976444", "9781541500990" ,"0133254429","9781118566541"]
# isbn_lib = ["9781118486894","9781259644030"]
# ========================================================================



#加入資料庫
df = pd.read_csv(r'Book-Data-Sheet1.csv')
isbn_lib = df['ISBN/ID'].tolist()
temp_lib = isbn_lib[:]

for i in isbn_lib:
    if (len(i) != 10) and (len(i) != 13) or i.isdigit() == False :
        temp_lib.remove(i)

isbn_lib = temp_lib[:]
print("--- Data Filter Finished in %s seconds ---" % (time.time() - start_time))

#亂序排列
# random.shuffle(isbn_lib)

# browser = webdriver.Firefox()
# browser = webdriver.Chrome()

delay = 15
count = 0

f_text = open(r"bookBenefit.txt", "w")
# isbn_lib.reverse()

# 遞迴ISBN資料庫
for book in isbn_lib:
    # TEMP
    if count >= order:
        break
    count += 1
    print(count)

    # 暫停器
    time.sleep(random.random()*0.1+0.05)

    # 每本書的參數
    income = 0.0
    buy_price = 0.0
    lowest_used_price = 0

    # browser.implicitly_wait(5000)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36','Accept-Encoding': 'identity'}
    try:
        req = requests.get("https://www.bookfinder.com/search/?keywords=" + book +
                "&currency=USD&destination=us&mode=basic&lang=en&st=sh&ac=qr&submit=", headers = headers, timeout = timeout)
    except (requests.exceptions.Timeout,):
        print("requests timeout")
        continue
    # browser.get("https://www.bookfinder.com/search/?keywords=" + book +
    #             "&currency=USD&destination=us&mode=basic&lang=en&st=sh&ac=qr&submit=")

    # browser.refresh();

    # try:
    #     # myElem = WebDriverWait(browser, delay).until(
    #     #     EC.presence_of_element_located((By.ID, 'buyback_table')))
    #     # time.sleep(random.randint(6,7))
    #     # print("Page is ready!")
    #
    # except TimeoutException:
    #     print("Loading took too much time!")
    #     continue


    # soup = BeautifulSoup(browser.page_source, 'html')
    # soup = BeautifulSoup(req.text, 'html')
    soup = BeautifulSoup(req.text, 'lxml')

    # <尋找收購價格>
    # 建立篩選器
    selector_buy_price = "#buyback_table a"
    try:
        # 取得價格字串並轉換
        temp_bp_selector = soup.select(selector_buy_price)
        # 價格為篩選過後最後一個<a>
        str_buy_price = temp_bp_selector[len(temp_bp_selector)-1].string
        # 去除$符號
        buy_price = float(str_buy_price[1:len(str_buy_price)])

    # 排除為空list的情況，跳至下一本書(isbn)
    except (AttributeError,IndexError):
        continue


    # <尋找二手書籍的最低價>
    # 找出 class 為 results-table-Logo
    result_table = soup.find_all("table","results-table-Logo")

    # 排除沒有新書的情況(只有二手書時，len(result_talbe)==1)
    if len(result_table)>1:
        print("================")
        # 重設暫存參數

        temp_used_price = 0
        next_book = False

        # 讀取每筆資料
        used_data_row = result_table[1].find_all("tr")


        # 多重判斷，只留下比收購價低的二手書 且 二手書來自美國網站 且 敘述中沒有提到"internation edition"的版本
        for row in used_data_row:

            # 尋找第一筆二手書的價格
            try :
                temp_used_price =float(row['data-price'])

            # 排除標題(沒有 "data-price" 屬性)
            except (NameError,KeyError):
                continue

            else:
                # 二手書的價格低於收購價時
                if temp_used_price > buy_price:
                    next_book = True
                    break

                # 二手書的價格高於收購價時
                else:

                    # 建立來自"美國網站"的過濾器selector
                    src_temp_selector = row.select('.results-table-center .results-explanatory-text-Logo')
                    # 二次過濾，"United States"為list的最後一個index的內容
                    src_nation = src_temp_selector[len(src_temp_selector)-1].string.lower()

                    # 排除非"United States"的書籍(轉小寫比對)
                    if nation.lower() not in src_nation:
                        continue

                    # 排除敘述中有提到"international edition"的版本
                    else:
                        for desc in row.select(".item-note")[0].contents:
                            for e in exclude_word:
                                if (e in desc):
                                    break

                                    # 沒有提到"international edition"
                                else:
                                    # 儲存價格和連結
                                    lowest_used_price = temp_used_price
                                    link_src = row.select(".results-price a")[0]['href']

        # 二手書的價格低於收購價時，換一本
        if next_book == True:
            continue

    # 沒有新書的情況(只有二手書時，len(result_talbe)==1)
    else:
        continue

    # 儲存ISBN
    # selector_isbn = ".attributes h1"
    # isbn_str = soup.select(selector_isbn).string
    # isbn = isbn_str[0:isbn_str.find("/")-1]

    # 存檔
    income = buy_price - lowest_used_price
    if income > income_diff:
        print("start-----------------------------")
        # print("Isbn:", isbn)
        print("Isbn:", book ," 收益",income)
        print("賣出:", buy_price,"買入",lowest_used_price)
        print("----------------------------------")
        # f_text = open(r"C:\Users\chen\Downloads\bookBenefit.txt", "w")
        f_text = open(r"bookBenefit.txt", "a")
        f_text.write('-----------------------------\n')
        f_text.write(time.strftime("%Y-%m-%d %H:%M:%S" )+'\n')
        # f_text.write('Isbn:'+isbn+'\n')
        f_text.write('Isbn:'+book+'\n')
        f_text.write('收益'+str(income)+'\n')
        f_text.write("賣出:"+str(buy_price)+"買入"+str(lowest_used_price)+'\n')
        f_text.close()

# browser.quit()
print("--- %s seconds ---" % (time.time() - start_time))
