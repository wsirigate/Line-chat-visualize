import re
import pandas as pd
from datetime import datetime

def read_chat(filename):
    """
    This function will read chat data.
    """
    files = open(filename+'.txt', "r", encoding="utf8")
    chat = [i.strip() for i in files]
    return chat[3:]

def reformat_pc(chat):
    """
    This function will reformat chat history.txt that exported from PC format to data frame format.
    """
    new_format = []
    keeper = ''
    for i in chat:
        if re.search("^[2][0][1-9][1-9].[0-1][1-9].[0-3][0-9]", i):
            keeper = i.replace(' ', '\t', 1)
        if re.search("^[0-2][0-9]:[0-5][0-9]", i):
            i = i.replace(' ', '\t', 2)
            new_format.append(keeper + '\t' + i)
    new_format = [i.split('\t') for i in new_format]
    # Create data frame.
    date = [new_format[i][0] for i in range(len(new_format)) if len(new_format[i]) == 5]
    day = [new_format[i][1] for i in range(len(new_format)) if len(new_format[i]) == 5]
    time = [new_format[i][2] for i in range(len(new_format)) if len(new_format[i]) == 5]
    user = [new_format[i][3] for i in range(len(new_format)) if len(new_format[i]) == 5]
    messages =[new_format[i][4] for i in range(len(new_format)) if len(new_format[i]) == 5]
    df = pd.DataFrame({'day':day, 'time':time, 'date':date, 'user':user, 'messages':messages})
    # Create date time column
    date_time = [datetime.strptime(df['date'][i] + ' ' + df['time'][i], '%Y.%m.%d %H:%M') for i in range(len(df))]
    df['date_time'] = date_time
    df.drop('time', axis=1, inplace = True)
    # Reformat day and date.
    for k in range(len(df)):
        df['day'].iloc[k] = df['date_time'].iloc[k].strftime('%a')
        df['date'].iloc[k] = df['date_time'][k].strftime('%d/%m/%Y')
    df = time_binning(df)
    return df

def reformat(chat):
    """
    This function will reformat text format to data frame format.
    """
    # reformatted data
    keep = ''
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
    # Check day language
    if re.search('[a-z, A-Z]', chat[0][0]): # Eng
        for i in range(len(chat_reformated)):
            chat_reformated[i] = chat_reformated[i].replace(', ', '\t', 1)
    else: # Thai
        for i in range(len(chat_reformated)):
            chat_reformated[i] = chat_reformated[i].replace(' ', '\t', 1)

    # Convert to new format
    new_format = [i.split('\t') for i in chat_reformated]

    # Convert A.D. to B.E.
    if int(new_format[0][1][(len(new_format[0][1])-4):][1]) > 0:
        new_format = ad_to_be(new_format)

    # Create data frame.
    day = [new_format[i][0] for i in range(len(new_format)) if len(new_format[i]) == 5]
    date = [new_format[i][1] for i in range(len(new_format)) if len(new_format[i]) == 5]
    time = [new_format[i][2] for i in range(len(new_format)) if len(new_format[i]) == 5]
    user = [new_format[i][3] for i in range(len(new_format)) if len(new_format[i]) == 5]
    messages =[new_format[i][4] for i in range(len(new_format)) if len(new_format[i]) == 5]
    df = pd.DataFrame({'day':day, 'time':time, 'date':date, 'user':user, 'messages':messages})

    # Add date_time as column.
    if 0 < int(df.date[0].split('/')[1]) <= 12:
        date_time = [datetime.strptime(df['date'][i] + ' ' + df['time'][i], '%d/%m/%Y %H:%M') for i in range(len(df))]
        df['date_time'] = date_time
    else:
        date_time = [datetime.strptime(df['date'][i] + ' ' + df['time'][i], '%m/%d/%Y %H:%M') for i in range(len(df))]
        df['date_time'] = date_time
    df.drop('time', axis=1, inplace = True)

    # Reformat day and date.
    for k in range(len(df)):
        df['day'].iloc[k] = df['date_time'].iloc[k].strftime('%a')
        df['date'].iloc[k] = df['date_time'][k].strftime('%d/%m/%Y')

    # add column in data frame
    month_year = [df.date_time[i].strftime("%m/%Y") for i in range(len(df))]
    dd = [df.date_time[i].strftime("%d") for i in range(len(df))]
    df['month_year'] = month_year
    df['dd'] = dd

    df = time_binning(df)
    return df

def time_binning(df):
    # Time binning
    bins = list(range(0, 25*60, 60*3))
    labels = ['0-3', '3-6', '6-9', '9-12','12-15', '15-18', '18-21', '21-24']
    # add column minutes to data frame
    df['minutes'] = df.date_time.dt.hour * 60 + df.date_time.dt.minute
    # add column groupto data frame
    df['group'] = pd.cut(df['minutes'], bins=bins, labels=labels)
    # df.drop('minutes', axis=1, inplace = True)
    return df

def ad_to_be(new_format):
    """
    Convert year A.D. to B.E.
    """
    for i in range(len(new_format)):
        new_format[i][1] = new_format[i][1].replace(new_format[i][1], new_format[i][1][:6]+str(int(new_format[i][1][6:])-543))
    return new_format

def find_my(df):
    """
    Function find all month and year in chat.
    """
    month_year = [df['date_time'][i].strftime("%m/%Y") for i in range(len(df['date_time']))]
    month_year = list(set(month_year))
    return month_year


def filter_my(df, month_year):
    """
    Function filter month year.
    """
    df_filter = df[df['month_year'] == month_year]
    df_filter = df_filter.reset_index()
    df_filter.drop('index', inplace=True, axis=1)
    return df_filter

def urt(df): #user responestime
    """
    Function find user respondstime
    """
    days = list(df.dd.value_counts().index)
    days.sort()
    
    conc_user = []
    conc_responsetime = []
    conc_day = []

    for i in days:
        df_dayf = df[df['dd']==i] # Day filter
        df_dayf = df_dayf.reset_index() #reset index
        df_dayf.drop('index', inplace=True, axis=1)
        
        position = []
        user = []
        
        counter = 0
        for j in range(len(df_dayf)):
            counter += 1
            if counter == len(df_dayf):
                break

            elif df_dayf['user'][j] != df_dayf['user'][j+1]:
                position.append(j)
                user.append(df_dayf['user'][j])

        dif_time = []
        counter = 0
        for k in range(len(position)):
            counter += 1
            if counter == len(df_dayf):
                dif_time.append(df_dayf['minutes'][position[k]] - df_dayf['minutes'][position[k-1]])
            elif counter != len(position):
                dif_time.append(df_dayf['minutes'][position[k+1]] - df_dayf['minutes'][position[k]])
        
        conc_user += user[1:]
        conc_responsetime += dif_time
        conc_day += [i for q in range(len(dif_time))]
    responsetime_df = pd.DataFrame({'user':conc_user, 'responsetime':conc_responsetime, 'day':conc_day})
    return responsetime_df

"""Function print info"""
def resinfo(responsetime_df, user):
    """
    Show response time info of each user.
    """
    print('User name :', user)
    print('Average response time :', responsetime_df[responsetime_df.user == user]['responsetime'].mean(), 'minutes')
    print('Longest response time :', responsetime_df[responsetime_df.user == user]['responsetime'].max(), 'minutes')
    print('Shotest response time :', responsetime_df[responsetime_df.user == user]['responsetime'].min(), 'minutes\n')

def rpt_summary(df, responsetime_df):
    """
    Function respond time summary.
    """
    print('Responestime / user')
    # Create list of user
    user_list = list(df.user.value_counts().index)
    for i in range(len(user_list)):
        resinfo(responsetime_df ,user_list[i])