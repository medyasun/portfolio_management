import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
plt.style.use("fivethirtyeight")

def df_port(assets,startd,endd):
    stockStartDate=startd
    stockEndDate=endd
    df=pd.DataFrame()
    for stock in assets:
        df[stock]=yf.download(stock,start=stockStartDate,end=stockEndDate,progress=False)["Adj Close"]
    return df
  
def expected_return(df,assets):
    port_num=len(assets)
    weights=[]
    for i in range(0,port_num):
        weights.append(1/port_num)
    weights=np.array(weights)
    
    returns=df.pct_change()
    cov_matrix_annual=returns.cov()*252
    port_variance=np.dot(weights.T,np.dot(cov_matrix_annual,weights))
    port_volatility=np.sqrt(port_variance)
    portSimpleReturn=np.sum(returns.mean()*weights)*252
    percent_var=str(round(port_variance*100,2))+"%"
    percent_volatility=str(round(port_volatility*100,2))+"%"
    precent_return=str(round(portSimpleReturn*100,2))+"%"
    return precent_return,percent_volatility,percent_var,weights


def opt_port(df,amount):
    from pypfopt.efficient_frontier import EfficientFrontier
    from pypfopt import risk_models
    from pypfopt import expected_returns
    df=df.dropna(how="any",axis=1)
    mu=expected_returns.mean_historical_return(df)
    S=risk_models.sample_cov(df)
    ef=EfficientFrontier(mu,S)
    weights=ef.max_sharpe()
    cleaned_weights=ef.clean_weights()
    print(cleaned_weights)
    ear,av,sr=ef.portfolio_performance(verbose=True)

    from pypfopt.discrete_allocation import DiscreteAllocation,get_latest_prices
    latest_prices=get_latest_prices(df)
    df_latest=pd.DataFrame(latest_prices).reset_index()
    df_latest.rename(columns={"index":"Hisse Kodu",df_latest.columns[1]:"Fiyat"},inplace=True)
    df_latest["Hisse Kodu"]=df_latest["Hisse Kodu"].str.replace(".IS","")

    weights=cleaned_weights
    da=DiscreteAllocation(weights,latest_prices,total_portfolio_value=int(amount))
    allocation,leftover=da.greedy_portfolio()

    allocation=pd.DataFrame.from_dict(allocation,orient ='index').reset_index().rename(columns={0:"Hisse Adedi","index":"Hisse Kodu"})
    allocation["Hisse Kodu"]=allocation["Hisse Kodu"].str.replace(".IS","")
    allocation=allocation.merge(df_latest)
    allocation["Fiyat"]=allocation["Fiyat"].round(2)
    toplam=sum(allocation["Fiyat"]*allocation["Hisse Adedi"])
    allocation["Oran"]=round(((allocation["Fiyat"]*allocation["Hisse Adedi"])/toplam)*100,2)
    return ear,av,sr,allocation,leftover

def get_stock_list(hisse_tanim="100",endeks=False,usd=False): 
  # 100 tum 30 ile istenen hisse listelerine ulaşılabilir
  df_hist=pd.DataFrame()
  df_bist100=pd.DataFrame()
  test=pd.read_html("https://uzmanpara.milliyet.com.tr/canli-borsa/bist-"+hisse_tanim+"-hisseleri/")
  df_bist100=pd.concat([df_bist100,test[1]])
  df_bist100=pd.concat([df_bist100,test[2]])
  df_bist100=pd.concat([df_bist100,test[3]]).reset_index()
  df_bist100=df_bist100.rename(columns={"Menkul":"Kod"})
  hisseler=df_bist100["Kod"].unique()
  hisseler=[x+'.IS' for x in hisseler]
  if endeks==True:
    hisseler.append("XU100.IS")
  if usd==True:
    hisseler.append("USDTRY=X")
  return hisseler


def backtesting_crossMA(ticker="GARAN.IS",start="2022-01-01",end="2022-12-16",ma1=10,ma2=20,cash=100000,commis=0.0005):
  from backtesting import Backtest, Strategy
  from backtesting.lib import crossover
  from backtesting.test import SMA

  df=yf.download(ticker,start=start,end=end,progress=False)

  class SmaCross(Strategy):
      n1 = ma1
      n2 = ma2

      def init(self):
          close = self.data.Close
          self.sma1 = self.I(SMA, close, self.n1)
          self.sma2 = self.I(SMA, close, self.n2)

      def next(self):
          if crossover(self.sma1, self.sma2):
              self.buy()
          elif crossover(self.sma2, self.sma1):
              self.sell()


  bt = Backtest(df, SmaCross,
                cash=cash, commission=commis,
                exclusive_orders=True)

  output = bt.run()
  
  return output,bt.plot(open_browser=False)


@st.cache()
def teknik_sira():
  from tradingview_ta import TA_Handler, Interval, Exchange
  import pandas as pd
  import numpy as np
  df_get_analysis=pd.DataFrame()
  df_get_analysis_full=pd.DataFrame()


  interv=[Interval.INTERVAL_5_MINUTES,Interval.INTERVAL_15_MINUTES,Interval.INTERVAL_30_MINUTES,Interval.INTERVAL_1_HOUR,Interval.INTERVAL_2_HOURS,Interval.INTERVAL_4_HOURS,Interval.INTERVAL_1_DAY,Interval.INTERVAL_1_WEEK]
  df_hist=pd.DataFrame()
  df_bist100=pd.DataFrame()
  test=pd.read_html("https://uzmanpara.milliyet.com.tr/canli-borsa/bist-100-hisseleri/")
  df_bist100=df_bist100.append(test[1])
  df_bist100=df_bist100.append(test[2])
  df_bist100=df_bist100.append(test[3]).reset_index()
  df_bist100=df_bist100.rename(columns={"Menkul":"Kod"})
  df_bist100 = df_bist100[~df_bist100['Kod'].astype(str).str.startswith('X')]

                        
  hisseler=df_bist100["Kod"].unique()


  df_get_analysis_full["Kod"]=hisseler

  for i in hisseler:
    try:
      analiz = TA_Handler(
          symbol=i,
          screener="turkey",
          exchange="BIST",
          interval=Interval.INTERVAL_1_DAY
      )
      result=analiz.get_analysis().summary
      df=pd.DataFrame.from_dict(result, orient='index').T
      df["Kod"]=i
      df=df.add_suffix("_1D")
      df=df.rename(columns={"Kod"+"_1D":"Kod"})
      df_get_analysis=df_get_analysis.append(df)
    except:
        print("hata",i)

  df_get_analysis["skor"]=df_get_analysis["BUY_1D"]-df_get_analysis["SELL_1D"]-df_get_analysis["NEUTRAL_1D"]
  df_get_analysis=df_get_analysis.sort_values(by="skor",ascending=False)
  df_get_analysis["sira"]=range(1,1+len(df_get_analysis))
  return df_get_analysis
