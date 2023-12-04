import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import pycountry
import pydeck as pdk
st.set_page_config(layout="wide")
from urllib.request import urlopen
import json
import plotly.express as px

st.write("# Let's start with a warm cup of Coffee! ")
tab1, tab2 = st.tabs(["Introduction", "About this App"])

with tab1: 
    st.markdown(
        """
    As Starbucks has emerged as a global coffee giant, its largest market, the **United States**, has faced a growing concern - the challenge of obesity. As Starbucks continues to expand its reach worldwide, the nutritional implications of its offerings, 
    particularly in a country where it holds significant market dominance, become a critical point of examination.
    You can choose different countries to compare
    """
    )

    st.markdown(
        """
    Zoom out to find the concentration of stores across the world.
    """
    )
    df_map = pd.read_csv('directory.csv')
    df_map_cleaned = df_map.dropna(subset=['Latitude', 'Longitude'])

    df_country_bar=df_map_cleaned.groupby('Country')['Country'].count().reset_index(name='Count')
    df_country_bar_sorted = df_country_bar.sort_values(by='Count', ascending=False)
    df_country_bar_sorted['CountryName'] = df_country_bar_sorted['Country'].apply(lambda code: pycountry.countries.get(alpha_2=code).name)
    df_country_bar_sorted['CountryName'] = df_country_bar_sorted['CountryName'].replace('Korea, Republic of', 'South Korea')

    Country_list=df_country_bar_sorted['CountryName'].unique().tolist()
    Country_list_top5=df_country_bar_sorted['CountryName'].head(5).tolist()
    options = st.multiselect(
        'Select the Countries for comparison',Country_list,default=Country_list_top5
        )

    df_country_bar_sorted_filtered = df_country_bar_sorted[df_country_bar_sorted['CountryName'].isin(options)]
    max_count = df_country_bar_sorted_filtered['Count'].max()
    chart = alt.Chart(df_country_bar_sorted_filtered).mark_bar(color='#006241').encode(
        x=alt.X('Count:Q',title="Number of Stores",scale=alt.Scale(domain=(0, max_count+900))),
        y=alt.Y('CountryName:N',title="Country").sort('-x'),
        tooltip=[alt.Tooltip('CountryName:O', title="Country Name"), alt.Tooltip('Count:Q', title="Number of Stores")]
    ).properties(
        title='Countries with Most Starbucks Stores',
        width=250,
        height=400
    ).transform_window(
        rank='rank(Count)',
        sort=[alt.SortField('Count', order='descending')]
    ).interactive()

    text = chart.mark_text(
        align='center',
        baseline='middle',
        dx=13,  
        
        color='Black'  # Text color
    ).encode(
        text='Count:Q'  
    )

    # Combine the bar chart and text layer
    chart_with_text = (chart + text).interactive()

    col1, col2 = st.columns((2,2))
    with col1:
        st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=31.76,
            longitude=-97.4,
            zoom=3,
            pitch=0,
            
        ),
        layers=[
            
            pdk.Layer(
                'ScatterplotLayer',
                data=df_map_cleaned,
                get_position='[Longitude, Latitude]',
                #get_color='[200, 2,2]',
                get_radius=10000,
                get_fill_color=[0, 98, 65],
                get_line_color=[0, 0, 0],
                #tooltip="City: {City}"
            ),
        ]
    ))
        

    
    with col2:
            st.altair_chart(chart_with_text, use_container_width=True)

with tab2:
     
      st.markdown(
        """
    As Starbucks has emerged as a global coffee giant, its largest market, the **United States**, has faced a growing concern - the challenge of obesity. As Starbucks continues to expand its reach worldwide, the nutritional implications of its offerings, 
    particularly in a country where it holds significant market dominance, become a critical point of examination.
    You can choose different countries to compare
    """
    )

