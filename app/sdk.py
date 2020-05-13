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

    # resample in year_week
    df_daily_filtered = df_daily[selected_columns].copy()
    year_week = df_daily_filtered.ride_end.dt.strftime("%Y-%U")
    df_daily_filtered.insert(0,"year_week",year_week)


    df_daily_reindexed = (df_daily_filtered
                        .groupby("year_week")[selected_columns[1:]]
                        .sum()
                        .reset_index())
    # prepare df to plot
    df_daily_melted = df_daily_reindexed.melt(id_vars="year_week")
    df_daily_melted.columns = ["year_week","calibration_result","count"]

    #calculating percentage
    df_perct = df_daily_reindexed.iloc[:,1:]
    df_perct = df_perct.div(df_perct.sum(axis=1), axis=0)
    df_perct.loc[:,"year_week"] = df_daily_reindexed.year_week
    df_perct_melted = df_perct.melt(id_vars="year_week")
    df_daily_melted.loc[:,"percentage"] = df_perct_melted["value"]

    # generate figure
    fig = px.bar(
        df_daily_melted,
        x="year_week",
        y="count",
        color="calibration_result",
        color_discrete_map=color_dict,
        hover_data= {
            "percentage":":.1%"},
        width=350,
        height=400
    )
    fig.update_xaxes(title = "Year - Week")
    fig.update_yaxes(title = "Number of Trips")
    fig.update_layout(
        title="Calibrations Results per Week of Year",
        xaxis = dict(
            tickmode = 'linear',
            fixedrange = True
        ),
        yaxis = dict(
            fixedrange = True
        )
    )
    for trace in fig.data:
        trace.name = trace.name.replace("_"," ")

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
        y="percentage",
        color="calibration_result",
        color_discrete_map=color_dict,
        hover_data={"percentage":":.1%",
                    "count":True},
        width=350,
        height=400
    )
    fig.update_xaxes(title="SDK version")
    fig.update_yaxes(title="Number of Trips")
    fig.update_layout(
        title="Calibrations Results per SDK Versions",
        xaxis = dict(
            tickmode = 'linear',
            fixedrange = True
            ),
        yaxis = dict(
            fixedrange = True
            ),
        yaxis_tickformat = '%'
        )
    for trace in fig.data:
        trace.name = trace.name.replace("_"," ")

    return fig

def path_to_image(pose):
    path = "https://raw.githubusercontent.com/lorransr/axyz-dashboard/master/app/assets/images/positions/{}.png".format(pose)
    return '<img src="'+ path + '" width="60" >'

def get_driver_summary(data):
    df_driver = pd.DataFrame(data["driver_summary"])
    df_driver.loc[:,"user_response_pose"] = df_driver.user_response_pose.astype("int")
    df_driver.loc[:,"position_image"] = (df_driver
    .user_response_pose
    .apply(lambda x: path_to_image(x)))
    df_driver = df_driver[df_driver.user_response_pose != 0]
    new_columns = []
    for column in df_driver.columns:
        new_columns.append(column.replace("_"," "))
    df_driver.columns  = new_columns
    return df_driver.to_html(escape=False)


def load_page(data):
    daily_overview = get_daily_overview_plot(data)
    version_overview = get_version_overview_plot(data)
    st.plotly_chart(daily_overview)
    st.plotly_chart(version_overview)
    st.markdown("### %Correct x User x Position")
    df_driver = get_driver_summary(data)
    # st_ms = st.multiselect("Columns", df_driver.columns.tolist(),df_driver.columns.tolist())
    st.markdown(df_driver, unsafe_allow_html=True)
