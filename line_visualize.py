import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import pandas as pd
import re

def filter_plot(df, month_year):
    """
    Plot number of message for each user in specific month and year.
    """
    user_day = pd.DataFrame(df.groupby(['date', 'user']).size(), columns=['count']).unstack()
    user_day.columns = user_day.columns.droplevel()
    
    lst_filter = []
    for i in range(len(user_day)):
        if re.search(month_year, user_day.index[i]):
            lst_filter.append(True)
        else:
            lst_filter.append(False)
            
    plt.figure()
    p = user_day[lst_filter].plot.bar(figsize=(20,5), fontsize=12)
    p.set_title(F"message per days ( {month_year} )", fontsize=16)
    user_day[lst_filter].plot(figsize=(20,5))
    plt.xticks(rotation='vertical')
    plt.show()

def day_message(df):
    """
    number of messages each user and day. [all time]
    """
    user_date = pd.DataFrame(df.groupby(['day', 'user']).size(), columns=['count']).unstack()
    user_date.columns = user_date.columns.droplevel()
    user_date = user_date.reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

    plt.figure()
    p = user_date.plot.bar(figsize=(10, 5))
    p.set_title('number of messages each user and day. [all time]', fontsize=16)
    plt.xticks(rotation='vertical')
    plt.show()


def day_duration(df):
    """
    Plot Which day and time that most chatting.
    """
    gg = df.groupby(['day', 'group'])
    gg = gg.size().unstack()
    gg = gg.reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    gg = gg.fillna(0)

    plt.figure(figsize=(9,7))
    ax = sns.heatmap(gg, cmap="YlGnBu", annot=True, fmt='.0f')
    ax.set_xlabel('duration')
    ax.set_title("Which day and time that most chatting. (all time)", fontsize=16)