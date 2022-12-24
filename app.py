import streamlit as st
from calculations import df_port,expected_return,opt_port,get_stock_list,backtesting_crossMA,teknik_sira,grafik_prophet,genel_bilgiler,test
from charts import chart_return
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import time
import math
import yfinance as yf

st.set_page_config(layout="wide")

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

reduce_header_height_style = """
    <style>
        div.block-container {padding-top:0rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

st.header("BIST50 ile Portföyünü Analiz Et")
st.markdown("""---""")


with st.sidebar:
    selected=option_menu(
        menu_title=None,
        options=["Genel Bilgiler","Portföy Test Et","Otomatik Portföy","Teknik Analizler","Strateji Test","Tahmin Oluştur"],
        icons=["broadcast","app-indicator","activity","graph-up-arrow","bi-clock-history","gift"],
        styles={"nav-link-selected": {"background-color": "#0be494"}}
    )

if selected=="Genel Bilgiler":
    stock=st.text_input("Hisse Kodunu Giriniz")
    bistmi=st.checkbox("BIST",value=True)

    submit=st.button("Bilgileri Getir")
    if submit:
        if bistmi==True:
            stock=stock+".IS"

        
        logo,short_name,pddd,fd_favok,ozsermaye_borc,piyasa_degeri,hisse_adedi,temettu_verimi,guncel_fiyat,onceki_kapanis,net_kar_buyume_orani=genel_bilgiler(stock)
        
        with st.expander("Genel Bilgiler",expanded=True):
            i1,i2,i3,i4,i5=st.columns(5)
            i1.image(logo)
            i2.metric("Güncel Fiyat",str(guncel_fiyat),round(((guncel_fiyat-onceki_kapanis)/onceki_kapanis)*100,2))
            i3.metric("PD/DD",str(round(pddd,2)))
            i4.metric("FD/FAVOK",str(round(fd_favok,2)))
            i5.metric("Piyasa Değeri (mn TL)",f'{round(piyasa_degeri/1000000,0):,}')
            
        st.subheader(short_name)

if selected=="Portföy Test Et":
    sd, ed = st.columns(2)
    startd = sd.date_input("Başlangıç Tarihi",datetime.date(2022, 1, 1))
    endd = ed.date_input("Bitiş Tarihi")
    assets=st.text_input("Portföyünüzdeki Hisselerin Kodlarını Giriniz-Hisseleri Virgül İle ayırabilirsiniz")
    amount=st.text_input("Yatırmak İstediğiniz Bakiyeyi Belirtiniz")
    assets=assets.upper()
    assets=assets.split(",")
    assets=[i+".IS" for i in assets]
    submit=st.button("Portföyü Test Et")
    if submit:
        if len(assets)>7:
            st.error("Portföyünde En Fazla 7 Hisse Olabilir!!!")
        else:
            try:
                df=df_port(assets=assets,startd=startd,endd=endd)
                precent_return,percent_volatility,percent_var,weights=expected_return(df,assets)
                chart_return=chart_return(df)

                ear,av,sr,allocation,leftover=opt_port(df,amount)

                with st.expander("Genel Metrikler",expanded=True):
                    h1, h2, h3,h4 = st.columns(4)
                    h1.metric("Total Return", precent_return,help="Yıllık Kazandırdığı Tutarı Gösterir")
                    h2.metric("Volatility", percent_volatility)
                    h3.metric("Varyans",percent_var )
                    h4.metric("Equal Weights",str(round(weights[0]*100,2))+"%")


                    o1, o2, o3,o4 = st.columns(4)
                    o1.metric("Total Return", str(round(ear*100,2))+"%")
                    o2.metric("Volatility", str(round(av*100,2))+"%")
                    o3.metric("Sharp Ratio",round(sr,2) )
                    o4.metric("Kalan Para",str(round(leftover,2)))

                r1,r2=st.columns(2)

                r1.dataframe(allocation)
                r2.pyplot(chart_return)
            except:
                st.error("Hisse Kodlarını Kontrol Ediniz. Bazı Hisse Bilgileri Sistemde Kayıtlı Olmayabilir!!!")


if selected=="Otomatik Portföy":  
    sd, ed = st.columns(2)
    startd = sd.date_input("Start Date",datetime.date(2022, 1, 1))
    endd = ed.date_input("End Date")
    hisse_sec=st.selectbox("Portöy Hisselerini Nereden Seçelim",options=["Bist100","Bist30","Bist Tüm"])
    #assets=[i+".IS" for i in assets]
    amount=st.text_input("Yatırmak İstediğiniz Bakiyeyi Belirtiniz")
    submit=st.button("Otomatik Portföy Oluştur")
    if submit:
        with st.spinner("Hesaplamalar Yapılırken Biraz Beklemenizi Rica Ederim"):
            if hisse_sec=="Bist100":
                assets="100"
            elif hisse_sec=="Bist30":
                assets="30"
            elif hisse_sec=="Bist Tüm":
                assets="tum"
            assets=get_stock_list(hisse_tanim=assets,endeks=False,usd=False)
            df=df_port(assets=assets,startd=startd,endd=endd)
            ear,av,sr,allocation,leftover=opt_port(df,amount)
            o1, o2, o3,o4 = st.columns(4)
            o1.metric("Total Return", str(round(ear*100,2))+"%")
            o2.metric("Volatility", str(round(av*100,2))+"%")
            o3.metric("Sharp Ratio",round(sr,2) )
            o4.metric("Kalan Para",str(round(leftover,2)))

            st.dataframe(allocation)

if selected=="Teknik Analizler":
    selection=st.radio("Hisse Tipi Seç",options=("Portföyümün Teknik Analizi","Bist100 ün En İyileri","Tüm Borsa En İyiler"),horizontal=True)
    if selection=="Bist100 ün En İyileri":
        with st.spinner("Hesaplamalar Yapılırken Biraz Beklemenizi Rica Ederim"):
            AgGrid(teknik_sira())



if selected=="Strateji Test":  
    st.caption("Stratejileri Kullanarak Para yatırsaydın Ne Olurdu?")
    str1, str2, str3 = st.columns(3)
    stocks=str1.text_input("Hisse Kodunu Giriniz","GARAN.IS")
    startdate = str2.date_input("Test Başlangıç Dönemini Giriniz",datetime.date(2022, 1, 1))
    enddate = str3.date_input("Test Bitiş Dönemini Giriniz")
    str4, str5, str6 = st.columns(3)

    str_bakiye=str4.text_input("Başlangıç Bakiyeniz",100000)
    hoper1=str5.text_input("Hareketli Ortalama Periodu",10)
    hoper2=str6.text_input("Hareketli Ortalama Periodu",20)
    #riskperc=str6.text_input("Her İşlemde Anaparanızın Ne Kadarını Riske Atacaksınız",20)
    strateji_olustur=st.button("Stratejiyi Test Et")
    if strateji_olustur:
        output,fig=backtesting_crossMA(ticker=stocks,start=startdate,end=enddate,ma1=int(hoper1),ma2=int(hoper2),cash=float(str_bakiye),commis=0.0005)
        sr1,sr2,sr3,sr4,sr5,sr6=st.columns(6)
        sr1.metric("Son Bakiye", "{:,}".format(math.floor(output[4])),help="Belirttiğin Tarih aralığının son günü elindeki bakiye.")
        sr2.metric("Getiri", "%"+str(round(output[6],2)),help="Belirttiğin Tarih aralığındaki yüzdesel getiri")
        sr3.metric("Al Bekle Getirisi", "%"+str(round(output[7],2)),help="Hiç strateji yapmayıp tarih aralığının ilk günü alıp son günü satsaydın oluşacak bakiye.")
        sr4.metric("En Büyük Kayıp", "%"+str(round(output[13],2)),help="Anaparanın en fazla düştüğü oran.")
        sr5.metric("Volatilite","%"+str(round(output[9],2)),help="Ortalama bakiyenin hareket aralığı")
        sr6.metric("Sharp Rasyosu","%"+str(round(output[10],2)),help="Oranın yüksek olması oluşturulan portföyün risklere karşı dayanıklı olduğu, düşük olması ise oluşturulan portföyün risklere açık olduğu anlamına gelir.")
        st.bokeh_chart(fig)


if selected=="Tahmin Oluştur":
    st.caption("Zaman Serisi Analizi İle Trend Tahmini")
    str1, str2, str3, str4 = st.columns(4)
    stocks=str1.text_input("Hisse Kodunu Giriniz","GARAN.IS")
    startdate = str2.date_input("Test Başlangıç Dönemini Giriniz",datetime.date(2020, 1, 1))
    enddate = str3.date_input("Test Bitiş Dönemini Giriniz")
    predict_date=str4.text_input("İleride Kaç Gün Tahminlemek İstersin",120)
    tahmin=st.button("Geleceği Tahmin Et")
    if tahmin:
        df=yf.download(stocks,start=startdate,end=enddate,progress=False)["Adj Close"].reset_index()
        st.set_option('deprecation.showPyplotGlobalUse', False)
        predict=grafik_prophet(df,asset=stocks,predict=int(predict_date))
        st.pyplot(predict)
