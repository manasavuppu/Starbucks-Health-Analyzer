import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import pycountry
import pydeck as pdk
import plotly.express as px
import time
st.set_page_config(layout="wide")
# Cache data for faster Data Retrieval
@st.cache_data(show_spinner="Loading..")
def load_data(file):
    df_map = pd.read_csv(file)
    return df_map



df_map = load_data('Data/directory.csv')
df_nutri = pd.read_csv('Data/avg_nutri.csv')
col1, col2 = st.columns((0.3, 2))
with col1:
    image = 'Images/starbucks_logo.png'
    st.image(image, width=100)
with col2:
    st.write("# Sip Smart: Analyze Beverage Choices at Starbucks.")
    st.write("Explore the nutritional landscape of your Starbucks drinks—uncover insights and make informed choices for a healthier sip.")

tab1, tab2, tab3 = st.tabs(["Introduction", "Background", "About the App"])

with tab1:
    st.markdown(
        """
           As **Starbucks** expands its footprint across the globe, understanding the nutritional landscape of its offerings becomes increasingly crucial. Particularly in the **United States**, where Starbucks holds significant market dominance, this app allows you to explore and compare nutritional information, empowering you to make informed choices.
            """
    )





    df_map_cleaned = df_map.dropna(subset=['Latitude', 'Longitude'])

    df_country_bar = df_map_cleaned.groupby(
        'Country')['Country'].count().reset_index(name='Count')
    df_country_bar_sorted = df_country_bar.sort_values(by='Count', ascending=False)
    # Add Country name from pycountry based on the country code
    df_country_bar_sorted['CountryName'] = df_country_bar_sorted['Country'].apply(
        lambda code: pycountry.countries.get(alpha_2=code).name)
    df_country_bar_sorted['CountryName'] = df_country_bar_sorted['CountryName'].replace(
        'Korea, Republic of', 'South Korea')

    st.markdown(
        """**Select your Favourite countries to see the number of Starbucks stores**""")
    Country_list = sorted(df_country_bar_sorted['CountryName'].unique().tolist())
    Country_list_top5 = df_country_bar_sorted['CountryName'].head(5).tolist()  # Top 5 countries with high store count
    # Country select box creation
    options = st.multiselect(
        'Choose your countries from the drop down', Country_list, default=Country_list_top5
    )

    df_country_bar_sorted_filtered = df_country_bar_sorted[df_country_bar_sorted['CountryName'].isin(options)]
    max_count = df_country_bar_sorted_filtered['Count'].max()
    st.markdown(
        """Zoom in and explore the global concentration of Starbucks stores."""
    )
   # Bar chart for store density analysis
    chart = alt.Chart(df_country_bar_sorted_filtered).mark_bar(color='#006241').encode(
        x=alt.X('Count:Q', title="Number of Stores",
                scale=alt.Scale(domain=(0, max_count+900))),
        y=alt.Y('CountryName:N', title="Country", sort=alt.EncodingSortField(
            field='Count', op='sum', order='descending')),
        tooltip=[alt.Tooltip('CountryName:O', title="Country Name"), alt.Tooltip(
            'Count:Q', title="Number of Stores")]
    ).properties(
        title='Starbucks Store Count',
        width=500,
        height=550
    )
    text = chart.mark_text(
        align='center',
        baseline='middle',
        dx=12,

        color='green'  # Text color
    ).encode(
        text='Count:Q'
    )

    # Combine the bar chart and text layer
    chart_with_text = (chart + text).interactive()

    col1, col2 = st.columns((2, 2))
    with col1:
         #Map creation
   
        st.map(data=df_map_cleaned,latitude='Latitude',longitude='Longitude',color='#006241',use_container_width=True)
       

    with col2:
        if df_country_bar_sorted_filtered.empty:
            st.write("Choose your countries from the list.")
        else:
            st.altair_chart(chart_with_text, use_container_width=True)

with tab2:

    st.markdown("""
         **The percent Daily Value (% DV) tells how much a nutrient in a serving of the food or beverage contributes to a total daily 2,000-calorie diet.**""")
    st.markdown("""As per US Food and Drug Administration (FDA) **20% Daily Value or more of a nutrient per serving is considered high**""")

    st.markdown("""Let's identify the primary nutrient that significantly influences the %Daily Value in Starbucks beverages, on an average""")
    df_nutri['perc_values'] = df_nutri['Value'].round(2).astype(str)+'%'
    bars = alt.Chart(df_nutri).mark_bar().encode(
        x='Metric',
        y='Value',
        tooltip=[alt.Tooltip('Metric:O', title="Nutrient"),
                 alt.Tooltip('Value:Q', title="%Daily value")],
        color=alt.Color('Value', scale=alt.Scale(
            scheme='browns'), legend=None),
    ).properties(height=alt.Step(70), width=alt.Step(80))

    # Text labels
    text = alt.Chart(df_nutri).mark_text(align='center', baseline='middle', dy=-5, color='#006241').encode(
        x=alt.X('Metric:N', title='Nutrient'),
        y=alt.Y('Value:Q', title='%Daily Value'),
        text=alt.Text('perc_values:N'),

    )

    combined = (bars+text)
    st.altair_chart(combined, use_container_width=True)
    st.markdown("""Sugar and caffeine emerge as prominent contributors to the %Daily Value with **Sugar at 68.64%** and **Caffeine reaching 20%**.""")

with tab3:
    Nutri_score = "https://en.wikipedia.org/wiki/Nutri-Score"
    st.markdown("""This app compares different Starbucks beverages, assessing Sugar and Caffeine content, and considering Percentage Daily Value to provide insights on how healthy are they.""")
    st.markdown("""**Sugar Vs Caffeine**: Compare Sugar vs Caffeine (%DV) in this section, enabling users to choose beverage categories and protein ranges providing insights into where various beverages align. Categorizations include  **Balanced Brews** and **Over-indulgent** choices for a comprehensive understanding of drink profiles.""")
    st.markdown("""**Healthiness Score**: Dive deeper into individual beverages with the app's insightful feature **Healthiness Score**. This feature is inspired by [Nutri_score](%s) but focused primarily on Sugar and Caffeine content, allowing you to categorize healthiness effortlessly with an interactive **categorization meter**.""" % Nutri_score)
    st.markdown("""Healthiness Score Range: Balanced Option:<=33,
                                      Moderate Indulgences: 34-65
                                      Unbalanced Delights: >=66""")
    st.subheader("Data Sources:")
    BNV = '[Starbucks Nutritional content](https://stories.starbucks.com/uploads/2019/01/nutrition-1.pdf)'
    SSC = '[Starbucks Stores](https://data.world/data-hut/starbucks-location-dataset)'

    st.markdown(BNV, unsafe_allow_html=True)
    st.markdown(SSC, unsafe_allow_html=True)

    st.subheader('Image Sources:')
    st.markdown('https://creative.starbucks.com/logos/')
    st.subheader('References:')
    FDA = '[US Food and Drug Administration](https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels)'
    st.markdown(FDA, unsafe_allow_html=True)
    NS = '[Nutri-Score]( https://en.wikipedia.org/wiki/Nutri-Score)'
    st.markdown(NS, unsafe_allow_html=True)
