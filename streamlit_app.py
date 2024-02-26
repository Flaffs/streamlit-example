import pandas as pd
import streamlit as st
import influxdb_client
import plotly.express as px
from datetime import datetime

from streamlit_date_picker import date_range_picker


bucket = st.secrets["BUCKET"]
org = st.secrets["ORG"]
token = st.secrets["TOKEN"]
url=st.secrets["URL"]

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

# zeit intervall auswählen
datetime_string = date_range_picker(start=0, end=0, unit='minutes', key='range_picker')

start_date = int(datetime.strptime(datetime_string[0], '%Y-%m-%d %H:%M:%S').timestamp())
end_date = int(datetime.strptime(datetime_string[1], '%Y-%m-%d %H:%M:%S').timestamp())

time_picker = {"start_date": start_date, "end_date": end_date}

# Dropdown-Menü für die aggregate
time_intervals = {
    "raw": None,
    "1 Minute": "1m",
    "2 Minuten": "2m",
    "5 Minuten": "5m",
    "10 Minuten": "10m",
    "30 Minuten": "30m",
    "1 Stunde": "1h",
    "2 Stunden": "2h",
    "4 Stunden": "4h",
    "1 Tag": "1d"
}

selected_interval = st.selectbox("Aggregate Intervall", list(time_intervals.keys()))


def get_data(interval):
    global time_picker

    st.write(interval)

    query_api = client.query_api()
    query = 'from(bucket: "CO2-Messer")\
        |> range(start: ' + str(time_picker["start_date"]) + ', stop: ' + str(time_picker["end_date"]) + ')\
        |> filter(fn: (r) => r._measurement == "CO2-Messer")\
        |> filter(fn: (r) => r._field == "temperature")'

    if interval:
        query += '|> aggregateWindow(every: ' + str(interval) + ', fn: mean)'

    print("das ist die query: ")
    print(query)

    result = query_api.query(org=org, query=query)

    data = []
    for table in result:
        for record in table.records:
            data.append((record.get_time(), record.get_field(), record.get_value()))

    df = pd.DataFrame(data, columns=["time", "field", "value"])

    return df


# Button zum Ausführen der Abfrage
if st.button("Daten abrufen"):

    interval = time_intervals[selected_interval]
    df = get_data(interval)

    # Plot mit Plotly
    fig = px.line(df, x="time", y="value", title='Temperature Over Time', width=800, height=400)

    # Zeige den Plot mit st.plotly_chart() an
    st.plotly_chart(fig)
