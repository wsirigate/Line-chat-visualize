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
    df.drop('minutes', axis=1, inplace = True)
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
