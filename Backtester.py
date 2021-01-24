import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import time

#Functions
def parse_date_ranges(dates):

    def group_consecutive(dates):
        dates_iter = iter(sorted(set(dates)))  # de-dup and sort

        run = [next(dates_iter)]
        for d in dates_iter:
            if (d.toordinal() - run[-1].toordinal()) == 1:  # consecutive?
                run.append(d)
            else:  # [start, end] of range else singleton
                yield [run[0], run[-1]] if len(run) >= 1 else None
                run = [d]

        yield [run[0], run[-1]] if len(run) >= 1 else None

    return list(group_consecutive(dates))


# BASIC YFINANCE STOCK INFORMATION
input = input('Please input a ticker to backtest: ')
ticker = yf.Ticker(input.upper())
print(f'Gathering data for {input.upper()}')
time.sleep(2)
spxl_hist = ticker.history(period='max')
data_raw = pd.DataFrame(spxl_hist)
data_clean = data_raw[['Open', 'High', 'Low', 'Close']]
data_clean['Date_col'] = data_clean.index
pd.to_datetime(data_clean['Date_col'])

tend_ma = data_clean['Open'].rolling(window=10, min_periods=1).mean()
fiftyd_ma = data_clean['Open'].rolling(window=50,min_periods=1).mean()

data_clean['10 Day MA'] = tend_ma
data_clean['Fifty Day MA'] = fiftyd_ma

#------------------------------
#------------------------------
#-----Separated by years-------
#--------and Quarters----------
#------------------------------
#------------------------------
data_clean['Year'] = data_clean['Date_col'].dt.year
data_clean ['Quarter'] = pd.PeriodIndex(data_clean['Date_col'], freq='Q')
data_clean = data_clean.sort_index().asfreq('D', method='pad')

#----------------------
#----------------------
#--BUYING AND SELLING--
#----------------------
#----------------------

data_bought = data_clean[data_clean['10 Day MA'] > data_clean['Fifty Day MA']]

date_list = data_bought.index[:]

date_list_parse = list(parse_date_ranges(date_list))

starting_dates = []

ending_dates = []

for obj in date_list_parse:
    starting_dates.append(obj[0])
    ending_dates.append(obj[1])

starting_frame = pd.DataFrame(starting_dates, columns=['Date'])

ending_frame = pd.DataFrame(ending_dates, columns=['Date'])

'''Performance of the Moving Avg Method'''
data_pure_open = data_clean[['Open', 'Close']]

merge_start = data_pure_open.merge(starting_frame, left_index=True, right_on='Date')

merge_end = data_pure_open.merge(ending_frame, left_index=True, right_on='Date')

end_stats = pd.DataFrame(merge_end['Close']/merge_start['Open']-1)
end_stats.columns = ['Performance']
end_stats.index = ending_frame['Date']




print('Ending performance mean')
print(f'10 Vs 50 Day MA Avg/Trade: {end_stats.mean()}')

print('---------------')
print('Average number of trades/year') # this tuple will return the total amount of trades for the whole term,
print('10 v 50:')                       # must then be divided by number of years
print(end_stats.shape)




end_stats['Floats'] = end_stats['Performance'].astype(float)    # need to use floats to initiate math operations
dollarMA = 1
dollarMA_list = []
for float in end_stats['Floats']:
    dollarMA = dollarMA * (1+float)
    dollarMA_list.append(dollarMA)


# Buy and hold performance
Startbuyhold = data_clean['Open'][0]
Endbuyhold = data_clean['Close'][-1]
totalperfbuyhold = (Endbuyhold/Startbuyhold)-1

#-----------------
#-----------------
#----PLOTS--------
#-----------------

fig_1 = plt.figure(1)     # plotting a scatter plot of each MA trade's performance
plt.scatter(end_stats.index,end_stats['Performance'], alpha=0.7)
plt.xlabel('Date')
plt.ylabel('Performance')
plt.title('10 Versus 50 Day MA Perf/Trade')

valueofdollar_ma = plt.figure(2)        # value of one dollar following the moving average trading criteria
plt.plot(end_stats.index, dollarMA_list)
plt.xlabel('Date')
plt.ylabel('Dollar value')
plt.title('Value of $1, using 10/50 day MA method')

dollar_vals_comp = plt.figure(3)        # value of one dollar moving average criteria vs buy and hold
ax = plt.subplot(111)
ax.bar(1, totalperfbuyhold, width= 0.2, color = 'b', align='center', label ='Buy&Hold')
ax.bar(1.2, dollarMA, width = 0.2, color='g', align='center', label = 'Moving Avgs')
ax.title.set_text('Value of $1, Moving Avg vs Buy and Hold')
ax.set_xlabel('X axis')
ax.set_ylabel('Value of $1')
ax.legend(loc='upper right')
plt.show()
