import copy
import datetime as dt
import numpy as np
import pandas as pd

# QSTK Imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du

def get_symbols(s_index):
    dataobj = da.DataAccess('Yahoo')
    return dataobj.get_symbols_from_list(s_index)

def get_data(dt_start, dt_end, ls_symbols):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    ls_keys = ["open", "high", "low", "close", "volume", "actual_close"]
    dataobj = da.DataAccess('Yahoo')
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method="ffill")
        d_data[s_key] = d_data[s_key].fillna(method="bfill")
        d_data[s_key] = d_data[s_key].fillna(1.0)
    return d_data

def get_prices(dt_start, dt_end, ls_symbols, s_key="close"):
    # close = adjusted close
    # actual_close = actual close
    d_data = get_data(dt_start, dt_end, ls_symbols)
    return d_data[s_key]

def find_events(ls_symbols, df_prices, f_price):
    df_events = copy.deepcopy(df_prices)
    df_events = df_events * np.NAN

    ldt_timestamps = df_prices.index

    for s_sym in ls_symbols:
        for t in range(1, len(ldt_timestamps)):
            f_symprice_current = df_prices[s_sym].ix[ldt_timestamps[t]]
            f_symprice_last = df_prices[s_sym].ix[ldt_timestamps[t - 1]]
            if f_symprice_last >= f_price and f_symprice_current < f_price:
                df_events[s_sym].ix[ldt_timestamps[t]] = 1
    return df_events

def generate_order(ldt_dates, t, delta_t, s_symbol, i_num):
    l_buy_order = [ldt_dates[t], s_symbol, "Buy", i_num]  
    i = t + delta_t
    if t + delta_t >= len(ldt_dates):
        i = len(ldt_dates) - 1
    l_sell_order = [ldt_dates[i], s_symbol, "Sell", i_num]
    return l_buy_order, l_sell_order
    
def generate_orders(df_events, i_num, delta_t):
    t = 0
    ldt_dates = list(df_events.index)
    ls_symbols = list(df_events.columns)
    ls_orders = []
    for t in range(len(ldt_dates)):
        for s_symbol in ls_symbols:
            if df_events.ix[ldt_dates[t], s_symbol] == 1:
                l_buy_order, l_sell_order = generate_order(ldt_dates, t, delta_t, s_symbol, i_num)
                ls_orders.append(l_buy_order)
                ls_orders.append(l_sell_order)
    df_orders = pd.DataFrame(data=ls_orders, columns=["date", "sym", "type", "num"])
    # It is not possible to set "date" as index due duplicate keys
    df_orders = df_orders.sort(["date", "sym", "type"], ascending=[1, 1, 1])
    df_orders = df_orders.reset_index(drop=True)
    return df_orders

def save_orders(df_orders, s_out_file_path):
    na_dates = np.array([[dt_date.year, dt_date.month, dt_date.day] for dt_date in df_orders["date"]])
    df_dates = pd.DataFrame(data=na_dates, columns=["year", "month", "day"])
    del df_orders["date"]
    df_orders = df_dates.join(df_orders)
    df_orders.to_csv(s_out_file_path, sep=",", header=False, index=False)

if __name__ == '__main__':
    print "start event_finder.py"
    s_start = "2008-01-01"
    s_end = "2009-12-31"
    s_index = "sp5002012"
    s_price = "10.0"
    s_delta_t = "5"
    s_num = "100"
    s_out_file_path = "data/q2_orders.csv"
    
    f_price = float(s_price)
    delta_t = int(s_delta_t)
    i_num = int(s_num)

    dt_start = dt.datetime.strptime(s_start, "%Y-%m-%d")
    dt_end = dt.datetime.strptime(s_end, "%Y-%m-%d")

    ls_symbols = get_symbols(s_index)
    df_prices = get_prices(dt_start, dt_end, ls_symbols, "actual_close")
    df_events = find_events(ls_symbols, df_prices, f_price)
    df_orders = generate_orders(df_events, i_num, delta_t)
    save_orders(df_orders, s_out_file_path)
    print "end event_finder.py"
