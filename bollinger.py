import datetime as dt
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd

# QSTK Imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du

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

def get_bollinger(dt_start, dt_end, s_symbol, i_lookback):
    ls_symbols = []
    ls_symbols.append(s_symbol)
    df_prices = get_prices(dt_start, dt_end, ls_symbols)
    ts_price = df_prices[s_symbol]
    ts_mid = pd.rolling_mean(ts_price, i_lookback)
    ts_std = pd.rolling_std(ts_price, i_lookback)
    ts_lower = ts_mid - ts_std
    ts_upper = ts_mid + ts_std
    ts_bollinger = (ts_price - ts_mid) / (ts_std) 

    df_bollinger = pd.concat([ts_price, ts_mid, ts_std, ts_lower, ts_upper, ts_bollinger], join='outer', axis = 1)
    df_bollinger.columns = ["price", "mid", "std", "lower", "upper", "bollinger"]

    ldt_dates = ts_price.index
    i_len = len(ldt_dates)
    na_buy_signal = np.NaN * np.empty(i_len)
    na_sell_signal = np.NaN * np.empty(i_len)
    if i_lookback > 0:
        for i in range(i_lookback, i_len):
            if ts_bollinger[i - 1] >= -1 and ts_bollinger[i] < -1:
                    na_buy_signal[i] =  1
            elif ts_bollinger[i - 1] <= 1 and ts_bollinger[i] > 1:
                    na_sell_signal[i] = 1
    df_bollinger["buy_sig"] = na_buy_signal
    df_bollinger["sell_sig"] = na_sell_signal
    return df_bollinger

def save_bollinger(df_bollinger, s_out_file_path):
    df_bollinger.to_csv(s_out_file_path, sep=",", header=True, index=True)

def plot_bollinger(df_bollinger, s_symbol, s_lookback, s_out_img_path):
    # creating subplot
    fig, axes = plt.subplots(2, sharex=True)
    gs = gridspec.GridSpec(2, 1, height_ratios=[5, 2])    
    axes[0] = plt.subplot(gs[0])
    axes[1] = plt.subplot(gs[1], sharex=axes[0])
    #plt.tight_layout(h_pad=0.06)
    fig.subplots_adjust(hspace=0.06)
    plt.subplots_adjust(left=0.1, right=0.95, top=0.94, bottom=0.15)
    axes[0].grid()
    axes[1].grid()
    plt.setp(axes[0].get_xticklabels(), visible=False)    
    plt.setp(axes[1].get_xticklabels(), rotation=30)    
    fig.suptitle("Bollinger bands for " + s_symbol + ", lookback=" + s_lookback, fontsize=16)
    axes[1].set_xlabel("timestamps (days)") 
    axes[0].set_ylabel("adjusted close (USD)") 
    axes[1].set_ylabel("bollinger value") 
    ldt_timestamps = list(df_bollinger.index)
    axes[0].plot(ldt_timestamps, df_bollinger["price"], "b", linewidth=1.5)
    axes[0].plot(ldt_timestamps, df_bollinger["mid"], "b--", linewidth=1)
    axes[0].plot(ldt_timestamps, df_bollinger["lower"], "b-", color="#808080")
    axes[0].plot(ldt_timestamps, df_bollinger["upper"], "b-", color="#808080")
    axes[0].fill_between(ldt_timestamps, df_bollinger["upper"], df_bollinger["lower"], color="#E6E6E6")
    axes[1].plot(ldt_timestamps, df_bollinger["bollinger"], "k", linewidth=1.5)
    axes[1].fill_between(ldt_timestamps, 1, -1, color="#E6E6E6")
    # plotting vertical lines
    for i in range(len(ldt_timestamps)):
        if df_bollinger.ix[i, "buy_sig"] == 1:
            axes[0].axvline(x=ldt_timestamps[i], color="g", linewidth=0.5)
            axes[1].axvline(x=ldt_timestamps[i], color="g", linewidth=0.5)
        elif df_bollinger.ix[i, "sell_sig"] == 1:
            axes[0].axvline(x=ldt_timestamps[i], color="r", linewidth=0.5)
            axes[1].axvline(x=ldt_timestamps[i], color="r", linewidth=0.5)
    plt.savefig(s_out_img_path)
    plt.show(fig)

if __name__ == '__main__':
    print "start bollinger_bands.py"
    s_symbol = "MSFT"
    s_lookback = "20"
    s_start = "2010-01-01"
    s_end = "2010-12-31"
    s_date = "2010-06-23 16:00:00"
    s_out_file_path = "data/bollinger " + s_symbol + ".csv"
    s_out_img_path = "data/bollinger " + s_symbol + ".png"
    
    i_lookback = int(s_lookback)
    dt_start = dt.datetime.strptime(s_start, "%Y-%m-%d")
    dt_end = dt.datetime.strptime(s_end, "%Y-%m-%d")
    dt_date = dt.datetime.strptime(s_date, "%Y-%m-%d %H:%M:%S")
    df_bollinger = get_bollinger(dt_start, dt_end, s_symbol, i_lookback)
    print df_bollinger.ix[dt_date]
    save_bollinger(df_bollinger, s_out_file_path)
    plot_bollinger(df_bollinger, s_symbol, s_lookback, s_out_img_path)
    print "end bollinger_bands.py"
