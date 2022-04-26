#!/usr/bin/env python
# coding: utf-8

# In[1]:

#Reference- https://github.com/claudian37/DS_Portfolio/blob/master/NYC_cab_dataset/01_EDA_NYC_Cab_geospatial_visualization.ipynb 

import pandas as pd
import numpy as np
import time 

import folium
from folium.plugins import HeatMap
from IPython.display import IFrame

import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image 
import glob


# In[2]:


df_train = pd.read_csv('NYC-Cab-Pickup_train.csv')
df_train.head()


# In[3]:


#Data preprocessing to get the hour and day of week for all entries in my training set

df = df_train[['pickup_datetime', 'pickup_longitude', 'pickup_latitude']].copy()
df['day_of_week'] = pd.to_datetime(df['pickup_datetime']).dt.dayofweek
df['hour_of_day'] = pd.to_datetime(df['pickup_datetime']).dt.hour
df.head()


# In[4]:


# Function to visualize map
def embed_map(map, filename):
    map.save(filename)
    return IFrame(filename, width='100%', height='500px')


# In[5]:


#Plot heatmap of lat/long coordinates by hour and day of week

dow_dict = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}


# In[6]:


'''
You need to mess around below to see where you can add the CO2 emissions data

https://eduardovirtuoso.github.io/Testes_Folium/

'''


# In[7]:


for i in range(df.day_of_week.min(), df.day_of_week.max()+1):
    for j in range(df.hour_of_day.min(), df.hour_of_day.max()+1):    
        
        # Filter to include only data for each day of week and hour of day
        df_geo = df.loc[(df.day_of_week==i) & (df.hour_of_day==j)][['pickup_latitude', 'pickup_longitude']].copy()

        # Instantiate map object 
        map_5 = folium.Map(location=[40.75, -73.96], tiles='openstreetmap', zoom_start=12)

        # Plot heatmap
        HeatMap(data=df_geo, radius=10).add_to(map_5)

        # Get day of week string from dow_dict
        d = dow_dict.get(i)
        
        # Add title to heatmap
        title_html = f'''<h3 align="center" style="font-size:20px">
                        <b>NYC Cab Pickups at {j}:00 on {d}: {len(df_geo)} rides</b></h3>
                     '''
        map_5.get_root().html.add_child(folium.Element(title_html))

        # Save map
        embed_map(map_5, f'./html_maps_pickup/{i}_{j}_heatmap.html')


# In[ ]:


#Automate Screenshots of heatmap files using selenium

for i in range(0, 7):
    for j in range(0, 24):
        # Set file path
        tmpurl= f'C:/Users/Nivashini/Desktop/Desktop/Ribbit Network/html_maps_pickup/{i}_{j}_heatmap.html'
        
        # Set browser to Chrome
        browser = webdriver.Chrome()
        
        # Open file in browser
        browser.get(tmpurl)
            
        # If hour is < 10, add 0 for sorting purposes and to keep chronological order
        if j < 10:
            browser.save_screenshot(f'./maps_png_pickup/{i}_0{j}_heatmap.png')
        else:
            browser.save_screenshot(f'./maps_png_pickup/{i}_{j}_heatmap.png')
        
        # Close browser
        browser.quit()


# In[ ]:


#Create Animated .gif file

def png_to_gif(path_to_images, save_file_path, duration=500):
    frames = []
    
    # Retrieve image files
    images = glob.glob(f'{path_to_images}')
    
    # Loop through image files to open, resize them and append them to frames
    for i in sorted(images): 
        im = Image.open(i)
        im = im.resize((550,389),Image.ANTIALIAS)
        frames.append(im.copy())
        
    # Save frames/ stitched images as .gif
    frames[0].save(f'{save_file_path}', format='GIF', append_images=frames[1:], save_all=True,
                   duration=duration, loop=0)


# In[ ]:


png_to_gif(path_to_images='./maps_png_pickup/*.png', 
           save_file_path='./plots/pickup_heatmap.gif',
          duration = 500)


# In[ ]:



import plotly.express as px
import plotly.graph_objects as go

scl = [0,"rgb(150,0,90)"],[0.125,"rgb(0, 0, 200)"],[0.25,"rgb(0, 25, 255)"],[0.375,"rgb(0, 152, 255)"],[0.5,"rgb(44, 255, 150)"],[0.625,"rgb(151, 255, 0)"],[0.75,"rgb(255, 234, 0)"],[0.875,"rgb(255, 111, 0)"],[1,"rgb(255, 0, 0)"]

fig = go.Figure(data=go.Scattergeo(
    lat = df['Latitude'],
    lon = df['Longitude'],
    text = df['CO2, PPM'].astype(str),
    marker = dict(
        color = df['CO2, PPM'],
        colorscale = scl,
        reversescale = True,
        opacity = 0.7,
        size = 2,
        colorbar = dict(
            titleside = "right",
            outlinecolor = "rgba(68, 68, 68, 0)",
            ticks = "outside",
            showticksuffix = "last",
            dtick = 0.1
        )
    )
))

fig.update_layout(
    geo = dict(
        scope = 'usa'), title='US CO2 emissions',
)

'''
fig.update_layout(
    geo = dict(
        scope = 'usa',
        showland = True,
        landcolor = "rgb(212, 212, 212)",
        subunitcolor = "rgb(255, 255, 255)",
        countrycolor = "rgb(255, 255, 255)",
        showlakes = True,
        lakecolor = "rgb(255, 255, 255)",
        showsubunits = True,
        showcountries = True,
        resolution = 50,
        projection = dict(
            type = 'conic conformal',
            rotation_lon = -100
        ),
        lonaxis = dict(
            showgrid = True,
            gridwidth = 0.5,
            range= [ -140.0, -55.0 ],
            dtick = 5
        ),
        lataxis = dict (
            showgrid = True,
            gridwidth = 0.5,
            range= [ 20.0, 60.0 ],
            dtick = 5
        )
    ),
    title='US CO2 emissions',
)
'''
fig.show()


# In[ ]:




