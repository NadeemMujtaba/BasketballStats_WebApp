import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
st.set_page_config(
        page_title="BasketballStats🏀📈🤾🏿",
)
st.title('NBA Player Stats Explorer')

st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2020))))

# Web scraping of NBA player stats
@st.cache_data
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)#convert NaN to 0
    playerstats = raw.drop(['Rk'], axis=1)# useless column
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]
# .isin return a df similar to org df but where selected team is replaced by 1 and others by 0 in org df
# .isin return a df similar to org df but where selected pos is replaced by 1 and others by 0 in org df
#& is bitwise so 1 & 1 give one meaning this way we can ensure we only get a particular set of data for 
# a particular selection of team and position
#therefore df_selected_team returns a unique df with unique dimensions
#now we have dimensions we move forward
st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64_bytes=base64.b64encode(csv.encode())
    b64_string = b64_bytes.decode()  # strings <-> bytes conversions
    href_string = f'<a href="data:file/csv;base64,{b64_string}" download="playerstats.csv">Download CSV file</a>'
    return href_string

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)
# in pandas dataframe
# out href string

# def get_table_download_link(df):
#     """Generates a link allowing the data in a given panda dataframe to be downloaded
#     in:  dataframe
#     out: href string
#     """
#     val = to_excel(df)
#     b64 = base64.b64encode(val)  # val looks like b'...'
#     return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

# df = ... # your dataframe
# st.markdown(get_table_download_link(df), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    
    df_selected_team.to_csv('output.csv',index=False)
    #only when working with df we need index to perform oprns else we dont
    df=pd.read_csv('output.csv')

    corr = df.corr()
    #.corr() finds correlation between columns
    maske= np.zeros_like(corr)
    #deloberately named as maske to understand

    # np.zeros_like return an array of zeroes with the same shape and type of given array
    
    maske[np.triu_indices_from(maske)] = True
    # here we set the cells we want to mask as true by accessing maske indexes by using maske[] method 

    #np.triu_indices_from return indices of  upper triangular elements(diagonal included)

    #mask[np.triu_indices_from(mask)] is set as true means all upper triangular ele set as 1 and lowertri ele is 0

    # if I dont mask pairwise correlations are made (a,b) and (b,a) unnecessarily

    
    with sns.axes_style("ticks"):
        #The Seaborn.axes_style() method is used to obtain the settings that govern the plots' overall look.
        f, ax = plt.subplots(figsize=(7, 5))
        # f is figure ax is axis object
        # subplots is to create more visualisations in given figure by creating more axes objects
        ax= sns.heatmap(corr,mask=maske, vmax=1)#what to plot in axes object
        #masking is applied here --^ now as uptringl ele set as 1 it is masked and only lower tringl shown
        
st.pyplot(f)        