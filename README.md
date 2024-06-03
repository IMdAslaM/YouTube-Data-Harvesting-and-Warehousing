# YouTube-Data-Harvesting-and-Warehousing
Project Summary: Scrapping the channel's data from youtube, by connecting to youtube's API. Storing the data in MongoDB in the form of Collections. Taking data from MongoDB and converting it to Pandas dataframe to insert the data to SQL database in the form table. Now we can analyse the channel's data from SQL database.


Please find the below detailed explanation of this Project.

Step 1) Get an API key:
Search in web as "Yoiutube API Documentation"-->Guides-->Google Developers Console-->Choose Account

Step 2) Make a Request to API.
Request(API Key)-->Youtube-->Data Scrapping

Step 3) Now passing particular Channel's Channel ID to get Channel's info. by using get_channel_stats method

Step 4) Getting Playlist info, by writing a get_playlist_details method

Step 5) Now, getting each video id by passing universal playlistid of that channel by using get_video_id method.

Step 6) Again getting video's info. by passing each videoid which we get previously by using a get_video_details method.

Step 7) Now getting comment's details of each video by passing all video id by writing a get_comment_details method.

Step 8) Now store all the above all method's result to respective variables to access the data easily.

Step 9) Now writing a main method to store all of the above variables data in single dictionary.

Step 10) Now making a conection to MongoDB database to insert data.

Step 11) Every channel should be inserted only once, if we try to insert again it will throw a warning message.

Step 12) Now make a connection to SQL-->Create Database-->use database-->create required tables-->get the data from MongoDB collection and convert into pandas DataFrame-->Insert the Pandas DataFrame to SQl.

Step 13) Now we can analyze the data in SQL database in the form of DataFrame by selecting a queries in Dropdown.
