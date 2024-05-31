import streamlit as st
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
import seaborn as sns
import plotly.express as px
import pydeck as pdk #pip install pydeck,  #pip install plotly-express
import pymongo
import isodate
import mysql.connector
import time
from PIL import Image 
import base64

#establishing connection to youtube API
api_key='AIzaSyCGIkPNjS0GPsmNDN-ZbL5XEipoJYimIF4'
youtube = build('youtube','v3', developerKey=api_key)
# global channel_id
# channel_id=None
#channel_id=None

#Establishing connection to MongoDB
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://aslam:1234@cluster0.kaopbqa.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
#client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
#try:
 #   client.admin.command('ping')
  #  print("Pinged your deployment. You successfully connected to MongoDB!")
#except Exception as e:
 #   print(e)

youtube = build('youtube','v3', developerKey=api_key)
#Make a request to youtube API
#passing particular channel's channelid to get channel info
def get_channel_stats(youtube,channel_id):
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id)
    
    response=request.execute()
    data = dict(channel_name=response['items'][0]['snippet']['title'],
                channel_Country=response['items'][0]['snippet'].get(('country'),0),
                channel_Desc=response['items'][0]['snippet']['localized']['description'],
                Subscribers=int(response['items'][0]['statistics']['subscriberCount']),
               Total_Video_Count=int(response['items'][0]['statistics']['videoCount']),
               Total_View_Count=int(response['items'][0]['statistics']['viewCount']),
               Playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
               channel_id=response['items'][0]['id']
               #Video_Id=,
               #Dislikes=,
               #Comments=
               )

    return data

def get_playlist_details(youtube,channel_id):
    l=[]
    Token=None
    while True:
        
        request = youtube.playlists().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=50,
                pageToken=Token
            )
        response = request.execute()
        
        for i in range(len(response['items'])):
            data = dict(Playlist_title=response['items'][i]['snippet']['title'],
                       Playlist_Desc=response['items'][i]['snippet'][ 'description'],
                       Playlist_Published_at =response['items'][i]['snippet']['publishedAt'],
                       Video_Count_in_Playlist=response['items'][i]['contentDetails']['itemCount'],
                       Playlist_Id=response['items'][i]['id'])
            l.append(data)
        Token=response.get('nextPageToken')
        if response.get('nextPageToken') is None:
            break
    return l

def get_Video_id(youtube,channel_id):
    l=[]
    l1=[]
    for i in channel_id:
        l1.append(i)
    for i in range(len(l1)):
        if(i==1):
            l1[1]='U'
    Playlistid=''.join(l1)
    Token=None
    while True:
        request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                maxResults=50,
                playlistId=Playlistid, #change this 
                pageToken=Token
            
            )
        response = request.execute()
        for i in range(len(response['items'])):
            
            
            l.append(response['items'][i]['contentDetails']['videoId'])
                       
        Token=response.get('nextPageToken')
        if not Token:
             break
                         
    return l

def get_video_details(youtube,All_Video_ids):
    
    l=[]
    n=0
    for i in All_Video_ids:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            maxResults=5,
            id=i
        )
        response=request.execute()
        
        
        for i in range(len(response['items'])):
            data = dict(Video_id=response['items'][i]['id'],
                        Channel_Title=response['items'][i]['snippet']['channelTitle'],
                        Video_Title=response['items'][i]['snippet']['localized']['title'],
                        Video_Desc=response['items'][i]['snippet']['localized']['description'],
                        Video_Published_at=response['items'][i]['snippet']['publishedAt'],
                        Video_Likes_Count=response['items'][i]['statistics'].get('likeCount'),
                        Video_Views_Count=response['items'][i]['statistics']['viewCount'],
                        Video_Duration=response['items'][i]['contentDetails']['duration'],
                        Video_Duration_Minutes=response['items'][i]['contentDetails']['duration'],
                        Video_Duration_Seconds=response['items'][i]['contentDetails']['duration'],
                        Video_Comments_Count=response['items'][i]['statistics'].get('commentCount',0))
            for j in data: #to convert Duration String to Int we are using isodate function
                if j=='Video_Duration':
                    Durationn=data['Video_Duration']
                    Duration_seconds = int(isodate.parse_duration(Durationn).total_seconds())
                    Duration_seconds=int(Duration_seconds)
                    Duration_minutes=Duration_seconds/60
                    Duration_seconds=((Duration_minutes)-int(Duration_minutes))*60
                    Duration_minutes=str(int(Duration_minutes))+" Minutes"+" "+str(round(Duration_seconds))+" Seconds"
                    #Duration_minutes
                    data['Video_Duration']=Duration_minutes
                elif j=='Video_Duration_Minutes':
                    Durationn=data['Video_Duration_Minutes']
                    Duration_seconds = int(isodate.parse_duration(Durationn).total_seconds())
                    #Duration_seconds=int(Duration_seconds)
                    Duration_minutes=Duration_seconds/60
                    Duration_minutes="{:.2f}".format(Duration_minutes)
                    #Duration_minutes=round(Duration_minutes)
                    #Duration_minutes
                    data['Video_Duration_Minutes']=Duration_minutes
                elif j=='Video_Duration_Seconds':
                    Durationn=data['Video_Duration_Seconds']
                    Duration_seconds = int(isodate.parse_duration(Durationn).total_seconds())
                    Duration_seconds=int(Duration_seconds)
                    
                    #Duration_minutes
                    data['Video_Duration_Seconds']=Duration_seconds

            l.append(data)           # Video_Count_in_Playlist=response['items'][0]['contentDetails']['itemCount'])
    return l

def get_comment_details(youtube,All_Video_ids):
    l=[]

    for i in All_Video_ids:
        try:
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=i,
                maxResults=5

            )
            response = request.execute()
            for j in range(len(response['items'])):


                    data = dict(Comment_id=response['items'][j]['id'],
                                    Comment_Video_id=i, #response['items'][j]['replies']['comments'][0]['snippet']['videoId'],
                                    Commenter_Name=response['items'][j]['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                    Commenter_Channel_Id=response['items'][j]['snippet']['topLevelComment']['snippet']['authorChannelId']['value'],
                                    Comment_Text=response['items'][j]['snippet']['topLevelComment']['snippet']['textOriginal'],
                                    Comment_Like_Count=response['items'][j]['snippet']['topLevelComment']['snippet']['likeCount'],
                                    Comment_Published_at=response['items'][j]['snippet']['topLevelComment']['snippet']['publishedAt'])
                    l.append(data)

        except:
            pass
               
    return l

def Entire_Details(channel_id):
    c=get_channel_stats(youtube,channel_id)
    p=get_playlist_details(youtube,channel_id)
    ids=get_Video_id(youtube,channel_id)
    v=get_video_details(youtube,ids)
    cm=get_comment_details(youtube,ids)
    
    data = {'Channel_Details' : c,
            'Playlist_Details':p,
            'All_Video_Details':v,
            'All_Videos_Comments_Details':cm}
    return data

#sidebar Homepage
def page_home():
    st.title("Welcome to My Streamlit Dashboard")#title
    
    file_ = open("C:/Users/hp/GUVI_Project/youtube_icon.gif", "rb") ##added this logic for playing the gif
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    unsafe_allow_html=True,
)

    # gif_1=Image.open("C:/Users/hp/GUVI_Project/youtube_icon.gif")
    # st.image(gif_1, caption='',width=480)
    st.markdown('## Purpose of this application🤔')
    st.markdown('The **Streamlit Application** allows the users to access and analyze data of multiple YouTube Channels.')
    st.markdown('This application allows users to enter Youtube Channel ID as input and retrieve channel data. This Channel can collect data for multiple YouTube channels and store them in database in just a click.')
    st.markdown('By selecting a channel, we could migrate the data from MongoDB Database to SQL, to retrieve the relevant youtube channel information like Videos Count, Likes Count, Comments Count etc.,')
    st.markdown('## Steps to get Channel ID from YouTube👨🏻‍🏫')
    st.markdown('1. Go to your favourite youtube channel, **right click** on the channel screen. Click on **View Page Source** option to proceed')
    image_1=Image.open("C:/Users/hp/GUVI_Project/Youtube_Step1.jpg")
    st.image(image_1, caption='BBC Youtube Channel Page',use_column_width=True)
    st.markdown('2. Press **Ctrl+F** and search for **https://www.youtube.com/channel** in source page. The **Channel Id** will appear after the link.')
    image_2=Image.open("C:/Users/hp/GUVI_Project/Youtube_Step2.png")
    st.image(image_2, caption='Source Page',use_column_width=True)
    st.markdown('3. Paste the Channel ID in the Next Page')
    image_3=Image.open("C:/Users/hp/GUVI_Project/Youtube_Step3.png")
    st.image(image_3, caption='Next Page',use_column_width=True)


def insert_MongoDB(channel_id):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/") #connecting to MongoDB
        mydb = myclient["youtube"] #creating Database
        mycol = mydb["Entire_Channel_Details"]  #creating collection
        mydict = Entire_Details(channel_id)
        x = mycol.insert_one(mydict) 

def page_MongoDB():
    #global channel_id
    st.title("Enter ChannelId & Migrate Channel data to MongoDB📲")
    #st.subheader('new')
    channel_name=st.text_input('Enter Channel Name')#getting a input from User
    channel_id=st.text_input('Enter Channelid for which you want to analyze data...') 
    if channel_id:
        st.session_state['channel_id']=channel_id
    #print("channel_idd=======",channel_idd)
    #channel_id=str(channel_idd)
    print("channel_id=======",channel_id)

    myclient = pymongo.MongoClient("mongodb://localhost:27017/") #connecting to MongoDB
    mydb1 = myclient.youtube #creating Database
    mycol = mydb1.Entire_Channel_Details 
    #print(mydict)
    #x = mycol.insert_one(mydict) 
    result = mycol.find_one({"Channel_Details.channel_id":channel_id},{})
    if result==None:
        if st.button('Migrate data to MongoDB🚀'):#button
            placeholder=st.empty()
            #st.write('Data is migrating to MongoDB🚀...')
            placeholder.write('Data is migrating to MongoDB🚀...')
            time.sleep(10)
            insert_MongoDB(channel_id)
            placeholder.empty()
            placeholder.write('Data is Successfully migrated to MongoDB🎯')
            time.sleep(10)
            placeholder.empty()
            #st.write('Data is Successfully migrated to MongoDB🎯')
    else:
        placeholder=st.empty()
        placeholder.write('This Channel data is already inserted to MongoDB Database...')
        time.sleep(7)
        placeholder.empty()
        placeholder.write('Please enter any other ChannelId...')
        time.sleep(10)
        placeholder.empty()
    
            
def insert_SQL(selection):
    #establishing connection to the server named localhost
        myclient = pymongo.MongoClient("mongodb://localhost:27017/") #connecting to MongoDB
        mydb1 = myclient.youtube #creating Database
        mycol = mydb1.Entire_Channel_Details  #creating collection
        #mydict = Entire_Details(channel_id)
        #x = mycol.insert_one(mydict) 
        #resultt=mycol.find_one({"Channel_Details.channel_id":"UCLx1PYSKcbOAymKX_UJ232g"})   
        
        myclient = pymongo.MongoClient("mongodb://localhost:27017/") #connecting to MongoDB
        mydb = myclient["youtube"] #creating Database
        mycol = mydb["Entire_Channel_Details"]  
        channel_id=st.session_state.get('channel_id','')
        #print("channel_id===",channel_id)
        resultt=mycol.find_one({"Channel_Details.channel_name":selection})   
        ch_l=[]
        ch_l.append(resultt["Channel_Details"])
        pl_l=resultt["Playlist_Details"]
        all_vi_l=resultt["All_Video_Details"]
        all_com_l=resultt["All_Videos_Comments_Details"]
        
        ch_df=pd.DataFrame(ch_l)
        pl_df=pd.DataFrame(pl_l)
        all_vi_df=pd.DataFrame(all_vi_l)
        all_com_df=pd.DataFrame(all_com_l)

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        #database='joins'
        )
        #print(mydb)
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("USE youtube2")
        #inserting data into Channel_details table after getting data from MONGODB and converted into DataFrame
        for index,row in ch_df.iterrows():
            #INSERT INTO Channel_details
            sql="INSERT INTO Channel_details (channel_name,channel_Country,channel_Desc,Subscribers,Total_Video_Count,Total_View_Count,Playlist_id,channel_id) VAlUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            #Dict_val=result["Channel_Details"].values()
            val=(row["channel_name"],row["channel_Country"],row["channel_Desc"],row["Subscribers"],row["Total_Video_Count"],row["Total_View_Count"],row["Playlist_id"],row["channel_id"])
            mycursor.execute(sql, val)

            mydb.commit()
        #inserting data into Playlist_Details table after getting data from MONGODB and converted into DataFrame
        for index,row in pl_df.iterrows():
            #INSERT INTO Playlist_Details
            sql="INSERT INTO Playlist_Details (Playlist_title,Playlist_Desc,Playlist_Published_at,Video_Count_in_Playlist,Playlist_Id) VAlUES(%s,%s,%s,%s,%s)"
            #Dict_val=result["Channel_Details"].values()
            val=(row["Playlist_title"],row["Playlist_Desc"],row["Playlist_Published_at"],row["Video_Count_in_Playlist"],row["Playlist_Id"])
            mycursor.execute(sql, val)

            mydb.commit()
        #inserting data into All_Videos_Details table after getting data from MONGODB and converted into DataFrame
        for index,row in all_vi_df.iterrows():
            #INSERT INTO All_Videos_Details
            sql="INSERT INTO All_Videos_Details (Video_id,Channel_Title,Video_Title,Video_Desc,Video_Published_at,Video_Likes_Count,Video_Views_Count,Video_Duration,Video_Duration_Minutes,Video_Duration_Seconds,Video_Comments_Count) VAlUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            #Dict_val=result["Channel_Details"].values()
            val=(row["Video_id"],row["Channel_Title"],row["Video_Title"],row["Video_Desc"],row["Video_Published_at"],row["Video_Likes_Count"],row["Video_Views_Count"],row["Video_Duration"],row["Video_Duration_Minutes"],row["Video_Duration_Seconds"],row["Video_Comments_Count"])
            mycursor.execute(sql, val)

            mydb.commit()
        #inserting data into All_Videos_Comments_Details table after getting data from MONGODB and converted into DataFrame
        for index,row in all_com_df.iterrows():
            #INSERT INTO All_Videos_Comments_Details
            sql="INSERT INTO All_Videos_Comments_Details (Comment_id,Comment_Video_id,Commenter_Name,Commenter_Channel_Id,Comment_Text,Comment_Like_Count,Comment_Published_at) VAlUES(%s,%s,%s,%s,%s,%s,%s)"
            #Dict_val=result["Channel_Details"].values()
            val=(row["Comment_id"],row["Comment_Video_id"],row["Commenter_Name"],row["Commenter_Channel_Id"],row["Comment_Text"],row["Comment_Like_Count"],row["Comment_Published_at"])
            mycursor.execute(sql, val)

            mydb.commit()


def page_SQL():
    st.title("Migrate Channel data to SQL📲")
    
    #print(i)
    myclient = pymongo.MongoClient("mongodb://localhost:27017/") #connecting to MongoDB
    mydb = myclient["youtube"] #creating Database
    mycol = mydb["Entire_Channel_Details"]  
    doc=mycol.find({},{"Channel_Details.channel_name":1,"_id":0})
    li=[]

    for i in doc:
        li.append(i["Channel_Details"]["channel_name"])
    selection = st.selectbox("Select a Channel to insert Channel data to SQL",li)
    # channel_id=st.session_state.get('channel_id','')
    # #print("channel_id===",channel_id)
    # resultt=mycol.find_one({"Channel_Details.channel_id":channel_id})   
    # sql_queries={
        
    # }
    if st.button('Migrate data to SQL🚀'):#button
        #establishing connection to the server named localhost
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        #database='joins'  
        )

        #print(mydb)
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("USE youtube2")
        mycursor.execute("select channel_name from Channel_details")
        rows=mycursor.fetchall()
        sqli=[]
        for i in rows:
            sqli.append(*i)
            #print(*i)
        
        #for j in range(len(sqli)):
        if selection not in sqli:

            placeholder=st.empty()
            placeholder.write('Data is migrating to SQL🚀...')
            #st.write('Data is migrating to SQL🚀...')
            time.sleep(10)
            insert_SQL(selection)
            placeholder.empty()
            #st.write('Data is successfully migrated to SQL🎯')
            placeholder.write('Data is successfully migrated to SQL🎯')
            time.sleep(10)
            placeholder.empty()

        else:
            placeholder=st.empty()
            placeholder.write('This Channel data is already inserted to SQL Database...')
            time.sleep(7)
            placeholder.empty()
            placeholder.write('Please Select any other Channel from the dropdown...')
            time.sleep(10)
            placeholder.empty()

def page_Analysis():
    st.title("Data Analysis📊📈")
    #establishing connection to the server named localhost
    
    st.markdown('### Lets Analyse youtube channel\'s data🧐') #markdown
    file_ = open("C:/Users/hp/GUVI_Project/data-analysis.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    unsafe_allow_html=True,
)
    # gif_1=Image.open("C:/Users/hp/GUVI_Project/data-analysis.gif")
    # st.image(gif_1, caption='',use_column_width=True)
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    #database='joins'
    )
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("USE youtube2")
    sql_queries={
        "Select a query to analyze data":" ",
        "1. What are the names of all the videos and their corresponding channels?":"Select Video_Title as 'Video Name',Channel_Title as 'Channel Name' from All_Videos_Details",
        "2.	Which channels have the most number of videos, and how many videos do they have?":"Select Channel_Name,Total_Video_Count as 'No. of Videos' from Channel_Details   ORDER BY Total_Video_Count DESC",
        "3.	What are the top 10 most viewed videos and their respective channels?":"Select Channel_Title as 'Channel_Name',Video_id as 'Most Viewed Videos' from All_Videos_Details ORDER BY Video_Views_Count DESC LIMIT 10",
        "4.	How many comments were made on each video, and what are their corresponding video names?":"Select Video_Title as 'Video Name',Video_Comments_Count as 'Comments Count' from All_Videos_Details ORDER BY Video_Comments_Count DESC",
        "5.	Which videos have the highest number of likes, and what are their corresponding channel names?":"Select Channel_Title as 'Channel Name',Video_Likes_Count as 'Likes Count' from All_Videos_Details order by Video_Likes_Count desc",
        "6.	What is the total number of likes and dislikes for each video, and what are their corresponding video names?":"Select Video_Likes_Count as 'Likes Count',Video_Title as 'Video Name' from All_Videos_Details",
        "7.	What is the total number of views for each channel, and what are their corresponding channel names?":"Select Total_View_Count as 'Toatal View Count',channel_name as 'Channel Name' from Channel_details",
        "8.	What are the names of all the channels that have published videos in the year 2022?":"Select DISTINCT Channel_Title as 'Channel Name' from All_Videos_Details where Video_Published_at BETWEEN'2022-01-01T00:00:00Z' AND '2023-01-01T00:00:00Z'",
        "9.	What is the average duration of all videos in each channel, and what are their corresponding channel names?":"Select AVG(Video_Duration_Seconds) as 'Avg Video Duration in Seconds',AVG(Video_Duration_Minutes) as ' Avg Video Duration in Minutes',Channel_Title as 'Channel Name' from All_Videos_Details GROUP BY Channel_Title",
        "10.Which videos have the highest number of comments, and what are their corresponding channel names?":"Select Video_Comments_Count as 'Comments Count',Channel_Title as 'Channel Name' from All_Videos_Details ORDER BY Video_Comments_Count DESC"
    }
    query=st.selectbox(" ",list(sql_queries.keys()))
    
    if st.button("Execute"):
        sql=sql_queries[query]
        df=pd.read_sql_query(sql,mydb)
        st.dataframe(df)
    
    mydb.close()

def main():
    st.sidebar.title("Page Navigation👇")
    selection = st.sidebar.selectbox("",["Home Page 🏠", "Enter ChannelId & Migrate Channel data to MongoDB🚀", "Migrate Channel data to SQL🚀","Data Analysis📊📈"])

    if selection == "Home Page 🏠":
        page_home()
    elif selection == "Enter ChannelId & Migrate Channel data to MongoDB🚀":
        page_MongoDB()
    elif selection == "Migrate Channel data to SQL🚀":
        page_SQL()
    elif selection == "Data Analysis📊📈":
        page_Analysis()

if __name__=="__main__":
    main()
    


