import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import pycountry
import pydeck as pdk
import datetime as dt
import seaborn as sns
from streamlit_dynamic_filters import DynamicFilters
st.set_page_config(layout="wide")

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
dv['Sugar_dv_percent']=dv['Sugar'].round(2).astype(str)+'%'
dv['Caffeine_dv_percent']=dv['Caffeine'].round(2).astype(str)+'%'
# bev_cat_options=dv['Beverage Category'].unique().tolist()
# sel_bev_cat=st.sidebar.multiselect("Choose a category to analyze",bev_cat_options)
# df_bev_cat_fil = dv[dv['Beverage Category'].isin(sel_bev_cat)]

#with st.sidebar.expander("Select a threshold for Sugar/Caffein for the visualization"):
selected_Sugar = st.sidebar.slider("Select a number for Sugar:", 1, 40, 40)
selected_Caffeine = st.sidebar.slider("Select a number for Caffeine:", 1, 40, 40)

select_protien = st.sidebar.slider("Select a range for Protien(g)", min_value=1, max_value=40, value=(1,20))

def determine_healthiness(row):
    if row['Sugar'] > selected_Sugar or row['Caffeine'] > selected_Caffeine :
        return 'Not Recommended'
    else:
        return 'Recommended'

# Apply the function to create the 'Healthiness' column
dv['Healthiness'] = dv.apply(determine_healthiness, axis=1)

# bev_cat_options=dv['Beverage Category'].unique().tolist()
# sel_bev_cat=st.sidebar.multiselect("Choose a category to analyze",bev_cat_options)
# df_bev_cat_fil = dv[dv['Beverage Category'].isin(sel_bev_cat)]
# milk_options=df_bev_cat_fil['Milk'].unique().tolist()
# sel_bev_cat_milk=st.sidebar.multiselect("Choose a type of Milk",milk_options)
# df_bev_cat_milk_fil=df_bev_cat_fil[df_bev_cat_fil['Milk']].isin(sel_bev_cat_milk)
# size_options=df_bev_cat_milk_fil['Size'].unique().tolist()
# sel_bev_cat_size=st.sidebar.multiselect("Choose a Size",size_options)
# df_bev_cat_size_fil=df_bev_cat_milk_fil[df_bev_cat_milk_fil['Size']].isin(sel_bev_cat_size)
# bev_options=df_bev_cat_size_fil['Beverege'].unique().tolist()
# sel_bev=st.multiselect("Choose a Drink",size_options)
# df_bev_fil=df_bev_cat_size_fil[df_bev_cat_size_fil['Beverege']].isin(sel_bev)
dynamic_filters = DynamicFilters(dv, filters=['Beverage Category', 'Milk', 'Size','Beverage'])
dynamic_filters.display_filters(location='columns',num_columns=2,gap='large')
df_filtered = dynamic_filters.filter_df()
df_no_duplicates = df_filtered.drop_duplicates(subset='Beverage')
df_with_protein_fil = df_no_duplicates[(df_no_duplicates['Protein (g)'] >= select_protien[0]) & (df_no_duplicates['Protein (g)'] <= select_protien[1])]

if len(df_no_duplicates)>=80:
    df_filtered_default=df_no_duplicates.groupby(['Beverage Category'])[['Sugar','Caffeine']].mean().reset_index()
    df_filtered_default['Healthiness'] = df_filtered_default.apply(lambda row: 'Not Recommended' if (row['Sugar'] > selected_Sugar or row['Caffeine'] > selected_Caffeine) else 'Recommended', axis=1)
    colors = ['#006241', '#b90000']
    df_filtered_default['Sugar_dv_percent']=df_filtered_default['Sugar'].round(2).astype(str)+'%'
    df_filtered_default['Caffeine_dv_percent']=df_filtered_default['Caffeine'].round(2).astype(str)+'%'
    chart=alt.Chart(df_filtered_default).mark_circle(size=90).encode(
                x=alt.X('Sugar').scale(domain=(5, 200)).title('Sugar(%DV)'),
                y=alt.X('Caffeine').title('Caffeine(%DV)').scale(domain=(-5, 50)),
                color=alt.Color('Healthiness:N', scale=alt.Scale(domain=['Recommended', 'Not Recommended'], range=colors)),
                tooltip=['Beverage Category','Sugar_dv_percent','Caffeine_dv_percent']
            ).properties(height=500,width=550).interactive()

    #Reference Line
    reference_line_x = alt.Chart(pd.DataFrame(([{'Caffeine': selected_Caffeine}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
        y='Caffeine:Q'
    )

    reference_line_y = alt.Chart(pd.DataFrame([{'Sugar': selected_Sugar}])).mark_rule(strokeDash=[3, 3], color='gray').encode(
        x='Sugar:Q'
    )
    text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=7
            ).encode(
            text='Beverage Category'
            )
    st.altair_chart(chart+text+reference_line_x+reference_line_y,use_container_width=True)
else:
    df_with_protein_fil['Sugar_dv_percent']=df_with_protein_fil['Sugar'].round(2).astype(str)+'%'
    df_with_protein_fil['Caffeine_dv_percent']=df_with_protein_fil['Caffeine'].round(2).astype(str)+'%'
    colors = ['#006241', '#b90000']
    chart=alt.Chart(df_with_protein_fil).mark_circle(size=90).encode(
                x=alt.X('Sugar').scale(domain=(5, 200)),
                y=alt.X('Caffeine').scale(domain=(-5, 50)),
                color=alt.Color('Healthiness', scale=alt.Scale(domain=['Recommended', 'Not Recommended'], range=colors)),
                tooltip=['Beverage','Beverage Category', 'Milk', 'Size']
            ).properties(height=500,width=550).interactive()

    #Reference Line
    reference_line_x = alt.Chart(pd.DataFrame(([{'Caffeine': selected_Caffeine}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
        y='Caffeine:Q'
    )

    reference_line_y = alt.Chart(pd.DataFrame(([{'Sugar': selected_Sugar}]))).mark_rule(strokeDash=[3, 3], color='gray').encode(
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
if st.button("Click Here for Recommendations"):
        if df_with_protein_fil_recommended.empty:
             st.success("We do not have any Recommendations catering to your Choices. However, Below are few recommendations for you!")
             
             recommended_df = dv.query("Healthiness == 'Recommended'").sample(n=5)
             styled_df = recommended_df[['Beverage Category','Beverage','Milk','Size','Calories','Protein (g)','Sugar','Caffeine']]

                # Display the styled table using st.dataframe
             st.dataframe(styled_df)
            
        else:
             
            st.success("Here are your recommendations!")
           

    # Apply the color function to the relevant columns
        
            styled_df = df_with_protein_fil_recommended[['Beverage Category','Beverage','Milk','Size','Calories','Protein (g)','Sugar','Caffeine']]

                # Display the styled table using st.dataframe
            st.dataframe(styled_df)
            

