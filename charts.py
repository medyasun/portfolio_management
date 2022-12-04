import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
plt.style.use("fivethirtyeight")

def chart_return(df):
   
    returns_cumsum=df.pct_change().cumsum()
    title="Hisse Getirisi"
    my_stocks=df
    for c in my_stocks.columns.values:
        plt.plot(my_stocks[c],label=c)

    
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Own Country Currency",fontsize=18)
    plt.legend(my_stocks.columns.values,loc="upper left")
    return plt