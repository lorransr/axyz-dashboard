import pandas as pd
import plotly.express as px
import streamlit as st

color_dict = {
    "correct": "green",
    "generic_position": "gray",
    "no_calibration": "goldenrod",
    "incorrect": "red",
}


def get_daily_overview_plot(data):

    # set datetime
    df_daily = pd.DataFrame(data["daily_overview"])
    df_daily.ride_end = pd.to_datetime(df_daily.ride_end)

    # select columns without "pct"
    selected_columns = []
    for column in df_daily.columns.to_list():
        if "pct" in column:
            continue
        else:
            selected_columns.append(column)
    df_daily_filtered = df_daily[selected_columns]

    # fill empty days
    first_date = df_daily_filtered.loc[0, "ride_end"]
    last_date = df_daily_filtered.iloc[-1, 0]
    idx = pd.date_range(first_date, last_date)
    idx.name = "ride_end"
    df_daily_reindexed = (
        df_daily_filtered.set_index("ride_end").reindex(idx, fill_value=0).reset_index()
    )

    # prepare df to plot
    df_daily_melted = df_daily_reindexed.melt(id_vars="ride_end")
    df_daily_melted.columns = ["date", "calibration_result", "count"]

    #calculating percentage
    df_perct = df_daily_reindexed.iloc[:,1:]
    df_perct = df_perct.div(df_perct.sum(axis=1), axis=0)
    df_perct.loc[:,"ride_end"] = df_daily_reindexed.ride_end
    df_perct_melted = df_perct.melt(id_vars="ride_end")
    df_daily_melted.loc[:,"percentage"] = df_perct_melted["value"]

    # generate figure
    fig = px.bar(
        df_daily_melted,
        x="date",
        y="count",
        color="calibration_result",
        color_discrete_map=color_dict,
        hover_data= {
            "percentage":":.1%"}
    )
    fig.update_xaxes(title="Recent Trips")
    fig.update_yaxes(title="Number of Trips")
    fig.update_layout(
        title="Calibrations Results per Day", xaxis=dict(tickmode="linear",)
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
    df_version_melted = df_version.melt(
        id_vars="sdk_version",
        value_vars=selected_columns,
        var_name="calibration_result",
        value_name="count",
    )

    #calculating percentage
    df_perct = df_version.iloc[:,1:4]
    df_perct = df_perct.div(df_perct.sum(axis=1), axis=0)
    df_perct.loc[:,"sdk_version"] = df_version.sdk_version
    df_perct_melted = df_perct.melt(id_vars="sdk_version")
    df_version_melted.loc[:,"percentage"] = df_perct_melted["value"]

    fig = px.bar(
        df_version_melted,
        x="sdk_version",
        y="count",
        color="calibration_result",
        color_discrete_map=color_dict,
        hover_data={"percentage":":.1%"}
    )
    fig.update_xaxes(title="SDK version")
    fig.update_yaxes(title="Number of Trips")
    fig.update_layout(title="Calibrations Results per SDK Versions")
    return fig


def get_driver_summary(data):
    df_driver = pd.DataFrame(data["driver_summary"])
    return df_driver


def load_page(data):
    daily_overview = get_daily_overview_plot(data)
    version_overview = get_version_overview_plot(data)
    st.plotly_chart(daily_overview)
    st.plotly_chart(version_overview)
    st.markdown("### %Correct x User x Position")
    df_driver = get_driver_summary(data)
    st_ms = st.multiselect("Columns", df_driver.columns.tolist(),df_driver.columns.tolist())
    st.dataframe(df_driver.loc[:,st_ms])