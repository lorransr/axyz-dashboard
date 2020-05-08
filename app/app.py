import sys
import pandas as pd
import plotly.express as px
import streamlit as st
import urllib
import json
import numpy as np
from PIL import Image
import sdk, about


def main():
    try:
        response = get_data()
        data = response["data"]
        create_layout(data)
    except Exception as e:
        st.sidebar.text(str(e))
        st.title("⭕️The data was not correctly loaded")


def get_logo():
    image = Image.open("https://raw.githubusercontent.com/lorransr/axyz-dashboard/master/app/assets/images/marca-axys.png")
    im = image.convert("RGBA")

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with black... (leaves alpha values alone...)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    data[..., :-1][white_areas.T] = (0, 0, 0)  # Transpose back needed

    im2 = Image.fromarray(data)
    return im2


@st.cache
def get_data():
    url = "https://j86umim9sa.execute-api.us-east-2.amazonaws.com/api/calibration"
    try:
        response = urllib.request.urlopen(url)
    except Exception as e:
        print(e)
    return json.loads(response.read())


def create_layout(data):
    logo = get_logo()
    st.image(logo, width=50)
    st.markdown("# axyz KPI Managment")
    st.sidebar.header("Menu")
    app_mode = st.sidebar.selectbox(
        "Please select a page", ["About", "SDK", "Maintenance"]
    )

    if app_mode == "SDK":
        sdk.load_page(data)
    if app_mode == "About":
        about.load_page()
    if app_mode == "Maintenance":
        st.write("\U0001F6D1 this session is under development")


if __name__ == "__main__":
    main()
