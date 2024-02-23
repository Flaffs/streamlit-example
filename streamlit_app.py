import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import influxdb_client
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
points = result.get_points()

df = pd.DataFrame(points)

st.title('Temperaturverlauf')
st.write('Visualisierung des Temperaturverlaufs')

# Daten anzeigen
st.write(df)

# Zeitreihenvisualisierung
st.line_chart(df.set_index(pd.to_datetime(df['time']))['temperature'])
