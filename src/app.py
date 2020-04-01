"""App."""

import altair as alt  # type: ignore
import streamlit as st  # type: ignore

from penn_chime.presentation import (
    display_download_link,
    display_header,
    display_more_info,
    display_sidebar,
    hide_menu_style,
    write_definitions,
    write_footer,
)
# from penn_chime.settings import DEFAULTS
from penn_chime.models import SimSirModel
from penn_chime.charts import (
    build_admits_chart,
    build_census_chart,
    build_descriptions,
    build_sim_sir_w_date_chart,
    build_table,
)

from penn_chime.parameters import (
    Parameters,
    Disposition,
)

import pandas as pd
from datetime import date

from penn_chime.datagrabber import fromSheet
@st.cache
def getDataFromGoogleSheets():
    return fromSheet()
data = getDataFromGoogleSheets()
df = pd.DataFrame(data)

st.sidebar.markdown(
    """**Region Parameters**"""
)
selectedRegion = st.sidebar.selectbox("Select City", df.city)

st.title("Region: "+selectedRegion)
selectedRegionData = df.loc[df['city'] == selectedRegion]
selectedIndex = selectedRegionData.index[0]
# st.map(selectedRegionData)

selectedRegionDefaults = Parameters(
    population=selectedRegionData.population[selectedIndex],
    current_hospitalized=selectedRegionData.current_hospitalized[selectedIndex],
    doubling_time=selectedRegionData.doubling_time[selectedIndex],
    # known_infected=selectedRegionData.known_infected[selectedIndex],
    date_first_hospitalized=date(2020,3,7),
    infectious_days=14,
    market_share=0.15,
    relative_contact_rate=selectedRegionData.relative_contact_rate[selectedIndex],
    hospitalized=Disposition(selectedRegionData.hospitalized_rate[selectedIndex], selectedRegionData.hospitalized_length_of_stay[selectedIndex]),
    icu=Disposition(selectedRegionData.icu_rate[selectedIndex], selectedRegionData.icu_length_of_stay[selectedIndex]),
    ventilated=Disposition(selectedRegionData.ventilated_rate[selectedIndex], selectedRegionData.ventilated_length_of_stay[selectedIndex]),
)

# This is somewhat dangerous:
# Hide the main menu with "Rerun", "run on Save", "clear cache", and "record a screencast"
# This should not be hidden in prod, but removed
# In dev, this should be shown
# st.markdown(hide_menu_style, unsafe_allow_html=True)

p = display_sidebar(st, selectedRegionDefaults)
m = SimSirModel(p)

# display_header(st, m, p)

if st.checkbox("Show more info about this tool"):
    notes = "The total size of the susceptible population will be the entire catchment area for our hospitals."
    display_more_info(st=st, model=m, parameters=p, defaults=selectedRegionDefaults, notes=notes)

st.subheader("New Admissions")
st.markdown("Projected number of **daily** COVID-19 admissions. \n\n _NOTE: Now including estimates of prior admissions for comparison._")
admits_chart = build_admits_chart(alt=alt, admits_df=m.admits_df, max_y_axis=p.max_y_axis)
st.altair_chart(admits_chart, use_container_width=True)
st.markdown(build_descriptions(chart=admits_chart, labels=p.labels, suffix=" Admissions"))
display_download_link(
    st,
    filename=f"{p.current_date}_projected_admits.csv",
    df=m.admits_df,
)

if st.checkbox("Show Projected Admissions in tabular form"):
    admits_modulo = 1
    if not st.checkbox("Show Daily Counts"):
        admits_modulo = 7
    table_df = build_table(
        df=m.admits_df,
        labels=p.labels,
        modulo=admits_modulo)
    st.table(table_df)


st.subheader("Admitted Patients (Census)")
st.markdown("Projected **census** of COVID-19 patients, accounting for arrivals and discharges \n\n _NOTE: Now including estimates of prior census for comparison._")
census_chart = build_census_chart(alt=alt, census_df=m.census_df, max_y_axis=p.max_y_axis)
st.altair_chart(census_chart, use_container_width=True)
st.markdown(build_descriptions(chart=census_chart, labels=p.labels, suffix=" Census"))
display_download_link(
    st,
    filename=f"{p.current_date}_projected_census.csv",
    df=m.census_df,
)

if st.checkbox("Show Projected Census in tabular form"):
    census_modulo = 1
    if not st.checkbox("Show Daily Census Counts"):
        census_modulo = 7
    table_df = build_table(
        df=m.census_df,
        labels=p.labels,
        modulo=census_modulo)
    st.table(table_df)


st.subheader("Susceptible, Infected, and Recovered")
st.markdown("The number of susceptible, infected, and recovered individuals in the hospital catchment region at any given moment")
sim_sir_w_date_chart = build_sim_sir_w_date_chart(alt=alt, sim_sir_w_date_df=m.sim_sir_w_date_df)
st.altair_chart(sim_sir_w_date_chart, use_container_width=True)
display_download_link(
    st,
    filename=f"{p.current_date}_sim_sir_w_date.csv",
    df=m.sim_sir_w_date_df,
)

if st.checkbox("Show SIR Simulation in tabular form"):
    table_df = build_table(
        df=m.sim_sir_w_date_df,
        labels=p.labels)
    st.table(table_df)

write_definitions(st)
write_footer(st)
