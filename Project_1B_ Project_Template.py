#!/usr/bin/env python
# coding: utf-8

# # Part I. ETL Pipeline for Pre-Processing the Files

# ## PLEASE RUN THE FOLLOWING CODE FOR PRE-PROCESSING THE FILES

# #### Import Python packages 

# In[7]:


# Import Python packages 
import pandas as pd
import cassandra
import re
import os
import glob
import numpy as np
import json
import csv


# #### Creating list of filepaths to process original event csv data files

# In[8]:


# checking your current working directory
print(os.getcwd())

# Get your current folder and subfolder event data
filepath = os.getcwd() + '/event_data'

# Create a for loop to create a list of files and collect each filepath
for root, dirs, files in os.walk(filepath):
    
# join the file path and roots with the subdirectories using glob
    file_path_list = glob.glob(os.path.join(root,'*'))
    #print(file_path_list)


# #### Processing the files to create the data file csv that will be used for Apache Casssandra tables

# In[9]:


# initiating an empty list of rows that will be generated from each file
full_data_rows_list = [] 
    
# for every filepath in the file path list 
for f in file_path_list:

# reading csv file 
    with open(f, 'r', encoding = 'utf8', newline='') as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
        next(csvreader)
        
 # extracting each data row one by one and append it        
        for line in csvreader:
            #print(line)
            full_data_rows_list.append(line) 
            
# uncomment the code below if you would like to get total number of rows 
#print(len(full_data_rows_list))
#uncomment the code below if you would like to check to see what the list of event data rows will look like
#print(full_data_rows_list)

# creating a smaller event data csv file called event_datafile_full csv that will be used to insert data into the \
# Apache Cassandra tables
csv.register_dialect('myDialect', quoting=csv.QUOTE_ALL, skipinitialspace=True)

with open('event_datafile_new.csv', 'w', encoding = 'utf8', newline='') as f:
    writer = csv.writer(f, dialect='myDialect')
    writer.writerow(['artist','firstName','gender','itemInSession','lastName','length',                'level','location','sessionId','song','userId'])
    for row in full_data_rows_list:
        if (row[0] == ''):
            continue
        writer.writerow((row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[12], row[13], row[16]))


# In[10]:


# check the number of rows in your csv file
with open('event_datafile_new.csv', 'r', encoding = 'utf8') as f:
    print(sum(1 for line in f))


# # Part II. Complete the Apache Cassandra coding portion of your project. 
# 
# ## Now you are ready to work with the CSV file titled <font color=red>event_datafile_new.csv</font>, located within the Workspace directory.  The event_datafile_new.csv contains the following columns: 
# - artist 
# - firstName of user
# - gender of user
# - item number in session
# - last name of user
# - length of the song
# - level (paid or free song)
# - location of the user
# - sessionId
# - song title
# - userId
# 
# The image below is a screenshot of what the denormalized data should appear like in the <font color=red>**event_datafile_new.csv**</font> after the code above is run:<br>
# 
# <img src="images/image_event_datafile_new.jpg">

# ## Begin writing your Apache Cassandra code in the cells below

# #### Creating a Cluster

# In[2]:


# This should make a connection to a Cassandra instance your local machine 
# (127.0.0.1)

from cassandra.cluster import Cluster
cluster = Cluster()

# To establish connection and begin executing queries, need a session
session = cluster.connect()


# #### Create Keyspace

# In[3]:


try:
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS udacity 
    WITH REPLICATION = 
    { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }"""
)

except Exception as e:
    print(e)


# #### Set Keyspace

# In[4]:


try:
    session.set_keyspace('udacity')
except Exception as e:
    print(e)


# ### Now we need to create tables to run the following queries. Remember, with Apache Cassandra you model the database tables on the queries you want to run.

# ## Create queries to ask the following three questions of the data
# 
# ### 1. Give me the artist, song title and song's length in the music app history that was heard during  sessionId = 338, and itemInSession  = 4
# 
# 
# ### 2. Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name) for userid = 10, sessionid = 182
#     
# 
# ### 3. Give me every user name (first and last) in my music app history who listened to the song 'All Hands Against His Own'
# 
# 
# 

# In[187]:


## TO-DO: Query 1:  Give me the artist, song title and song's length in the music app history that was heard during \
## sessionId = 338, and itemInSession = 4

query1="select * from music_app_history_by_session where session_id='338' and item_in_session = '4'"
                    


# In[183]:


# We have provided part of the code to set up the CSV file. Please complete the Apache Cassandra code below#
file = 'event_datafile_new.csv'

try:
    session.execute("drop table music_app_history_by_session")
except Exception as e:
    print(e)
try:
    session.execute("drop table music_app_history_by_user")
except Exception as e:
    print(e)
try:
    session.execute("drop table music_app_history_by_song")
except Exception as e:
    print(e)
    
query1 = "CREATE TABLE IF NOT EXISTS music_app_history_by_session"
query1 = query1 + "(artist text,                first_name text,                gender text,                item_in_session text,                last_name text,                length text,                level text,                location text,                session_id text,                song text,                user_id text,                PRIMARY KEY((session_id,item_in_session),user_id))"
try:
    session.execute(query1)
except Exception as e:
    print(e)
    
query2 = "CREATE TABLE IF NOT EXISTS music_app_history_by_user"
query2 = query2 + "(artist text,                first_name text,                gender text,                item_in_session text,                last_name text,                length text,                level text,                location text,                session_id text,                song text,                user_id text,                PRIMARY KEY((user_id,session_id),item_in_session))"
try:
    session.execute(query2)
except Exception as e:
    print(e) 

query3 = "CREATE TABLE IF NOT EXISTS music_app_history_by_song"
query3 = query3 + "(artist text,                first_name text,                gender text,                item_in_session text,                last_name text,                length text,                level text,                location text,                session_id text,                song text,                user_id text,                PRIMARY KEY((song),user_id))"
try:
    session.execute(query3)
except Exception as e:
    print(e)     

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
## TO-DO: Assign the INSERT statements into the `query` variable
        query1="insert into music_app_history_by_session (artist, first_name, gender,item_in_session, last_name, length, level, location, session_id, song, user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        query2="insert into music_app_history_by_user (artist, first_name, gender,item_in_session, last_name, length, level, location, session_id, song, user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        query3="insert into music_app_history_by_song (artist, first_name, gender,item_in_session, last_name, length, level, location, session_id, song, user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        ## TO-DO: Assign which column element should be assigned for each column in the INSERT statement.
        ## For e.g., to INSERT artist_name and user first_name, you would change the code below to `line[0], line[1]`
        session.execute(query1, (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]))        
        session.execute(query2, (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]))
        session.execute(query3, (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]))        


# #### Do a SELECT to verify that the data have been inserted into each table

# In[188]:


## TO-DO: Add in the SELECT statement to verify the data was entered into the table
try:
    rows=session.execute(query1)
except Exception as e:
    print(e)
    
for row in rows:
    print(row.artist,row.song,row.length)


# ### COPY AND REPEAT THE ABOVE THREE CELLS FOR EACH OF THE THREE QUESTIONS

# In[185]:


## TO-DO: Query 2: Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name)\
## for userid = 10, sessionid = 182
query2="select * from music_app_history_by_user where session_id='182' and user_id='10'"
try:
    rows=session.execute(query2)
except Exception as e:
    print(e)
    
for row in rows:
    print(row.artist, row.song, row.first_name,row.last_name)

                    


# In[186]:


## TO-DO: Query 3: Give me every user name (first and last) in my music app history who listened to the song 'All Hands Against His Own'
query3="select * from music_app_history_by_song where song='All Hands Against His Own'"
try:
    rows=session.execute(query3)
except Exception as e:
    print(e)
    
for row in rows:
    print(row.first_name,row.last_name)

                    


# In[ ]:





# In[ ]:





# ### Drop the tables before closing out the sessions

# In[4]:


## TO-DO: Drop the table before closing out the sessions
try:
    session.execute("drop table music_app_history_by_session")
except Exception as e:
    print(e)
try:
    session.execute("drop table music_app_history_by_user")
except Exception as e:
    print(e)
try:
    session.execute("drop table music_app_history_by_song")
except Exception as e:
    print(e)


# In[ ]:





# ### Close the session and cluster connection¶

# In[ ]:


session.shutdown()
cluster.shutdown()


# In[ ]:





# In[ ]:




