import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import influxdb_client
import plotly.express as px
from datetime import datetime, timedelta
from influxdb_client.client.write_api import SYNCHRONOUS


bucket = st.secrets["BUCKET"]
org = st.secrets["ORG"]
token = st.secrets["TOKEN"]
url=st.secrets["URL"]

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

# Datumsauswahl über Date Picker
start_date = st.date_input("Startdatum", datetime.now() - timedelta(days=7))
end_date = st.date_input("Enddatum", datetime.now())

# Umwandlung der Datumsangaben in Unix-Zeitstempel
start_timestamp = int(datetime(start_date.year, start_date.month, start_date.day).timestamp()) * 1000000000
end_timestamp = int(datetime(end_date.year, end_date.month, end_date.day).timestamp()) * 1000000000

query_api = client.query_api()
query = 'from(bucket: "CO2-Messer")\
    |> range(start: {start_timestamp}, stop: {end_timestamp})\
    |> filter(fn: (r) => r._measurement == "CO2-Messer")\
    |> filter(fn: (r) => r._field == "temperature")'

result = query_api.query(org=org, query=query)

data = []
for table in result:
    for record in table.records:
        data.append((record.get_time(), record.get_field(), record.get_value()))

df = pd.DataFrame(data, columns=["time", "field", "value"])


# Plot mit Plotly
fig = px.line(df, x="time", y="temperatur", title='Temperatur', width=800, height=400)

# Zeige den Plot mit st.plotly_chart() an
st.plotly_chart(fig)
