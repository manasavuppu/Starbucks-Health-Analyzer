import streamlit as st
import numpy as np
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import pydeck as pdk
import datetime as dt
import seaborn as sns
from streamlit_dynamic_filters import DynamicFilters
import plotly.graph_objects as go

st.write("Application")
st.sidebar.success("Select a demo above.")
st.markdown(
    """

"""
)


@st.cache_data  # 
def load_data(file):
    df = pd.read_excel(file)
    return df
df = load_data('starbucks_data_cleaned.xlsx')
df.rename(columns={'Product Name':'Beverage','Category':'Beverage Category'},inplace=True)
df['Size']=df['Size'].apply(lambda x :'Short' if x=='1 - 236 mL serving' else x)
size_op=['Short','Tall','Grande','Venti®']
df=df[df['Size'].isin(size_op)]
df['Milk'] = df['Milk'].astype(str)
df['hot_cold'] = df['Beverage'].apply(lambda x: 'cold' if any(keyword.lower() in x.lower() for keyword in ['iced', 'cold', 'cool', 'frappuccino®', 'smoothie']) else 'hot')
df['hot_cold'] = df['Beverage'].apply(lambda x: 'cold' if any(keyword.lower() in x.lower() for keyword in ['iced', 'cold', 'cool', 'frappuccino®', 'smoothie']) else 'hot')
df['hot_cold'] = df.apply(lambda row: 'cold' if row['Beverage Category'] == 'Smoothies' else row['hot_cold'], axis=1)
condition = df['Beverage Category'].str.contains('Add On', case=False, na=False)
df.loc[condition, ['Beverage Category', 'hot_cold']] = 'Add-on'
df['Milk'] = df['Milk'].apply(lambda x: 'No Milk' if x=='nan' else x)
df['Milk'] = df['Milk'].apply( lambda x: 'Whole' if x=='0.02' else x)
df['Vegan'] = df['Milk'].apply(lambda x: 'Non Vegan' if any(keyword in x for keyword in ['0.02', 'Whole', 'Nonfat']) else 'Vegan')
df = df[df['Beverage Category'] != 'Frappuccino Light Blended Coffee']
dv = df.copy(deep=True)
dv['Calories'] = dv['Calories'] / 2000 * 100
dv['Total Fat'] = dv['Total Fat (g)'] / 78 * 100
dv['Cholesterol'] = dv['Cholesterol (mg)'] / 300 * 100
dv['Carbohydrates'] = dv['Total Carbohydrates (g)'] / 275 * 100
dv['Sugar'] = dv['Sugar (g)'] / 50 * 100 
dv['Protein'] = dv['Protein (g)'] / 50 * 100
dv['Caffeine'] = dv['Caffeine (mg)'] / 400 * 100
dv['Sugar(%DV)']=dv['Sugar'].round(2).astype(str)+'%'
dv['Caffeine(%DV)']=dv['Caffeine'].round(2).astype(str)+'%'
# bev_cat_options=dv['Beverage Category'].unique().tolist()
# sel_bev_cat=st.sidebar.multiselect("Choose a category to analyze",bev_cat_options)
# df_bev_cat_fil = dv[dv['Beverage Category'].isin(sel_bev_cat)]

#with st.sidebar.expander("Select a threshold for Sugar/Caffein for the visualization"):
#selected_Sugar = st.sidebar.slider("Select a number for Sugar:", 1, 40, 40)
#selected_Caffeine = st.sidebar.slider("Select a number for Caffeine:", 1, 40, 40)

select_protien = st.sidebar.slider("Select a range for Protien(g)", min_value=1, max_value=40, value=(1,20))
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'
def determine_healthiness(row):
    if row['Sugar'] > 30 or row['Caffeine'] > 30 :
        return 'Not Recommended'
    else:
        return 'Recommended'
# Apply the function to create the 'Healthiness' column
dv['Healthiness'] = dv.apply(determine_healthiness, axis=1)
def calculate_nutri_score(row):
            # Nutritional factors and their weights
            factors = {
                "Sugar": {"weight": 0.5, "base": 2.0},
                "Caffeine": {"weight": 0.5, "base": 15},  # Custom weight for caffeine
            }

            # Calculate scores for each factor
            scores = {factor: max(0, factors[factor]["weight"] * (row[factor] - factors[factor]["base"])) for factor in factors}

            # Calculate the overall Nutri-Score
            nutri_score = sum(scores.values())

            return nutri_score

        # Example Usage with a DataFrame
        # Assume dv is your DataFrame with columns like 'energy', 'sugars', 'saturated_fat', 'sodium', 'proteins', 'caffeine', etc.
dv["Nutri Score"] = dv.apply(calculate_nutri_score, axis=1)
bev_cat_options=['All Categories']
bev_cat_options +=dv['Beverage Category'].unique().tolist()
sel_bev_cat=st.sidebar.selectbox("Choose a category to analyze",bev_cat_options,placeholder='All Categories')
if sel_bev_cat=='All Categories':
    sel_bev_cat=dv['Beverage Category'].unique().tolist()
    df_bev_cat_fil = dv[dv['Beverage Category'].isin(sel_bev_cat)]
else:
    df_bev_cat_fil = dv[dv['Beverage Category'].isin([sel_bev_cat])]

# milk_options=df_bev_cat_fil['Milk'].unique().tolist()
# sel_bev_cat_milk=st.sidebar.multiselect("Choose a type of Milk",milk_options)
# df_bev_cat_milk_fil=df_bev_cat_fil[df_bev_cat_fil['Milk']].isin(sel_bev_cat_milk)
# size_options=df_bev_cat_milk_fil['Size'].unique().tolist()
# sel_bev_cat_size=st.sidebar.multiselect("Choose a Size",size_options)
# df_bev_cat_size_fil=df_bev_cat_milk_fil[df_bev_cat_milk_fil['Size']].isin(sel_bev_cat_size)
# bev_options=df_bev_cat_size_fil['Beverege'].unique().tolist()
# sel_bev=st.multiselect("Choose a Drink",size_options)
# df_bev_fil=df_bev_cat_size_fil[df_bev_cat_size_fil['Beverege']].isin(sel_bev)


df_no_duplicates = df_bev_cat_fil.drop_duplicates(subset='Beverage')
df_with_protein_fil = df_no_duplicates[(df_no_duplicates['Protein (g)'] >= select_protien[0]) & (df_no_duplicates['Protein (g)'] <= select_protien[1])]

# if len(df_no_duplicates)>=80:
#     df_filtered_default=df_no_duplicates.groupby(['Beverage Category'])[['Sugar','Caffeine']].mean().reset_index()
#     df_filtered_default['Healthiness'] = df_filtered_default.apply(lambda row: 'Not Recommended' if (row['Sugar'] > selected_Sugar or row['Caffeine'] > selected_Caffeine) else 'Recommended', axis=1)
#     colors = ['#006241', '#b90000']
#     df_filtered_default['Sugar_dv_percent']=df_filtered_default['Sugar'].round(2).astype(str)+'%'
#     df_filtered_default['Caffeine_dv_percent']=df_filtered_default['Caffeine'].round(2).astype(str)+'%'
#     chart=alt.Chart(df_filtered_default).mark_circle(size=90).encode(
#                 x=alt.X('Sugar',scale=alt.Scale(domain=(5, 200))),
#                 y=alt.X('Caffeine',scale=alt.Scale(domain=(-5, 50))),
#                 color=alt.Color('Healthiness:N', scale=alt.Scale(domain=['Recommended', 'Not Recommended'], range=colors)),
#                 tooltip=['Beverage Category','Sugar_dv_percent','Caffeine_dv_percent']
#             ).properties(height=500,width=550).interactive()

#     #Reference Line
#     reference_line_x = alt.Chart(pd.DataFrame(([{'Caffeine': selected_Caffeine}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
#         y='Caffeine:Q'
#     )

#     reference_line_y = alt.Chart(pd.DataFrame([{'Sugar': selected_Sugar}])).mark_rule(strokeDash=[3, 3], color='gray').encode(
#         x='Sugar:Q'
#     )
#     text = chart.mark_text(
#             align='left',
#             baseline='middle',
#             dx=7
#             ).encode(
#             text='Beverage Category'
#             )
#     st.altair_chart(chart+text+reference_line_x+reference_line_y,use_container_width=True)
# else:


df_with_protein_fil['Sugar(%DV)']=df_with_protein_fil['Sugar'].round(2).astype(str)+'%'
df_with_protein_fil['Caffeine(%DV)']=df_with_protein_fil['Caffeine'].round(2).astype(str)+'%'


        # Display the DataFrame with the added Nutri-Score column
st.dataframe(dv)
tab1, tab2 = st.tabs(["Beverage Category","Beverage"])
with tab1:
    colors = ['#006241', '#b90000']
    chart=alt.Chart(df_with_protein_fil).mark_circle(size=90).encode(
                    x=alt.X('Sugar:Q', scale=alt.Scale(domain=(5, 200)), title='Sugar(%Dv)'),
                    y=alt.Y('Caffeine:Q', scale=alt.Scale(domain=(-5, 50)), title='Caffeine(%Dv)'),
                    color=alt.Color('Healthiness', scale=alt.Scale(domain=['Recommended', 'Not Recommended'], range=colors)),
                    tooltip=[
            alt.Tooltip('Beverage:N', title='Beverage Name'),
            alt.Tooltip('Sugar(%DV)', title='Sugar (%DV)'),
            alt.Tooltip('Caffeine(%DV)', title='Caffeine (%DV)')
        ]
                ).properties(height=500,width=550).interactive()

        #Reference Line
    reference_line_x = alt.Chart(pd.DataFrame(([{'Caffeine': 30}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
            y='Caffeine:Q'
        )

    reference_line_y = alt.Chart(pd.DataFrame(([{'Sugar': 30}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
            x='Sugar:Q'
        )
        # text = chart.mark_text(
        #         align='left',
        #         baseline='middle',
        #         dx=7
        #         ).encode(
        #         text='Beverage'
        #         )
    combined=(chart+reference_line_x+reference_line_y).interactive()
    st.altair_chart(combined,use_container_width=True)





    df_with_protein_fil_recommended=df_with_protein_fil[df_with_protein_fil['Healthiness']=='Recommended']
    if st.button("Click Here for the List of Recommended beverages"):
                if df_with_protein_fil_recommended.empty :
                    st.success("We do not have any Recommendations catering to your Choices. However, Below are few healthier options you can choose from!")
                    
                    recommended_df = dv.query("Healthiness == 'Recommended'").sample(n=5)
                    styled_df = recommended_df[['Beverage Category','Beverage','Milk','Size','Calories','Protein (g)','Sugar(%DV)','Caffeine(%DV)']]

                        # Display the styled table using st.dataframe
                    st.dataframe(styled_df)
                    
                else:
                    
                    st.success("Here are your recommendations!")
                

            # Apply the color function to the relevant columns
                
                    styled_df = df_with_protein_fil_recommended[['Beverage Category','Beverage','Milk','Size','Calories','Protein (g)','Sugar(%DV)','Caffeine(%DV)']]

                        # Display the styled table using st.dataframe
                    st.dataframe(styled_df)


    # Grouped bar chart

    # Rec_List=['Recommended','Not Recommended']
    # opt_rec=st.radio("Select the category",Rec_List)
    # colors = ['#006241', '#b90000']
    # df_with_protein_fil_recommended_count=df_with_protein_fil.groupby(['Healthiness']).size().reset_index(name='Count')
    # bars= alt.Chart(df_with_protein_fil_recommended_count).mark_bar().encode(
    #             x='Count:Q',
    #             y='Healthiness',
    #             color=alt.Color('Healthiness', scale=alt.Scale(domain=['Recommended', 'Not Recommended'], range=colors))
    #         ).properties(height=200,width=400)

    # st.altair_chart(bars,use_container_width=True)

with tab2:
    bev_options=df_with_protein_fil['Beverage'].unique().tolist()
    sel_bev=st.selectbox("Choose a Drink",bev_options)
    df_bev_fil=df_with_protein_fil[df_with_protein_fil['Beverage'].isin([sel_bev])]
    st.dataframe(df_bev_fil)
    current_value = df_bev_fil['Nutri Score'].mean()
    


    plot_bgcolor = "#def"
    quadrant_colors = [plot_bgcolor, "#b22b27" , "#e69138","#6aa84f"] 
    quadrant_text = ["", "<b>UnHealthy</b>", "<b>Moderately Healthy</b>", "<b>healthy</b>"]
    n_quadrants = len(quadrant_colors) - 1

    current_value = df_bev_fil['Nutri Score'].mean()
    min_value = 0
    max_value = 50
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    fig = go.Figure(
        data=[
            go.Pie(
                values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
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
            margin=dict(b=0,t=10,l=10,r=10),
            width=450,
            height=450,
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>Nutri Score:</b><br>{current_value}",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
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
    st.plotly_chart(fig)

    
    
  


  