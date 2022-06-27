
"""
OKX交易所 python 永續合約 全自動交易程式

％％％ 看得懂python程式再使用 ％％％

使用 ANTUSDT 一小時級別交易對 Laguerre濾波 疊加 SuperTrend指標

作者 : ivan [某位窮高中生]
"""

import json

import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.status_api as Status
import okx.subAccount_api as SubAccount
import okx.TradingData_api as TradingData
import okx.Broker_api as Broker
import okx.Convert_api as Convert
import time
import os

start_time = time.time()

os.system("clear") # windows系統請改 os.system("cls")

st = 0
flag = '0'

######################################  API 相關資料
api_key = "XXXX-XXXX-XXXX-XXXX-XXXX"
secret_key = "XXXXXXXX"
passphrase = "1234567"
######################################

tradingDataAPI = TradingData.TradingDataAPI(api_key, secret_key, passphrase, False, flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
convertAPI = Convert.ConvertAPI(api_key, secret_key, passphrase, False, flag)
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, True, flag)
publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)

#######################

m = 1    # 合約倍數 （不要開太高，請珍惜生命）
num = 1  # 開單張數 （注意是張數不是幣的數量）

#######################

from PIL import Image
from selenium.webdriver.firefox.options import Options
import numpy as np
from selenium import webdriver
option = Options()
option.headless = True
wd = webdriver.Firefox(options=option)

wd.get('https://tw.tradingview.com/chart/bLOm64iW/')

re = 0
bs = 0
bs2 = 0
st = 0
text = ""
bsmode = 0
bsmode2 = 0

buy_var = 0
sell_var = 0
total = float(str(fundingAPI.get_asset_valuation(ccy = 'USDT')).split(", ")[4].split("'")[3])-218263.75*int(flag)

time.sleep(5)

while True:
        try:
                coin = str(wd.title).split()[0].replace("USDT", "")+"-USDT-SWAP"
                price = float(str(wd.title).split()[1])
                os.system("clear")  # windows系統請改 os.system("cls")
                print(text)
                print("價格 : "+str(price)+"\n餘額 : "+str(total))
                image = wd.find_element_by_xpath("/html/body/div[2]/div[1]/div/div[1]/div/table/tr[1]/td[2]/div/canvas[2]")
                image.screenshot("screenshot.png")
                image = Image.open("screenshot.png")
                img = np.array(image)
                max_X = 0



                ###################################################################################  顏色辨識 抓取指標上的標籤 （我API，直接辨識顏色，哈哈）

                for i in img:
                        for r in range(len(i)):
                                j = i[r]
                                if 255 == j[0] and 23 == j[1] and 68 == j[2] and r > max_X:    #  255,23,68（RGB）每個人電腦顏色會有些許不同，可能需要更改
                                        max_X = r
                                        bsmode = 1
                                if 41 == j[0] and 98 == j[1] and 255 == j[2] and r > max_X:    #  41,98,255（RGB）每個人電腦顏色會有些許不同，可能需要更改
                                        max_X = r
                                        bsmode = 2
                max_X2 = 0
                for i in img:
                        for r in range(len(i)):
                                j = i[r]
                                if 255 == j[0] and 82 == j[1] and 82 == j[2] and r > max_X2:   #  同上
                                        max_X2 = r
                                        bsmode2 = 1
                                if 76 == j[0] and 175 == j[1] and 80 == j[2] and r > max_X2:   #  同上
                                        max_X2 = r
                                        bsmode2 = 2

                ###################################################################################


                if bsmode != 1 or bsmode2 != 1:
                    bs = 2
                    print("buy")
                if bsmode != 2 or bsmode2 != 2:
                    bs = 1
                    print("sell")
                if (bsmode != 1 or bsmode2 != 1) and (bsmode != 2 or bsmode2 != 2):
                    bs = bsmode2
                    print("None")

                if st == 0 and bs != 0:
                        text += coin + "\n"
                        bs2 = bs
                        st = 1

                if not bs2 == bs:
                        if bs == 1:
                                sell_var += 1
                                buy_var = 0
                        elif bs == 2:
                                buy_var += 1
                                sell_var = 0
                if sell_var == 300:
                        r1 = tradeAPI.close_positions(coin, 'cross', posSide="long")                                                              # 平倉
                        accountAPI.set_leverage(instId=coin, lever=str(m), mgnMode='cross')                                                       # 設定合約倍數
                        result = tradeAPI.place_order(instId=coin, tdMode='cross', side='sell', ordType='market', sz=str(num), posSide="short")   # 開空倉
                        if "'code': '0'" in str(result):
                                text += "做空 "+str(price) + "\n"
                                bs2 = bs
                                sell_var = 0
                if buy_var == 300:
                        r1 = tradeAPI.close_positions(coin, 'cross', posSide="short")                                                             # 平倉
                        accountAPI.set_leverage(instId=coin, lever=str(m), mgnMode='cross')                                                       # 設定合約倍數
                        result = tradeAPI.place_order(instId=coin, tdMode='cross', side='buy', ordType='market', sz=str(num), posSide="long")     # 開多倉
                        if "'code': '0'" in str(result):
                                text += "做多 "+str(price) + "\n"
                                bs2 = bs
                                buy_var = 0
                re += 1
                if re == 30:
                    wd.refresh()    # 重載網頁

                    total = float(str(fundingAPI.get_asset_valuation(ccy = 'USDT')).split(", ")[4].split("'")[3])-218263.75*int(flag)  # 計算交易帳戶資產
                    re = 0
                time.sleep(1)
        except:
                time.sleep(0.5)
                q = 0



