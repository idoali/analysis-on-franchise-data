import pandas as pd
import streamlit as st 
import plotly.express as px 
from datetime import datetime
import numpy as np 

data = pd.read_csv("data_input/data_franchise.csv")
updated_revenue = []

for i in range(len(data)):
    numb = data["revenue"][i]
    if len(numb.split(".")) <= 2:
        out = float(numb)
    else:
        anchor = len(data["revenue"][i-1].split(".")[0])
        new_numb = numb.replace(".", "")
        out = float(".".join([new_numb[:anchor]] + [new_numb[anchor:]]))
    updated_revenue.append(out)    
data["revenue"] = updated_revenue

jawa_bali = ["Jawa Tengah", "DI Yogyakarta", "Jawa Barat", "DKI Jakarta", "Banten", "Jawa Timur", "Bali"]

df_jawa_bali = data[(data["Province"].isin(jawa_bali)) & ([int(x.split("-")[1]) == 1 for x in data["month_period"]])]
avg_monthly = df_jawa_bali[["Province", "revenue"]].groupby("Province").mean().sort_values("revenue", ascending = True).reset_index()

data_prov = data[[x.split("-")[0] == "2021" for x in data.month_period]]["Province"].value_counts().index
rev_growth = []

for prov in data_prov:
    start = data[(data.Province == prov) & (data.month_period == "2021-01-01")]["revenue"].sum()
    end = data[(data.Province == prov) & (data.month_period == "2021-12-01")]["revenue"].sum()
    rev_growth.append(((end - start) / start) * 100)
    
rev_growth = pd.DataFrame({"province": data_prov,
                        "revenue_growth": rev_growth}).sort_values("revenue_growth", ascending = False)

years = [x.split("-")[0] for x in data["month_period"]]
months = [x.split("-")[1] for x in data["month_period"]]
data["date"] = [datetime(int(x), int(y), 1) for x, y in zip(years, months)]
data["date"] = pd.to_datetime(data["date"])

tab1, tab2 = st.tabs(["Answers", "Observe More"])

with tab1:
    st.title("Answers")
    fig_1 = px.bar(avg_monthly, x = "revenue", y = "Province", title = "Monthly Jawa-Bali Average Revenue",
                   hover_name = "Province", hover_data = {"Province": False},
                   labels = {"revenue": "Revenue"})
    st.plotly_chart(fig_1)

    fig_2 = px.bar(rev_growth.head(10).sort_values("revenue_growth", ascending = True), x = "revenue_growth", y = "province",
                   title = "Top 10 Provinces\nwith Highest Revenue Growth in 2021",
                   hover_name = "province", hover_data = {"province": False},
                   labels = {"province": "Province", "revenue_growth":"Revenue Growth (%)"})
    
    st.plotly_chart(fig_2)

with tab2:
    st.title("Revenue Plots")
    
    selected_class = st.multiselect("Select Product Class", data["class"].value_counts().index)
    selected_provinces = st.multiselect("Select Provinces", data.Province.value_counts().index)
    date_range = st.date_input("Select Date Range", [data['date'].min(), data['date'].max()])
    
    st.markdown("*Note: Remember to put two date inputs. If you get error, you probably just choose one date input*")
    
    date_min = pd.to_datetime(date_range[0])
    date_max = pd.to_datetime(date_range[1])

    
    # Filter data based on user input
    filtered_df = data[(data['date'] >= date_min) & (data['date'] <= date_max) &
                       (data["Province"].isin(selected_provinces)) & (data["class"].isin(selected_class))]
    filtered_df = filtered_df[["date", "Province", "revenue"]].groupby(["date", "Province"]).sum().reset_index()
    
    # Plot line chart using Plotly Express
    fig = px.line(filtered_df, x = 'date', y = "revenue", color = "Province")
    st.plotly_chart(fig)