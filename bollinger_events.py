import copy
import datetime as dt
import numpy as np
import pandas as pd

# QSTK Imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkstudy.EventProfiler as ep

def get_symbols(s_list_index):
    dataobj = da.DataAccess("Yahoo")
    return dataobj.get_symbols_from_list(s_list_index)

#def get_data(dt_start, dt_end, ls_symbols):
#    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
#    ls_keys = ["open", "high", "low", "close", "volume", "actual_close"]
#    dataobj = da.DataAccess('Yahoo')
#    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
#    d_data = dict(zip(ls_keys, ldf_data))
#    for s_key in ls_keys:
#        d_data[s_key] = d_data[s_key].fillna(method="ffill")
#        d_data[s_key] = d_data[s_key].fillna(method="bfill")
#        d_data[s_key] = d_data[s_key].fillna(1.0)
#    return d_data

def get_prices(dt_start, dt_end, ls_symbols, s_key="close"):
    # close = adjusted close
    # actual_close = actual close
    d_data = get_data(dt_start, dt_end, ls_symbols)
    return d_data[s_key]

def get_bollingers(df_prices, i_lookback):
    df_bollingers = np.NAN * copy.deepcopy(df_prices)
    for s_symbol in df_prices.columns:
        ts_price = df_prices[s_symbol]
        ts_mid = pd.rolling_mean(ts_price, i_lookback)
        ts_std = pd.rolling_std(ts_price, i_lookback)
        df_bollingers[s_symbol] = (ts_price - ts_mid) / (ts_std) 
    return df_bollingers

def save_bollingers(df_bollingers, s_out_file_path):
    df_bollingers.to_csv(s_out_file_path, sep=",", header=True, index=True)

def find_bollinger_events(df_bollingers):
    df_events = np.NAN * copy.deepcopy(df_bollingers)
    ldt_timestamps = df_bollingers.index
    for s_symbol in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            f_bollinger_today = df_bollingers[s_symbol].ix[ldt_timestamps[i]]
            f_bollinger_yest = df_bollingers[s_symbol].ix[ldt_timestamps[i - 1]]
            f_bollinger_index = df_bollingers[ls_symbols[-1]].ix[ldt_timestamps[i]]
            if f_bollinger_today < -2.0 and f_bollinger_yest >= -2.0 and f_bollinger_index >= 1.1:
                df_events[s_symbol].ix[ldt_timestamps[i]] = 1
    return df_events
    
if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    s_symbols = 'sp5002012'

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(s_symbols)
    ls_symbols.append('SPY')

    ls_keys = ["open", "high", "low", "close", "volume", "actual_close"]
#    ls_keys = ['close', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

#    df_events = find_events(ls_symbols, d_data)
#    filename = "event_study_" + s_symbols + ".pdf"
#    print "Creating Study"
#    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
#                s_filename=filename, b_market_neutral=True, b_errorbars=True,
#                s_market_sym='SPY')
                                           
#####################################################################################
    print "start bollinger_events.py"
    s_list_index = "SP5002012"
    s_index = "SPY"
    s_lookback = "20"
    s_start = "2008-01-01"
    s_end = "2009-12-31"
    s_out_file_path = "data/q1 " + s_list_index + ".csv"
    s_out_img_path = "data/q1 " + s_list_index + ".pdf"
    
    i_lookback = int(s_lookback)
#    dt_start = dt.datetime.strptime(s_start, "%Y-%m-%d")
#    dt_end = dt.datetime.strptime(s_end, "%Y-%m-%d")
    print("Check 1") 
#    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
#    ls_keys = ["open", "high", "low", "close", "volume", "actual_close"]
#    dataobj = da.DataAccess('Yahoo')
#    ls_symbols = dataobj.get_symbols_from_list(s_list_index)
#    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
#    d_data = dict(zip(ls_keys, ldf_data))
#    for s_key in ls_keys:
#        d_data[s_key] = d_data[s_key].fillna(method="ffill")
#        d_data[s_key] = d_data[s_key].fillna(method="bfill")
#        d_data[s_key] = d_data[s_key].fillna(1.0)

#    ls_symbols = dataobj.get_symbols_from_list(s_list_index)
#    ls_symbols.append(s_index)
#    d_data = get_data(dt_start, dt_end, ls_symbols)
    df_bollingers = get_bollingers(d_data["close"], i_lookback)
    save_bollingers(df_bollingers, s_out_file_path)
    df_bollinger_events = find_bollinger_events(df_bollingers)
    ep.eventprofiler(df_bollinger_events, d_data, i_lookback=20, i_lookforward=20, \
                     s_filename=s_out_img_path, \
                     b_market_neutral=True, b_errorbars=True, \
                     s_market_sym='SPY')
    print "end bollinger_events.py"
