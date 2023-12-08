import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import pydeck as pdk
import datetime as dt
import seaborn as sns
import plotly.graph_objects as go
st.set_page_config(layout='wide')
image = 'Images/starbucks_logo.png'
st.image(image, width=80)

# Cache data for faster data Retreival


@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df


df = load_data('Data/starbucks_nutrition.csv')
dv = df.copy(deep=True)
# %Daily Value Computations
dv['Calories'] = dv['Calories'] / 2000 * 100
dv['Total Fat'] = dv['Total Fat (g)'] / 78 * 100
dv['Cholesterol'] = dv['Cholesterol (mg)'] / 300 * 100
dv['Carbohydrates'] = dv['Total Carbohydrates (g)'] / 275 * 100
dv['Sugar'] = dv['Sugar (g)'] / 50 * 100
dv['Protein'] = dv['Protein (g)'] / 50 * 100
dv['Caffeine'] = dv['Caffeine (mg)'] / 400 * 100
dv['Sugar(%DV)'] = dv['Sugar'].round(2).astype(str)+'%'
dv['Caffeine(%DV)'] = dv['Caffeine'].round(2).astype(str)+'%'


# Functions for Data Processing
def determine_healthiness(row):
    if row['Sugar'] > 20 or row['Caffeine'] > 20:
        return 'Over-indulgent'
    else:
        return 'Balanced Brews'


# Apply the function to create the 'Healthiness' column
dv['Healthiness'] = dv.apply(determine_healthiness, axis=1)


def calculate_nutri_score(row):
    # Nutritional factors and their weights
    factors = {
        "Sugar": {"weight": 0.55, "base": 0.0},
        "Caffeine": {"weight": 0.5, "base": 0.0},  # Custom weight for caffeine
    }

    # Calculate scores for each factor
    scores = {factor: max(0, factors[factor]["weight"] * (
        row[factor] - factors[factor]["base"])) for factor in factors}

    # Calculate the overall Nutri-Score
    nutri_score = sum(scores.values())

    return nutri_score


dv["Nutri Score"] = dv.apply(calculate_nutri_score, axis=1)

# Sidebar Selection Parameters
# Baverage Category selectbox

bev_cat_options = ['All Categories']
bev_cat_options += dv['Beverage Category'].unique().tolist()
sel_bev_cat = st.sidebar.selectbox(
    "Choose a category to analyze", bev_cat_options, placeholder='All Categories')
if sel_bev_cat == 'All Categories':
    sel_bev_cat = dv['Beverage Category'].unique().tolist()
    df_bev_cat_fil = dv[dv['Beverage Category'].isin(sel_bev_cat)]
else:
    df_bev_cat_fil = dv[dv['Beverage Category'].isin([sel_bev_cat])]

df_no_duplicates = df_bev_cat_fil.drop_duplicates(subset='Beverage')

# Protien Slider
select_protien = st.sidebar.slider(
    "Select a range for Protien(g)", min_value=0, max_value=40, value=(0, 20))
df_with_protein_fil = df_no_duplicates[(df_no_duplicates['Protein (g)'] >= select_protien[0]) & (
    df_no_duplicates['Protein (g)'] <= select_protien[1])]
df_with_protein_fil['Sugar(%DV)'] = df_with_protein_fil['Sugar'].round(2).astype(str)+'%'
df_with_protein_fil['Caffeine(%DV)'] = df_with_protein_fil['Caffeine'].round(2).astype(str)+'%'


# Tab Creation
tab1, tab2 = st.tabs(["Beverage Category", "Beverages"])
with tab1:
    st.markdown(
        """
           **Select a Beverage category and choose a Protien range from the sidebar to explore how beverages are distributed in the Sugar (%DV) vs Caffeine (%DV) space.** 
           \n Hover over the dots for details. Scroll down for Beverage Recommendations
             """
    )
# altair scatter plot
    colors = ['#006241', '#b90000']
    chart = alt.Chart(df_with_protein_fil).mark_circle(size=90).encode(
        x=alt.X('Sugar:Q', scale=alt.Scale(
            domain=(-5, 200)), title='Sugar(%Dv)'),
        y=alt.Y('Caffeine:Q', scale=alt.Scale(
            domain=(-5, 50)), title='Caffeine(%Dv)'),
        color=alt.Color('Healthiness', scale=alt.Scale(
            domain=['Balanced Brews', 'Over-indulgent'], range=colors)),
        tooltip=[
            alt.Tooltip('Beverage:N', title='Beverage Name'),
            alt.Tooltip('Sugar(%DV)', title='Sugar (%DV)'),
            alt.Tooltip('Caffeine(%DV)', title='Caffeine (%DV)')
        ]
    ).properties(height=500, width=800).interactive()

    # Reference Line x
    reference_line_x = alt.Chart(pd.DataFrame(([{'Caffeine': 20}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
        y='Caffeine:Q'
    )
    # Reference Line y
    reference_line_y = alt.Chart(pd.DataFrame(([{'Sugar': 20}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
        x='Sugar:Q'
    )

    combined = (chart+reference_line_x+reference_line_y).interactive()
    st.altair_chart(combined, use_container_width=True)
# Recommendations creation
    df_with_protein_fil_recommended = df_with_protein_fil[
        df_with_protein_fil['Healthiness'] == 'Balanced Brews']
    if df_with_protein_fil_recommended.empty:
        st.success(
            "We do not have any Recommendations catering to your Choices. However, Below are few healthier options you can choose from!")

        recommended_df = dv.query(
            "Healthiness == 'Balanced Brews'").sample(n=5)
        styled_df = recommended_df[['Beverage', 'Milk', 'Size']]
        styled_df['Beverage'] = styled_df['Beverage'].apply(
            lambda x: f'<span style="color:green">{x}</span>')

        st.write(styled_df.to_html(escape=False, index=False),
                 unsafe_allow_html=True, hide_index=True)

    else:

        st.success("Here are our recommendations from Balanced brews!")
        styled_df = df_with_protein_fil_recommended[[
            'Beverage', 'Milk', 'Size']].head(5)
        styled_df['Beverage'] = styled_df['Beverage'].apply(
            lambda x: f'<span style="color:green">{x}</span>')
        st.write(styled_df.to_html(escape=False, index=False),
                 unsafe_allow_html=True, hide_index=True)

    st.markdown(
        """
                    Would you like to know if your favourite Beverage is a healthy option? **Go to Beverages tab.**
             """
    )


with tab2:
    # Bevereges list
    bev_options = df_with_protein_fil['Beverage'].unique().tolist()
    sel_bev = st.selectbox(
        "Choose a Starbucks Beverage from the Selected Category ", bev_options)
    df_bev_fil = df_with_protein_fil[df_with_protein_fil['Beverage'].isin([
                                                                          sel_bev])]
    col1, col2, col3 = st.columns((4, 0.25, 2.5))
    with col1:
        # Nutriscore meter creation
        current_value = df_bev_fil['Nutri Score'].mean()

        plot_bgcolor = "#def"
        quadrant_colors = [plot_bgcolor, "#b22b27", "#e69138", "#006241"]
        quadrant_text = ["", "<b>Unbalanced Delights</b>",
                         "<b>Moderated Indulgences</b>", "<b>Balanced Option</b>"]
        n_quadrants = len(quadrant_colors) - 1

        current_value = df_bev_fil['Nutri Score'].mean()
        min_value = 0
        max_value = 50
        hand_length = np.sqrt(2) / 4
        hand_angle = np.pi * \
            (1 - (max(min_value, min(max_value, current_value)) -
             min_value) / (max_value - min_value))

        fig = go.Figure(
            data=[
                go.Pie(
                    values=[0.5] + (np.ones(n_quadrants) /
                                    2 / n_quadrants).tolist(),
                    rotation=90,
                    hole=0.5,
                    marker_colors=quadrant_colors,
                    text=quadrant_text,
                    textinfo="text",
                    hoverinfo="skip",
                ),
            ],
            layout=go.Layout(
                showlegend=False,
                margin=dict(b=0, t=10, l=10, r=10),
                width=500,
                height=500,
                paper_bgcolor=plot_bgcolor,
                annotations=[
                    go.layout.Annotation(
                        text=f"<b>Nutri Score:</b><br>{round(current_value,2)}",
                        x=0.5, xanchor="center", xref="paper",
                        y=0.25, yanchor="bottom", yref="paper",
                        showarrow=False,
                        font=dict(color="black", size=16)
                    )
                ],
                shapes=[
                    go.layout.Shape(
                        type="circle",
                        x0=0.48, x1=0.52,
                        y0=0.48, y1=0.52,
                        fillcolor="#333",
                        line_color="#333",
                    ),
                    go.layout.Shape(
                        type="line",
                        x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                        y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                        line=dict(color="#333", width=4)
                    )
                ]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
        """
                   **Nutri Score Range:** Balanced Option:<=17,
                                      Moderate Indulgences: 18-34
                                      Unbalanced Delights: >=35
             """)
    

    with col3:
        # Altair bar chart creation
        df_avg = df_bev_fil.groupby(['Beverage'])[
            ['Sugar', 'Caffeine']].mean().reset_index()
        df_long = pd.melt(df_avg[['Beverage', 'Sugar', 'Caffeine']], id_vars=[
                          'Beverage'], var_name='Nutrient', value_name='Score')

        df_long['Score'] = df_long['Score'].round(2)
        df_long['Score_perc'] = df_long['Score'].astype(str)+'%'

        bars1 = alt.Chart(df_long).mark_bar().encode(
            y=alt.Y('Score:Q', scale=alt.Scale(
                domain=(0, 100)), title='%Daily Value'),
            x='Nutrient:N',
            color=alt.Color('Score:Q', scale=alt.Scale(
                scheme='browns'), legend=None),
            tooltip=[
                alt.Tooltip('Score', title='%Daily Value:')
            ]
        ).properties(height=500, width=150)
        text = alt.Chart(df_long).mark_text(dy=-5, dx=3, color='black').encode(
            y=alt.Y('Score:Q'),
            x=alt.X('Nutrient:N'),
            text=alt.Text('Score_perc:N')

        )

        st.altair_chart(bars1+text, use_container_width=True)
