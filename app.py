import streamlit as st
from calculations import df_port,expected_return,opt_port,get_stock_list
from charts import chart_return
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
import time

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


with st.sidebar:
    st.image("https://cdn.freebiesupply.com/logos/large/2x/stock-logo-png-transparent.png")
    selected=option_menu(
        menu_title=None,
        options=["Portföy Test Et","Otomatik Portföy","Teknik Analizler"],
        icons=["app-indicator","activity","graph-up-arrow"],
        styles={"nav-link-selected": {"background-color": "#0be494"}}
    )



if selected=="Portföy Test Et":
    sd, ed = st.columns(2)
    startd = sd.date_input("Start Date",datetime.date(2022, 1, 1))
    endd = ed.date_input("End Date")
    assets=st.text_input("Please Enter Your Portfolio")
    amount=st.text_input("Yatırmak İstediğiniz Bakiyeyi Belirtiniz")
    assets=assets.upper()
    assets=assets.split(",")
    assets=[i+".IS" for i in assets]
    submit=st.button("Portföyü Test Et")
    if submit:
        if len(assets)>7:
            st.error("Portföyünde En Fazla 7 Hisse Olabilir!!!")
        else:
  
                df=df_port(assets=assets,startd=startd,endd=endd)
                precent_return,percent_volatility,percent_var,weights=expected_return(df,assets)
                chart_return=chart_return(df)

                ear,av,sr,allocation,leftover=opt_port(df,amount)

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
    if selection=="Portföyümün Teknik Analizi":
        st.markdown(assets)




