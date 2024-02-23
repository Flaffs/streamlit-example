import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import influxdb_client
import plotly.express as px
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

query_api = client.query_api()
query = 'from(bucket: "CO2-Messer")\
    |> range(start: -2h)\
    |> filter(fn: (r) => r._measurement == "CO2-Messer")\
    |> filter(fn: (r) => r._field == "temperature")'

result = query_api.query(org=org, query=query)

data = []
for table in result:
    for record in table.records:
        data.append((record.get_time(), record.get_field(), record.get_value()))

df = pd.DataFrame(data, columns=["time", "field", "value"])

# Altair Visualisierung erstellen
chart = alt.Chart(df).mark_line().encode(
    x='time:T',
    y='value:Q',
    color='field:N'
).properties(
    width=800,
    height=300
)

# Streamlit Anzeige
st.write(chart)

# Plot mit Plotly
fig = px.line(df, x="time", y="value", title='Temperature Over Time', width=800, height=400)

# Zeige den Plot mit st.plotly_chart() an
st.plotly_chart(fig)
