import streamlit as st
from streamlit_echarts import st_echarts


options = {
    "xAxis": { 
            "type": "value",
            "data": #Jahre 
    },
    "yAxis": {"type": "value"},
    "series": [{"data": #Feature Verlauf für Ernte}]


}

st_echarts(options=options, height = "400px")