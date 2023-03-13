# %%
import pandas as pd
import datetime
import pyupbit
from pyupbit import Upbit
import talib as ta
import warnings
import requests
import json
from datetime import timedelta
import time
from collections import deque
import requests
import pandas as pd
from pykrx import stock
import time
from datetime import datetime as dt
from datetime import timedelta
from dateutil.parser import parse
import holidays
import mplfinance as mpf
import pathlib
import IPython.display as IPydisplay
import config

image_save_path = config.data_path


async def auto_alarm():
    try:
        mode = "week"

        coin_nm_lst = [
            "BTC",
            "ETH",
            "NEO",
            "MANA",
            "SAND",
            "BORA",
            "ONG",
            "DOGE",
            "SOL",
            "QTUM",
            "JST",
            "AXS",
            "MATIC",
            "FLOW",
            "NU",
            "ONT",
            "ADA",
            "ATOM",
            "NEAR",
            "KNC",
            "ETC",
            "POWR",
            "AVAX",
            "WAVES",
            "EOS",
            "CVC",
            "REP",
            "TRX",
            "SXP",
            "VET",
            "TFUEL",
            "STX",
            "PLA",
            "CRO",
            "LINK",
            "HUNT",
            "PUNDIX",
            "GAS",
            "1INCH",
            "DOT",
            "THETA",
            "ENJ",
            "XLM",
            "CRE",
            "SRM",
            "ALGO",
            "SC",
            "ICX",
            #'BTT',
            "CHZ",
            "META",
            "BAT",
            "KAVA",
            "XEC",
            "LOOM",
            "XTZ",
            "WAXP",
            "AAVE",
            "HUM",
            "HBAR",
            "STRK",
            "HIVE",
            "STPT",
            "STORJ",
            "OMG",
            "FCT2",
            "MOC",
            "MLK",
            "DAWN",
            "TT",
            "MED",
            "QKC",
            "BCH",
            "ZIL",
            "SBD",
            "XEM",
            "AQT",
            "ANKR",
            "ZRX",
            "LSK",
            "BTG",
            "STRAX",
            "MTL",
            "ELF",
            "IOTA",
            "CBK",
            #'MFT',
            "STMX",
            "IQ",
            "TON",
            "UPP",
            "SNT",
            "AERGO",
            "GLM",
            "DKA",
            "SSX",
            "MVL",
            "ORBS",
            "ARK",
            "RFR",
            "ARDR",
            "IOST",
            "MBL",
            "STEEM",
            "BSV",
            "GRS",
            "AHT",
        ]

        # coin_nm_lst=['ATOM']

        ma_up_lst = []

        for coin_nm in coin_nm_lst:
            time.sleep(0.1)
            print(coin_nm)
            df = tickers_db("KRW-{}".format(coin_nm), "week", 30)[
                ["high", "low", "open", "close"]
            ]

            ma_30 = ta.SMA(df["open"], 30).iloc[-1]

            now_price = tickers_db("KRW-{}".format(coin_nm), "day", 1)["open"].iloc[0]

            if now_price > ma_30:
                ma_up_lst.append(coin_nm)
            time.sleep(0.1)

    except Exception as e:
        print(coin_nm)
        print(e)


def get_30_week_data(today_date):
    del_col = []
    kr_holidays = holidays.KR()

    std_date = (dt.now() - timedelta(weeks=30)).strftime("%Y%m%d")

    df_mk_kospi = stock.get_market_ohlcv(std_date, market="KOSPI")
    df_mk_kospi = df_mk_kospi[["종가"]]
    df_mk_kosdaq = stock.get_market_ohlcv(std_date, market="KOSDAQ")
    df_mk_kosdaq = df_mk_kosdaq[["종가"]]

    df_30_week = pd.concat([df_mk_kospi, df_mk_kosdaq])
    df_30_week.columns = [std_date]

    if df_30_week[std_date].sum() == 0:
        del_col.append(std_date)

    std_date = (parse(std_date) + timedelta(days=1)).strftime("%Y%m%d")

    while int(std_date) <= int(today_date):
        if (std_date not in kr_holidays) & (parse(std_date).weekday() not in [5, 6]):
            df_mk_kospi = stock.get_market_ohlcv(std_date, market="KOSPI")
            df_mk_kospi = df_mk_kospi[["종가"]]
            df_mk_kosdaq = stock.get_market_ohlcv(std_date, market="KOSDAQ")
            df_mk_kosdaq = df_mk_kosdaq[["종가"]]
            df_mk = pd.concat([df_mk_kospi, df_mk_kosdaq])
            df_mk.columns = [std_date]

            df_30_week = pd.merge(
                df_30_week, df_mk, how="left", left_index=True, right_index=True
            )

            if df_30_week[std_date].sum() == 0:
                del_col.append(std_date)

        std_date = (parse(std_date) + timedelta(days=1)).strftime("%Y%m%d")

    df_30_week = df_30_week.drop(del_col, axis=1)

    return df_30_week


# %%

today_date = dt.now().strftime("%Y%m%d")

df = get_30_week_data(today_date)

df["ma_30"] = df.mean(axis=1)

df = df[df["ma_30"] < df[df.columns[-2]]]

targ_df = df.copy()

# %%


today_date = dt.now().strftime("%Y%m%d")


kospi_lst = list(stock.get_market_ohlcv(today_date, market="KOSPI").index)
kosdaq_lst = list(stock.get_market_ohlcv(today_date, market="KOSDAQ").index)

kospi_ind_diff_1month = (
    stock.get_index_price_change(
        (parse(today_date) - timedelta(weeks=4)).strftime("%Y%m%d"), today_date, "KOSPI"
    ).iloc[0, 2]
) * 0.01

kosdaq_ind_diff_1month = (
    stock.get_index_price_change(
        (parse(today_date) - timedelta(weeks=4)).strftime("%Y%m%d"),
        today_date,
        "KOSDAQ",
    ).iloc[0, 2]
) * 0.01

kospi_targ_ticker_lst = []
kospi_targ_rs_lst = []

pass_cnt = 0

for ticker in kospi_lst:
    time.sleep(0.01)
    try:
        if ticker in list(targ_df.index):
            df = stock.get_market_ohlcv(
                (parse(today_date) - timedelta(weeks=4)).strftime("%Y%m%d"),
                today_date,
                ticker,
            )
            st_pr = df.iloc[0, 3]
            ed_pr = df.iloc[-1, 3]
            diff_1month = (ed_pr - st_pr) / (st_pr)

            if diff_1month > kospi_ind_diff_1month:
                rs_1month = abs(diff_1month / kospi_ind_diff_1month)
                kospi_targ_ticker_lst.append(ticker)
                kospi_targ_rs_lst.append(rs_1month)

    except:
        pass_cnt += 1
        print(ticker)
    time.sleep(0.01)

kosdaq_targ_ticker_lst = []
kosdaq_targ_rs_lst = []

print(pass_cnt)
for ticker in kosdaq_lst:
    time.sleep(0.01)
    try:
        if ticker in list(targ_df.index):
            df = stock.get_market_ohlcv(
                (parse(today_date) - timedelta(weeks=4)).strftime("%Y%m%d"),
                today_date,
                ticker,
            )
            st_pr = df.iloc[0, 3]
            ed_pr = df.iloc[-1, 3]
            diff_1month = (ed_pr - st_pr) / (st_pr)

            if diff_1month > kosdaq_ind_diff_1month:
                rs_1month = abs(diff_1month / kosdaq_ind_diff_1month)
                kosdaq_targ_ticker_lst.append(ticker)
                kosdaq_targ_rs_lst.append(rs_1month)
    except:
        pass_cnt += 1
        print(ticker)
    time.sleep(0.01)

kospi_df_rs = pd.DataFrame()
kospi_df_rs.index = kospi_targ_ticker_lst
kospi_df_rs["rs"] = kospi_targ_rs_lst

kosdaq_df_rs = pd.DataFrame()
kosdaq_df_rs.index = kosdaq_targ_ticker_lst
kosdaq_df_rs["rs"] = kosdaq_targ_rs_lst

sto_df = pd.concat([kospi_df_rs, kosdaq_df_rs])

# %%
print(len(kosdaq_targ_ticker_lst))
print(len(kospi_targ_ticker_lst))
# %%
targ_df = targ_df[
    targ_df.index.isin(kosdaq_targ_ticker_lst)
    | targ_df.index.isin(kospi_targ_ticker_lst)
]

targ_df = pd.merge(targ_df, sto_df, how="left", left_index=True, right_index=True)


# %%


image_save_path = image_save_path + today_date + "/"
a_path = image_save_path + "A/"
b_path = image_save_path + "B/"

if not os.path.isdir(image_save_path):
    os.makedirs(image_save_path)

if not os.path.isdir(a_path):
    os.makedirs(a_path)

if not os.path.isdir(b_path):
    os.makedirs(b_path)

for ticker in targ_df.index:
    df = stock.get_market_ohlcv(
        (parse(today_date) - timedelta(weeks=52)).strftime("%Y%m%d"), today_date, ticker
    )
    df.columns = ["Open", "High", "Low", "Close", "Volume", "abc", "updown"]
    name = stock.get_market_ticker_name(ticker)

    print(
        mpf.plot(
            df,
            type="candle",
            style="charles",
            title=name,
            ylabel="stock price",
            ylabel_lower="volume",
            volume=True,
            mav=(150),
        )
    )

    ans = input("차트를 저장할까요? : A/B/Skip(Enter) ")
    if ans == "A":
        mpf.plot(
            df,
            type="candle",
            style="charles",
            title=name,
            ylabel="stock price",
            ylabel_lower="volume",
            volume=True,
            mav=(150),
            savefig=dict(fname=a_path + name, dpi=100, pad_inches=0.25),
        )
    elif ans == "B":
        mpf.plot(
            df,
            type="candle",
            style="charles",
            title=name,
            ylabel="stock price",
            ylabel_lower="volume",
            volume=True,
            mav=(150),
            savefig=dict(fname=b_path + name, dpi=100, pad_inches=0.25),
        )
    else:
        pass
