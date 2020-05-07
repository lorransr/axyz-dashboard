import sys
import pandas as pd
import plotly.express as px
import streamlit as st
import urllib
import json
import numpy as np
from PIL import Image

url = "https://j86umim9sa.execute-api.us-east-2.amazonaws.com/api/calibration"
color_dict = {
                "correct": "green",
                "generic_position": "gray",
                "no_calibration": "goldenrod",
                "incorrect": "red"}

def get_logo():
    image = Image.open("assets/images/marca-axys.png")
    im = image.convert('RGBA')

    data = np.array(im)   # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    data[..., :-1][white_areas.T] = (0, 0, 0) # Transpose back needed

    im2 = Image.fromarray(data)
    return im2

logo = get_logo()
st.image(logo,width = 50)
'''
# axyz KPI Managment
'''


@st.cache
def get_data():
    try:
        response = urllib.request.urlopen(url)
    except Exception as e:
        print(e)
    return json.loads(response.read())

def get_daily_overview_plot(data):

    #set datetime
    df_daily = pd.DataFrame(data["daily_overview"])
    df_daily.ride_end = pd.to_datetime(df_daily.ride_end)

    #select columns without "pct"
    selected_columns = []
    for column in df_daily.columns.to_list():
        if "pct" in column:
            continue
        else:
            selected_columns.append(column)
    df_daily_filtered = df_daily[selected_columns]

    #fill empty days
    first_date = df_daily_filtered.loc[0,"ride_end"]
    last_date = df_daily_filtered.iloc[-1,0]
    idx = pd.date_range(first_date, last_date)
    idx.name = "ride_end"
    df_daily_reindexed = (df_daily_filtered
                        .set_index("ride_end")
                        .reindex(idx,fill_value=0)
                        .reset_index())

    #prepare df to plot
    df_daily_melted = df_daily_reindexed.melt(id_vars="ride_end")
    df_daily_melted.columns = ["date","calibration_result","count"]

    #generate figure
    fig = px.bar(
        df_daily_melted,
        x="date",
        y="count",
        color="calibration_result",
        color_discrete_map=color_dict)
    fig.update_xaxes(title = "Recent Trips")
    fig.update_yaxes(title = "Number of Trips")
    fig.update_layout(
        title="Calibrations Results per Day",
        xaxis = dict(
            tickmode = 'linear',
        )
    )
    return fig

def get_version_overview_plot(data):
    df_version = pd.DataFrame(data["version_overview"])
    selected_columns = []
    for column in df_version.columns.to_list():
        if "pct" in column:
            continue
        else:
            selected_columns.append(column)
    selected_columns.remove("sdk_version")
    df_version_melted = df_version.melt(id_vars="sdk_version",value_vars = selected_columns,var_name="calibration_result",value_name="count")

    fig = px.bar(df_version_melted,
        x="sdk_version",
        y = "count",
        color = "calibration_result",
        color_discrete_map=color_dict)
    fig.update_xaxes(title = "SDK version")
    fig.update_yaxes(title = "Number of Trips")
    fig.update_layout(
        title="Calibrations Results per SDK Versions"
    )
    return fig

def get_driver_summary(data):
    df_driver = pd.DataFrame(data["driver_summary"])
    return df_driver

def load_page():
    daily_overview = get_daily_overview_plot(data)
    version_overview = get_version_overview_plot(data)
    st.plotly_chart(daily_overview)
    st.plotly_chart(version_overview)

    '''
    ### %Correct x User x Position
    '''
    df_driver = get_driver_summary(data)
    st.dataframe(df_driver)



response = get_data()
data=response["data"]

st.sidebar.header("Menu")
app_mode = st.sidebar.selectbox("Please select a page", ["About",
                                                             "SDK",
                                                             "Maintenance"])

if app_mode == "SDK":
    load_page()
if app_mode == "About":
    st.write("This page contains information about axyz iA's that are currently running \U0001F4BB")
if app_mode == "Maintenance":
    st.write("\U0001F6D1 this session is under development")


