# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
from plotly import graph_objects as go
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
from streamlit_extras.app_logo import add_logo
from st_on_hover_tabs import on_hover_tabs
#   from st_aggrid import GridOptionsBuilder, AgGrid
import pyrebase


st.set_page_config(layout="wide")


@st.cache_data
def load_data():
    config = {
        "apiKey": "AIzaSyDbzHvGGbzmRBgQy0nv3vF7vVXiY261un8",
        "authDomain": "practicemallproject.firebaseapp.com",
        "databaseURL": "https://practicemallproject-default-rtdb.firebaseio.com/",
        "projectId": "practicemallproject",
        "storageBucket": "practicemallproject.appspot.com",
        "messagingSenderId": "495688621544",
        "appId": "1:495688621544:web:39872f5fcaf9e186d0d85d",
        "measurementId": "G-L2BX8D4NFG"
    }
    
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    
    december_ov = pd.read_excel('Декабрь 22.xlsx')
    january_ov = pd.read_excel('Январь 22.xlsx')
    december = pd.DataFrame(db.child("december").get().val())
    january = pd.DataFrame(db.child("january").get().val())
    return december_ov, january_ov, december, january


december_ov, january_ov, december, january = load_data()



df = pd.concat([december, january])
df['Period'] = pd.to_datetime(df['Period'])
numericols = ['Area', 'AverageReceipt', 'Conversion',
       'FloorConversion','WholeConversion', 'salespercentarea', 
              'trafficm2In', 'wholetrafficpercent']

for col in numericols:
    df[col] = df[col].apply(lambda x: float(x.replace(',', '.')))

s = df['Zone'].str.split(',')
df['Zone'] = np.where(s.str.len() == 1, '', s.str[0])

df['Month'] = df['Period'].apply(
    lambda x: 'Декабрь' if x.month == 12 else 'Январь')
df.drop(['Period'], axis=1, inplace=True)


def caltotal(df1, df2, colname):
    newcol = df1[colname]+df2[colname]
    return np.array(newcol)[-1]


def calper(df1, df2, colname):
    delta = df2[colname]-df1[colname]
    delta = np.array(delta)[-1]
    decvalue = np.array(df1[colname])[-1]
    return delta/decvalue


st.markdown('<style>' + open('./style.css').read() +
            '</style>', unsafe_allow_html=True)


with st.sidebar:
    tabs = on_hover_tabs(tabName=['Целый ТЦ', 'Этажи', 'Арендаторы'],
                         iconName=['dashboard', 'money', 'economy'], default_choice=0)

if tabs == 'Целый ТЦ':
    st.write(" ")
    st.header(':department_store:Общие Метрики')
    col01, col02 = st.columns(2)
    december = st.checkbox('Декабрь')
    january = st.checkbox('Январь')

    st.markdown('</hr>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    if december and not january:
        col1.metric('Продажи', '{:,.0f}'.format(
            np.array(december_ov['Продажи, Основание'])[-1]))
        col2.metric('Посещаемость', '{:,.0f}'.format(
            np.array(december_ov['Посещаемость Вход, Основание'])[-1]))
        col3.metric('Кассовые Чеки', '{:,.0f}'.format(
            np.array(december_ov['Кассовые чеки, Основание'])[-1]))
        col4.metric('Посещаемость на м2', np.round(
            np.array(december_ov['Посещаемость м² Вход, Основание'])[-1], 2))
        col5.metric('Конверсия', df[df.Month ==
                    'Декабрь'].WholeConversion.values[0])
    elif january and not december:
        col1.metric('Продажи', '{:,.0f}'.format(np.array(january_ov['Продажи, Основание'])[
                    -1]), "{:.2%}".format(calper(december_ov, january_ov, 'Продажи, Основание')))
        col2.metric('Посещаемость', '{:,.0f}'.format(np.array(january_ov['Посещаемость Вход, Основание'])[
                    -1]), "{:.2%}".format(calper(december_ov, january_ov, 'Посещаемость Вход, Основание')))
        col3.metric('Кассовые Чеки', '{:,.0f}'.format(np.array(january_ov['Кассовые чеки, Основание'])[
                    -1]), "{:.2%}".format(calper(december_ov, january_ov, 'Кассовые чеки, Основание')))
        col4.metric('Посещаемость на м2', np.round(np.array(january_ov['Посещаемость м² Вход, Основание'])[
                    -1], 2), "{:.2%}".format(calper(december_ov, january_ov, 'Посещаемость м² Вход, Основание')))
        col5.metric('Конверсия', df[df.Month == 'Январь'].WholeConversion.values[0], "{:.2%}".format(
            (df[df.Month == 'Январь'].WholeConversion.values[0]-df[df.Month == 'Декабрь'].WholeConversion.values[0])/df[df.Month == 'Декабрь'].WholeConversion.values[0]))
    else:
        col1.metric('Продажи', '{:,.0f}'.format(
            caltotal(december_ov, january_ov, 'Продажи, Основание')))
        col2.metric('Посещаемость', '{:,.0f}'.format(
            caltotal(december_ov, january_ov, 'Посещаемость Вход, Основание')))
        col3.metric('Кассовые Чеки', '{:,.0f}'.format(
            caltotal(december_ov, january_ov, 'Кассовые чеки, Основание')))
        col4.metric('Посещаемость на м2', np.round(
            caltotal(december_ov, january_ov, 'Посещаемость м² Вход, Основание'), 2))
        col5.metric('Конверсия', np.round(df.WholeConversion.mean(), 2))
    
    st.write(" ")
    st.write(" ")
    st.write(" ")

    selectmetric = st.selectbox("Выберите Метрику", [
                                'Продажи', 'Посещаемость', 'Кассовые Чеки', 'Посещаемость на м2', 'Конверсия'])
    col1, col2 = st.columns(2)
    if selectmetric == 'Продажи':
        fig = px.bar(df, x=['Sales'], y='Month', color='Floor', orientation='h', labels={
                     "Month": "Месяц",
                     "Sales": "Продажи(тг)",
                     "Floor": "Этаж"
                     })
        salesmean = df.groupby('Tenant')['Sales'].mean()
        top5 = list(salesmean.sort_values(ascending=False).head(10).keys())
        dftop5 = df[df.Tenant.map(lambda x: True if x in top5 else False)]
        fig2 = go.Figure()
        newdict = dftop5[dftop5.Month == 'Декабрь'][[
            'Tenant', 'Sales']].set_index('Tenant').to_dict()['Sales']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Декабрь',
                              marker_color='#83c9ff'))
        newdict = dftop5[dftop5.Month == 'Январь'][[
            'Tenant', 'Sales']].set_index('Tenant').to_dict()['Sales']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Январь',
                              marker_color='crimson'))
        fig2.update_layout(barmode='group', yaxis=dict(
            title='Продажи'), xaxis_tickangle=-45, title='Топ Арендаторов по Продажам', width=420)
    elif selectmetric == 'Посещаемость':
        fig = px.bar(df, x=['trafficIn'], y='Month', color='Floor', orientation='h', labels={
                     "Month": "Месяц",
                     "trafficIn": "Посещаемость",
                     "Floor": "Этаж"
                     })
        salesmean = df.groupby('Tenant')['trafficIn'].mean()
        top5 = list(salesmean.sort_values(ascending=False).head(10).keys())
        dftop5 = df[df.Tenant.map(lambda x: True if x in top5 else False)]
        fig2 = go.Figure()
        newdict = dftop5[dftop5.Month == 'Декабрь'][['Tenant', 'trafficIn']].set_index(
            'Tenant').to_dict()['trafficIn']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Декабрь',
                              marker_color='#83c9ff'))
        newdict = dftop5[dftop5.Month == 'Январь'][['Tenant', 'trafficIn']].set_index(
            'Tenant').to_dict()['trafficIn']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Январь',
                              marker_color='crimson'))
        fig2.update_layout(barmode='group', yaxis=dict(title='Посещаемость'),
                           xaxis_tickangle=-45, title='Топ Арендаторов по Посещениям', width=420)
    elif selectmetric == 'Кассовые Чеки':
        fig = px.bar(df, x=['Receipts'], y='Month', color='Floor', orientation='h', labels={
                     "Month": "Месяц",
                     "Receipts": "Кассовые Чеки",
                     "Floor": "Этаж"
                     })
        salesmean = df.groupby('Tenant')['Receipts'].mean()
        top5 = list(salesmean.sort_values(ascending=False).head(10).keys())
        dftop5 = df[df.Tenant.map(lambda x: True if x in top5 else False)]
        fig2 = go.Figure()
        newdict = dftop5[dftop5.Month == 'Декабрь'][[
            'Tenant', 'Receipts']].set_index('Tenant').to_dict()['Receipts']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Декабрь',
                              marker_color='#83c9ff'))
        newdict = dftop5[dftop5.Month == 'Январь'][['Tenant', 'Receipts']].set_index(
            'Tenant').to_dict()['Receipts']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Январь',
                              marker_color='crimson'))
        fig2.update_layout(barmode='group', yaxis=dict(title='Кассовые Чеки'),
                           xaxis_tickangle=-45, title='Топ Арендаторов по Количеству Чеков', width=420)
    elif selectmetric == 'Посещаемость на м2':
        fig = px.bar(df, x=['trafficm2In'], y='Month', color='Floor', orientation='h', labels={
                     "Month": "Месяц",
                     "trafficm2In": "Посещаемость на м2",
                     "Floor": "Этаж"
                     })
        salesmean = df.groupby('Tenant')['trafficm2In'].mean()
        top5 = list(salesmean.sort_values(ascending=False).head(10).keys())
        dftop5 = df[df.Tenant.map(lambda x: True if x in top5 else False)]
        fig2 = go.Figure()
        newdict = dftop5[dftop5.Month == 'Декабрь'][[
            'Tenant', 'trafficm2In']].set_index('Tenant').to_dict()['trafficm2In']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Декабрь',
                              marker_color='#83c9ff'))
        newdict = dftop5[dftop5.Month == 'Январь'][['Tenant', 'trafficm2In']].set_index(
            'Tenant').to_dict()['trafficm2In']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Январь',
                              marker_color='crimson'))
        fig2.update_layout(barmode='group', yaxis=dict(title='Посещаемость на м2'),
                           xaxis_tickangle=-45, title='Топ Арендаторов по Посещаемости на м2', width=420)
    else:
        convmean = df.groupby(['Floor', 'Month'])['Conversion'].mean()
        convmean = pd.DataFrame(convmean).reset_index()
        fig = px.bar(convmean, x=['Conversion'],
                     color='Floor', y='Month', orientation='h')
        salesmean = df.groupby('Tenant')['Conversion'].mean()
        top5 = list(salesmean.sort_values(ascending=False).head(10).keys())
        dftop5 = df[df.Tenant.map(lambda x: True if x in top5 else False)]
        fig2 = go.Figure()
        newdict = dftop5[dftop5.Month == 'Декабрь'][[
            'Tenant', 'Conversion']].set_index('Tenant').to_dict()['Conversion']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Декабрь',
                              marker_color='#83c9ff'))
        newdict = dftop5[dftop5.Month == 'Январь'][['Tenant', 'Conversion']].set_index(
            'Tenant').to_dict()['Conversion']
        fig2.add_trace(go.Bar(x=list(newdict.keys()), y=list(newdict.values()), name='Январь',
                              marker_color='crimson'))
        fig2.update_layout(barmode='group', yaxis=dict(
            title='Конверсия'), xaxis_tickangle=-45, title='Топ Арендаторов по Конверсии', width=420)
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    
    
    
elif tabs == 'Этажи':
    st.write(" ")
    st.header(':ladder:Метрики по Этажам')
    floor = st.multiselect(
        "Фильтр Этажов", df.Floor.unique(), df.Floor.unique())
    st.write("                     ")
    december = st.checkbox('Декабрь')
    january = st.checkbox('Январь')
    st.write("   ")
    if december and not january:
        selection_query = df[df.Month == 'Декабрь']
    elif january and not december:
        selection_query = df[df.Month == 'Январь']
    else:
        selection_query = df
    selection_query = selection_query.query("Floor==@floor")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('Продажи', '{:,.0f}'.format(selection_query.Sales.sum()))
    col2.metric('Посещаемость', '{:,.0f}'.format(
        selection_query.trafficIn.sum()))
    col3.metric('Кассовые Чеки', '{:,.0f}'.format(
        selection_query.Receipts.sum()))
    col4.metric('Посещаемость на м2', np.round(
        selection_query.trafficm2In.sum(), 2))
    col5.metric('Конверсия', np.round(
        selection_query.FloorConversion.mean(), 2))
    
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        data = selection_query.groupby(['Floor', 'Month']).Sales.sum(
        ).sort_values(ascending=False).reset_index()
        figsale = px.funnel(data, x='Sales', y='Floor',
                            color='Month', height=400)
        st.plotly_chart(figsale, use_container_width=True)
    with col2:
        data = selection_query.groupby(['Floor', 'Month']).trafficIn.sum(
        ).sort_values(ascending=False).reset_index()
        figsale = px.funnel(data, x='trafficIn', y='Floor',
                            color='Month', height=400)
        st.plotly_chart(figsale, use_container_width=True)
    with col3:
        data = selection_query.groupby(['Floor', 'Month']).Receipts.sum(
        ).sort_values(ascending=False).reset_index()
        figsale = px.funnel(data, x='Receipts', y='Floor',
                            color='Month', height=400)
        st.plotly_chart(figsale, use_container_width=True)
    with col4:
        data = selection_query.groupby(['Floor', 'Month']).trafficm2In.sum(
        ).sort_values(ascending=False).reset_index()
        figsale = px.funnel(data, x='trafficm2In',
                            y='Floor', color='Month', height=400)
        st.plotly_chart(figsale, use_container_width=True)
    with col5:
        data = selection_query.groupby(
            ['Floor', 'Month']).Conversion.mean().reset_index()
        figsale = px.funnel(data, x='Conversion', y='Floor',
                            color='Month', height=400)
        st.plotly_chart(figsale, use_container_width=True)
    st.write("   ")
    
    col1, col2 = st.columns(2)
    with col1:
        data = selection_query.groupby(
            ['Tenant', 'Month']).Sales.sum().reset_index()
        fig4 = px.funnel(data, x='Sales', y='Tenant', color='Month', height=825, labels={
                         "Month": "Месяц", "Tenant": " "}, color_discrete_sequence=['crimson', '#83c9ff'], title="Воронка Продаж по месяцам")
        st.plotly_chart(fig4, use_container_width=True)

        data = selection_query.groupby(
            ['Tenant', 'Month']).Receipts.sum().reset_index()
        fig4 = px.funnel(data, x='Receipts', y='Tenant', color='Month', height=825, labels={
                         "Month": "Месяц", "Tenant": " "}, color_discrete_sequence=['crimson', '#83c9ff'], title="Воронка Количества чеков по месяцам")
        st.plotly_chart(fig4, use_container_width=True)
    with col2:
        data = selection_query.groupby(
            ['Tenant', 'Month']).trafficIn.sum().reset_index()
        fig4 = px.funnel(data, x='trafficIn', y='Tenant', color='Month', height=825, labels={
                         "Month": "Месяц", "Tenant": " "}, color_discrete_sequence=['crimson', '#83c9ff'], title="Воронка Посещаемости по месяцам")
        st.plotly_chart(fig4, use_container_width=True)

        data = selection_query.groupby(
            ['Tenant', 'Month']).trafficm2In.sum().reset_index()
        fig4 = px.funnel(data, x='trafficm2In', y='Tenant', color='Month', height=825, labels={
                         "Month": "Месяц", "Tenant": " "}, color_discrete_sequence=['crimson', '#83c9ff'], title="Воронка Посещаемости на м2 по месяцам")
        st.plotly_chart(fig4, use_container_width=True)

    # st.title("Paper")
    #st.write('Name of option is {}'.format(tabs))

elif tabs == 'Арендаторы':
    st.write("  ")
    st.header(':convenience_store:Метрики по Арендаторам')
    tenant = st.selectbox("Выберите Арендатора:", df.Tenant.unique())
    
    december = st.checkbox('Декабрь')
    january = st.checkbox('Январь')
    st.write("   ")
    if december and not january:
        selection_query = df[df.Month == 'Декабрь']
    elif january and not december:
        selection_query = df[df.Month == 'Январь']
    else:
        selection_query = df
    selection_query = selection_query.query("Tenant==@tenant")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('Продажи', '{:,.0f}'.format(selection_query.Sales.mean()))
    col2.metric('Посещаемость', '{:,.0f}'.format(
        selection_query.trafficIn.mean()))
    col3.metric('Кассовые Чеки', '{:,.0f}'.format(
        selection_query.Receipts.mean()))
    col4.metric('Посещаемость на м2', np.round(
        selection_query.trafficm2In.sum(), 2))
    col5.metric('Конверсия', np.round(
        selection_query.Conversion.mean(), 2))
    
    with col1:
        f1 = px.bar(selection_query, x='Month', y = 'Sales', color='Month', labels={"Month":"Месяц", "Sales": "Продажи", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
    with col2:
        f1 = px.bar(selection_query, x='Month', y = 'trafficIn', color='Month', labels={"Month":"Месяц", "trafficIn": "Посещаемость", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
    with col3:
        f1 = px.bar(selection_query, x='Month', y = 'Receipts', color='Month', labels={"Month":"Месяц", "Receipts": "Кассовые Чеки", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
    with col4:
        f1 = px.bar(selection_query, x='Month', y = 'trafficm2In', color='Month', labels={"Month":"Месяц", "trafficm2In": "Посещаемость на м2", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
    with col5:
        f1 = px.bar(selection_query, x='Month', y = 'Conversion', color='Month', labels={"Month":"Месяц", "Conversion": "Конверсия", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
    st.write(" ")
    
    
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.title('Арендаторы по Категориям')
    category = st.selectbox("Выберите Категорию:", df.Category.unique())
    selection_query = df.query("Category==@category")
    col1, col2 = st.columns(2)
    with col1:
        f1 = px.bar(selection_query, x='Tenant', y = 'Sales', color='Month', labels={"Month":"Месяц", "Sales": "Продажи", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
        
        f1 = px.bar(selection_query, x='Tenant', y = 'Receipts', color='Month', labels={"Month":"Месяц", "Receipts": "Количество Чеков", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True) 
    with col2:
        f1 = px.bar(selection_query, x='Tenant', y = 'trafficIn', color='Month', labels={"Month":"Месяц", "trfficIn": "Посещаемость", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True)
        
        f1 = px.bar(selection_query, x='Tenant', y = 'trafficm2In', color='Month', labels={"Month":"Месяц", "trafficm2In": "Посещаемость на м2", "Tenant": " "})
        st.plotly_chart(f1, use_container_width=True) 
    
    
    # st.title("Tom")
    #st.write('Name of option is {}'.format(tabs))
