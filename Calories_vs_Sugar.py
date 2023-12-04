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

st.set_page_config(layout="wide")

st.write("Application")

st.sidebar.success("Select a demo above.")

st.markdown(
    """

"""
)

df = pd.read_excel('starbucks_data_cleaned.xlsx')
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
st.dataframe(dv)

# bev_cat_options=df['Beverage Category'].unique().tolist()
# sel_bev_cat=st.multiselect("Choose a category to analyze",bev_cat_options)
# df_bev_cat_fil = bev_melted[bev_melted['Beverage Category'].isin(sel_bev_cat)]
bev_cust_options=['Type of Milk','Size']
sel_cust_cat=st.multiselect("Choose a category to analyze",bev_cust_options)
bev_grp=dv.groupby(['Beverage Category'])[[ 'Sugar','Caffeine','Total Fat','Cholesterol','Carbohydrates','Protein','Sugar (g)','Caffeine (mg)','Total Fat (g)','Cholesterol (mg)','Total Carbohydrates (g)','Protein (g)']].mean().reset_index()
bev_melted = pd.melt(bev_grp, id_vars=['Beverage Category'], var_name='Metric', value_name='Value')
bev_bar=bev_melted.groupby(['Metric'])['Value'].mean().reset_index()
bev_bar['ind'] = bev_bar['Metric'].apply(lambda x: 'Actual Values' if '(' in str(x) else 'Daily Value(%)')
# Nutrient_option=['Sugar','Caffeine']
# Sel_Nutrient=st.sidebar.multiselect("Choose a Nutrient",Nutrient_option)
# filtered_bev_melted = bev_melted[bev_melted['Metric'].isin(Sel_Nutrient)]
tab1, tab2 = st.tabs(["Heat Map","Overview"])
with tab1:
            # dv_data=dv[dv['Milk']!='No Milk']
            # bev_cust_options=['Milk','Size']
            # Sel_cust_cat=st.radio("Choose a customization to analyze",bev_cust_options)
            # Nutrient_option=['Sugar','Caffeine']
            # Sel_Nutrient=st.sidebar.radio("Choose a Nutrient",Nutrient_option)
            # st.dataframe(dv_data)
            # if bev_cust_options=='Milk':
            #     bev_grp=dv_data.groupby(['Beverage Category','Milk','Size'])[['Sugar','Caffeine']].mean().reset_index()
            # else:
            #     bev_grp=dv_data.groupby(['Beverage Category','Milk','Size'])[['Sugar','Caffeine']].mean().reset_index()      
            # st.dataframe(bev_grp)
            #bev_melted = pd.melt(bev_grp, id_vars=['Beverage Category'], var_name='Milk', value_name='Sugar')
            #filtered_bev_melted = bev_melted[bev_melted['Metric'].isin(Sel_Nutrient)]
            st.dataframe(bev_grp)
            st.dataframe(bev_melted)
            st.dataframe(bev_bar)
        #     heatmap = alt.Chart(bev_grp).mark_rect().encode(
        #     x='Beverage Category:O',
        #     y=Sel_cust_cat+':O',
        #     color=alt.Color(Sel_Nutrient+':Q', scale=alt.Scale(scheme='browns',domain=[0, 100])),
        #     #alt.Color('Value:Q', scale=alt.Scale(scheme='lightgreyred', domain=[0, 26])),
        #     size='Value:Q'
        # ).properties(
        #     width=500,
        #     height=500
        # )

        #     text = alt.Chart(bev_grp).mark_text(baseline='middle').encode(
        #     x='Beverage Category:O',
        #     y='Metric:O',
        #     text='Value:Q'
        #     )

            # st.altair_chart(heatmap+text,use_container_width=True) 
        
        
            brown_colors = ['#3e1e04', '#6a3005', '#965015', '#c4923e', '#cbac85','#e9d6c0']
        # Grouped bar chart
            bars= alt.Chart(bev_bar[bev_bar['ind']=='Daily Value(%)']).mark_bar().encode(
            x='Metric',
            y='Value',
            color=alt.Color('Value', scale=alt.Scale(range=brown_colors)),
            #column='Beverage Category:N'
            ).properties(height=alt.Step(30),width=alt.Step(60)).interactive()

            st.altair_chart(bars)

            brown_colors = ['#3e1e04', '#6a3005', '#965015', '#c4923e', '#cbac85','#e9d6c0']
        # Grouped bar chart
            bars1= alt.Chart(dv).mark_bar().encode(
            x=alt.X("Sugar:Q").bin(),
            y='count():Q',
            color=alt.Color('count()', scale=alt.Scale(scheme='browns')),
            #column='Beverage Category:N'
            ).interactive()

            st.altair_chart(bars1)

            # Grouped bar chart
            bars1= alt.Chart(dv).mark_bar().encode(
            x=alt.X("Total Fat:Q").bin(),
            y='count():Q',
            color=alt.Color('count()', scale=alt.Scale(scheme='browns')),
            #column='Beverage Category:N'
            ).interactive()

            st.altair_chart(bars1)



        #     brown_colors = ['#3e1e04', '#6a3005', '#965015', '#c4923e', '#cbac85','#e9d6c0']
        # # Grouped bar chart
        #     bars= alt.Chart(bev_bar[bev_bar['ind']=='Daily Value(%)']).mark_bar().encode(
        #     x='Metric',
        #     y='Value',
        #     color=alt.Color('Value', scale=alt.Scale(range=brown_colors)),
        #     #column='Beverage Category:N'
        #     ).properties(height=alt.Step(30),width=alt.Step(60)).interactive()

        #     st.altair_chart(bars)
        

#     # #  # Text labels
#     # #     text = alt.Chart(filtered_bev_melted).mark_text(align='center', baseline='middle', dy=-5, color='white').encode(
#     # #     x=alt.X('Beverage Category:N', title='Beverage Category'),
#     # #     y=alt.Y('Value:Q', title='Mean Value'),
#     # #     text=alt.Text('Value:Q', format='.2f'),
#     # #     color=alt.Color('Metric:N', title='Nutrient')
#     # # )

# # Combine chart and text



# heatmap = alt.Chart(bev_melted).mark_rect(stroke='white', strokeWidth=2).encode(
#     x='Beverage Category:O',
#     y='Metric:O',
#     color=alt.Color('Value:Q', scale=alt.Scale(scheme='accent', domain=[0, 120])),
#     size='Value:Q'
# ).properties(
#     width=500,
#     height=500
# )


       
# with tab2: 
     
#     # var_category_analysis=['Beverage Category','Beverage']
#     # Sel_cat=st.sidebar.selectbox("Choose one major cat for analysis",var_category_analysis)

#     # var_cust=['hot_cold','Milk','Size']
#     # Sel_cust=st.sidebar.selectbox("Choose one for analysis",var_cust)




    # var_x_options=['Calories', 'Total Fat',
    #     'Cholesterol',  'Carbohydrates', 'Sugar', 'Protein','Caffeine']
    # var_y_options=['Calories', 'Total Fat',
    #     'Cholesterol',  'Carbohydrates', 'Sugar', 'Protein','Caffeine']
    # Sel_var_x=st.sidebar.selectbox("Select Variable x",var_x_options)
    # Sel_var_y=st.sidebar.selectbox("Select Variable y",var_y_options)
    # if Sel_var_x==Sel_var_y:
    #     "Please Choose different Nutrients to compare"
    # else: 
        
    #     df_bev_cat_fil = dv[dv['Beverage Category'].isin(sel_bev_cat)]
    #     st.dataframe(df_bev_cat_fil)
    #     df_bev_cat_group=df_bev_cat_fil.groupby([Sel_cat,Sel_cust])[[Sel_var_x,Sel_var_y]].mean().reset_index()
    #     st.dataframe(df_bev_cat_group)
    #     brown_colors = {
    #     'Soy': '#991f17',
    #     'Whole': '#5C4738',
    #     '0.02': '#644235',
    #     'Coconut': '#CDA890',
    #     'Nonfat': '#F3EBD6',
    #     'No Milk': '#2C2929'
    # }
        

    #     chart=alt.Chart(df_bev_cat_group).mark_circle(size=90).encode(
    #         x=Sel_var_x,
    #         y=Sel_var_y,
    #         color= alt.Color(Sel_cust+':N', scale=alt.Scale(range=list(brown_colors.values()))),
    #         tooltip=[Sel_cat+':N',Sel_cust+':N',Sel_var_x,Sel_var_y]
    #     ).interactive()
        
    #     text = chart.mark_text(
    #     align='left',
    #     baseline='middle',
    #     dx=7
    #     ).encode(
    #     text=Sel_cat
    #     )
    #     combined=(chart + text).interactive()
#     #     st.altair_chart(combined,use_container_width=True)
#    #stroke='white', strokeWidth=2
#     heatmap = alt.Chart(filtered_bev_melted).mark_rect().encode(
#         x='Beverage Category:O',
#         y='Metric:O',
#         color=alt.Color('Value:Q', scale=alt.Scale(scheme='browns',domain=[0, 100])),
#         #alt.Color('Value:Q', scale=alt.Scale(scheme='lightgreyred', domain=[0, 26])),
#         size='Value:Q'
#     ).properties(
#         width=500,
#         height=500
#     )

#     text = alt.Chart(filtered_bev_melted).mark_text(baseline='middle').encode(
#     x='Beverage Category:O',
#     y='Metric:O',
#     text='Value:Q'
# )

#     st.altair_chart(heatmap+text,use_container_width=True)

    # chart=alt.Chart(filtered_bev_melted).mark_circle(size=90).encode(
    #         x='Beverage Category',
    #         y='Value',
    #         color= alt.Color('Metric:N', scale=alt.Scale(scheme='browns')),
    #         #tooltip=[Sel_cat+':N',Sel_cust+':N',Sel_var_x,Sel_var_y]
    #     ).interactive()
        
    # text = chart.mark_text(
    #     align='left',
    #     baseline='middle',
    #     dx=7
    #     ).encode(
    #     text=Sel_cat
    #     )
    #combined=(chart + text).interactive()
   # st.altair_chart(chart,use_container_width=True)
