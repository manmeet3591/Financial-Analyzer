import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import scipy.stats

def simulate(startdate, enddate, ls_symbols, w):
	print("Check 1")	
	c_dataobj = da.DataAccess('Yahoo')	
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

	dt_timeofday = dt.timedelta(hours=16)
	ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)
	print("Check 2")	
	ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)

	print("Check 4")	
	d_data = dict(zip(ls_keys, ldf_data))	
	
	print("Check 5")	
	close = d_data['close'].values

	print("Check 7")
#	asset = close[:,0]	
	print("Check 6")	
#	print(asset[0])	
#	for i in range(0,4):
#		asset = close[:,i]
	asset1 = close[:,0] / close[0,0]
	na_rets1 = asset1.copy()
	ret1 = tsu.returnize0(na_rets1)
	as1ret=np.average(ret1)
	print("Average return from first equity is",as1ret*252)
#	print("The size of returns from 4 equities are",len(ret))
	asset2 = close[:,1] / close[0,1]
	na_rets2 = asset2.copy()
	ret2 = tsu.returnize0(na_rets2)
	as2ret=np.average(ret2)
	print("Average return from second equity is",as2ret*252)

	asset3 = close[:,2] / close[0,2]
	na_rets3 = asset3.copy()
	ret3 = tsu.returnize0(na_rets3)
	as3ret=np.average(ret3)

	print("Average return from third equity is",as3ret*252)
	asset4 = close[:,3] / close[0,3]
	na_rets4 = asset4.copy()
	ret4 = tsu.returnize0(na_rets4)
	as4ret=np.average(ret4)

	print("Average return from fourth equity is",as4ret*252)
	netret = w[0]*as1ret +  w[1]*as2ret +  w[2]*as3ret +  w[3]*as4ret   
	st1=np.std(ret1)
	st2=np.std(ret2)
	st3=np.std(ret3)
	st4=np.std(ret4)
#
#	rho12=np.corrcoef(ret1, ret2)[0, 1]
#	rho13=np.corrcoef(ret1, ret3)[0, 1]
#	rho14=np.corrcoef(ret1, ret4)[0, 1]
#	rho23=np.corrcoef(ret2, ret3)[0, 1]
#	rho24=np.corrcoef(ret2, ret4)[0, 1]
#	rho34=np.corrcoef(ret3, ret4)[0, 1]
#	print("rho24",rho24)

	rho12=scipy.stats.pearsonr(ret1, ret2)[0]
	rho13=scipy.stats.pearsonr(ret1, ret3)[0]
	rho14=scipy.stats.pearsonr(ret1, ret4)[0]
	rho23=scipy.stats.pearsonr(ret2, ret3)[0]
	rho24=scipy.stats.pearsonr(ret2, ret4)[0]
	rho34=scipy.stats.pearsonr(ret3, ret4)[0]
	
#	print("rho24",rho24)
	portVar = (w[0]**2)*(st1**2) +  (w[1]**2)*(st2**2) + (w[2]**2)*(st3**2) + (w[3]**2)*(st4**2) + 2*w[0]*w[1]*st1*st2*rho12 +  2*w[0]*w[2]*st1*st3*rho13 +  2*w[0]*w[3]*st1*st4*rho14 +  2*w[1]*w[2]*st2*st3*rho23 +  2*w[1]*w[3]*st1*st2*rho24 +  2*w[2]*w[3]*st3*st4*rho34 
	portStd=math.sqrt(portVar)
	print("Portfolio standard deviation = ", portStd)	
	print("Sharpe Ratio  = ", (netret)/portStd)	
	
def main():
	symbols = ["C", "GS", "IBM", "HNZ"]
	weights = [0.2,0.0,0.0,0.8]
	dt_start = dt.datetime(2011, 1, 1)
	dt_end = dt.datetime(2011, 12, 31)
#	vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, symbols, weights)
	simulate(dt_start, dt_end, symbols, weights)
	
if __name__ == "__main__": 
	main()

