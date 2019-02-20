# 一、把取得的html純文字送給BeautifulSoup，產生BeautifulSoup類別
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
import random
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')


nation="United States"
exclude_word=["internation edition",]
include_word=["international ship","ship internation"]
income_diff=10

# isbn_lib = []
# isbn_lib = ["9780321976444", "9781541500990" ,"0133254429","9781118566541"]
isbn_lib = ["9781133610663"]



#加入資料庫
# f = open(r'C:\Users\chen\Downloads\abebook.txt', 'r')
# for line in f:
#     tempBook = line[0:11]
#     isbn_lib.append(tempBook)
# f.close()

#亂序排列
# random.shuffle(isbn_lib)



# f = open(r'C:\Users\chen\Downloads\ol_dump_editions_2018-12-31.txt', 'r')
# for line in f:
#     isbn_count = line.find("isbn_13")
#     tempBook = line[isbn_count+12:isbn_count+25]
#     isbn_lib.append(tempBook)
#     # if len(isbn_lib)==500:
#     #     break
# f.close()




# browser = webdriver.Firefox()
browser = webdriver.Chrome()

delay = 15
order = 0

# isbn_lib.reverse()

for book in isbn_lib:
    income = 0.0
    buy_price = 0.0
    lowest_used_price = 0

    # browser.implicitly_wait(5000)
    browser.get("https://www.bookfinder.com/search/?keywords=" + book +
                "&currency=USD&destination=us&mode=basic&lang=en&st=sh&ac=qr&submit=")
    # browser.refresh();

    try:
        myElem = WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.ID, 'buyback_table')))
        time.sleep(random.randint(5,5))
        # time.sleep(random.randint(6,7))

        # print("Page is ready!")

    except TimeoutException:
        print("Loading took too much time!")


    soup = BeautifulSoup(browser.page_source, 'html')


    selector_buy_price = "table td a"
    buy_price = soup.select(selector_buy_price)

    for b in buy_price:
        str_b = str(b)
        # print(str_b)
        if str_b.find("/buyback/search/#") >= 0:
            buy_price = float((str_b[str_b.find("$") + 1:-4]))
    # if buy_price == 0:
    #     continue


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
                        desc = row.select(".results-note-excessively-long").string.lower()
                        for e in exclude_word:
                                if (e in desc):
                                    break

                                # 沒有提到"international edition"
                                else:
                                    # 儲存價格和連結
                                    lowest_used_price = temp_used_price
                                    link_src = row.select("span a")['href']



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
        f_text = open(r"bookBenefit.txt", "w")
        f_text.write('-----------------------------\n')
        f_text.write(time.strftime("%Y-%m-%d %H:%M:%S" )+'\n')
        # f_text.write('Isbn:'+isbn+'\n')
        f_text.write('Isbn:'+book+'\n')
        f_text.write('收益'+str(income)+'\n')
        f_text.write("賣出:"+str(buy_price)+"買入"+str(lowest_used_price)+'\n')
        f_text.close()

browser.quit()
