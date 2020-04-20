# Watcharin sirigate
# https://github.com/wsirigate

import re
import numpy as np
from scipy.stats import zscore
import pandas as pd
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Tahoma'
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
from datetime import datetime
import time
import plotly.graph_objs as go

def OpenFile(filename):
    chat = ReadChat(filename)
    chat = ChatRestr(chat)
    df = getDataFrame(chat)
    df = timeBining(data=df, bin_range=1)
    return df


def ReadChat(file_name):
    file = open(file_name, "r", encoding="utf8")
    chat = [i.strip() for i in file]
    chat = chat[3:]
    return chat

def ChatRestr(chat): # Chat Rescructure.
    
    chat_reformated = []
    
    for i in range(len(chat)):
        if re.search("^[M, T, W, T, F, S]", chat[i]):
            keep = chat[i]
        elif re.search("^[จ, อ, พ, พฤ, ศ, ส]", chat[i]):
            keep = chat[i]
        elif chat[i] == '':
            pass
        else:
            chat_reformated.append(keep + '\t' + chat[i])
            
    for i in range(len(chat_reformated)):
            chat_reformated[i] = chat_reformated[i].replace(', ', '\t', 1)
    
    new_format = [i.split('\t') for i in chat_reformated]
    
    return new_format

def yearTransform(data):
    """
    Convert year format A.D. to B.E.
    """
    
    # Check if input year = A.D. format
    if int(data[0][1][(len(data[0][1])-4):][1]) >= 5: # Check A.D.
        # Convert A.D. to B.E. format
        for i in range(len(data)):
            if len(data[i]) == 5 or len(data[i][0]) == 3:
                # data index count = 5 means normal situation.
                # index 0 of data = 3 means someone unsent a message or change album name.
                # with all of this condition still have a time value.
                data[i][1] = data[i][1].replace(data[i][1], data[i][1][:6]+str(int(data[i][1][6:])-543))
#             else:
#                 # incase of missing time.
#                 print(i)
#                 print(data[i], '\n')
#     else:
#         if len(data[i][0]) != 3:
#             # incase of missing time.
#                 print(data[i], '\n')
    return data

def getDataFrame(data):
    # Convert from list to data frame
    data = yearTransform(data)
    column = []
    
    for index in range(5):
        # Normal situation
        # unsent message and rename album won't include in data fraame.
        column.append([data[i][index] for i in range(len(data)) if len(data[i]) == 5])
        
    df = pd.DataFrame({'Day':column[0],
                       'Date':column[1],
                       'Time':column[2],
                       'User':column[3],
                       'Messages':column[4]})
    df['DateTime'] = pd.to_datetime(df.Date + ' ' + df.Time)
    return df

def timeBining(data, bin_range):
    bins = list(range(0, 25*60, 60*bin_range))
    labels = [str(i)+'-'+str(i+bin_range) for i in range(0, 24, bin_range)]
    data['minutes'] = data.DateTime.dt.hour * 60 + data.DateTime.dt.minute
    data['Group'] = pd.cut(data['minutes'], bins=bins, labels=labels)
    data.drop('minutes', axis=1, inplace = True)
    data = data.fillna('0-1')
    
    # add column message time(minute)
    data['MessageTime'] = (data.DateTime.dt.hour * 60) + (data.DateTime.dt.minute)
    return data

def chatResTime(data): # Chat respond time function
    chatRespond_df = pd.DataFrame()
    time = []
    user = []

    for i in range(len(data)):
        try:
            if data.loc[i, 'User'] != data.loc[i+1, 'User']:
                user.append(data.User[i+1])
#                 time.append(abs(data.MessageTime[i+1]-data.MessageTime[i]))
                res_time = data.MessageTime[i+1]-data.MessageTime[i]
                if res_time < 0:
                    # respond in next day.
                    wait_time = 1440 - data.MessageTime[i]
                    time.append(data.MessageTime[i+1] + wait_time)
                else:
                    # respond in same day.
                    time.append(data.MessageTime[i+1]-data.MessageTime[i])
    
        except:
            # Conversation ended.
            pass
        
    chatRespond_df['User'] = user
    chatRespond_df['Time'] = time
    
    return chatRespond_df

def getUser(data):
    return list(data.User.unique())

def rmOutlier(data, col_name):
    # Remove outlier
    z_scores = zscore(data[col_name])
    z_scores = np.abs(z_scores)
    filtered = (z_scores < 3)
    data = data[filtered]
    return data

def availableDay(data):
    return set([i[6:]+'/'+i[3:5] for i in data.Date.unique()])

def dateFilter(data, month, year):
    # Filter month and year for visualization.
    data = data[np.logical_and(data.DateTime.dt.month == month, data.DateTime.dt.year == year)]
    data = data.reset_index(drop=True)
    return data

def plotHeatmap(data):
    group = data.groupby(['Day', 'Group'])
    group = group.size().unstack()
    group = group.reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    group = group.fillna(0)
    group.columns.name = 'Time'
    
    plt.figure(figsize=(15,5))
    plt.title(data.Date[0]+' - '+list(data.Date)[-1:][0])
    
    ax = sns.heatmap(group, cmap="YlGnBu", annot=True, fmt='.0f')
    plt.show()

def basicInformation(data):
#     plt.rcParams['font.sans-serif'] = ['Source Han Sans TW', 'sans-serif']
    print('-'*108+'\n', ' '*28, f'Plot result from data ({data.Date[0]} - {list(data.Date)[-1:][0]})', '\n'+'-'*108)
    plt.figure(figsize=(14,3))
    
    plt.subplot(131)
    data.User.value_counts().plot(kind='pie', autopct='%1.0f%%')
    plt.title('Number of conversation per user.')
    
    plt.subplot(132)
    data.Day.value_counts().reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']).plot.bar(rot=0)
    plt.title('Number of conversation per days.')
    
    plt.subplot(133)
    data.DateTime.dt.year.value_counts().plot.bar(rot=0)
    plt.title('Number of conversation per years.')
    
    plotHeatmap(data)
    
    plt.tight_layout()
    plt.show()

def respondHist(data, bin_range):
    
    data = chatResTime(data)
    data = rmOutlier(data, 'Time')
    
    user = getUser(data)
    for i in range(len(user)):
        plt.figure(figsize=(10, 4))
        plt.title(user[i], fontsize=15)
        query = data.Time[data.User == user[i]]
        plt.hist(query, bins=range(0, bin_range))
        plt.show()
        
        print(f'User : {user[i]}')
        print('Average respond time :', data[data.User == user[i]].mean().values[0].round(2), 'minute')
        print('Min respond time =', data.Time[data.User == user[i]].min(), 'minute')
#         print('Max respond time =', data.Time[data.User == user[i]].max(), 'minute')

