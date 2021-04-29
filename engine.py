import re
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime

class Open:
    def __init__(self, filename):
        self.filename = filename

    def data(self):
        # Read chat file
        file = open(self.filename, "r", encoding="utf8")
        chat = [i.strip() for i in file]

        chat_with = re.findall(r'(?<=with\s).+', chat[0])[0]
        chat = chat[3:]
        # Create data frame
        try:
            df = pd.DataFrame(list(map(lambda message: message.split('\t'), chat)), columns=['time', 'user', 'message'])
        except:
            df = pd.DataFrame(list(map(lambda message: message.split('\t'), chat))).iloc[:, :3]
            df.columns = ['time', 'user', 'message']

        # Insert date column
        df.insert(0, "date", df.time.apply(lambda message: message if re.search(r'\S{3},\s\d{2}/\d{2}/\d{4}\sBE$', message) else np.NaN))
        df.loc[:, 'date'] = df.date.fillna(method='ffill')
        df = df.dropna(thresh=4).reset_index(drop=True)

        # Deal with unsent message
        df.loc[:, 'user'] = df.user.str.replace(' unsent a message.', '', regex=True)
        # Deal with changed the name of the album
        df.loc[:, 'user'] = df.user.apply(lambda x: re.sub(r'changed the name of the album.+|\u2068|\u2069|\s', '', x))
        # Replace user name
        df.loc[:, 'user'] = df.user.replace('You', set(df.user.unique()).difference({'You', chat_with}).pop())
        
        return self.formatDate(df)


    def formatDate(self, df):
        """
        Reformatted dataframe date
        """
        if df.date[0][-2:] == 'BE':
            df.loc[:, 'date'] = df.date.apply(lambda x: x.split(' ')[1])
            df.loc[:, 'date'] = df.date.apply(lambda x: x[:-4] + str(int(x[-4:])-543))
        else:
            df.loc[:, 'date'] = df.date.apply(lambda x: x.split(' ')[1])

        # Create datetime column
        df.insert(0, 'datetime', df.date + ' ' + df.time)
        df.loc[:, 'datetime'] = pd.to_datetime(df.datetime, format=('%d/%m/%Y %H:%M'))
        # reformatted date column
        df['date'] = df.datetime.dt.strftime('%y-%m-%d')

        df.insert(1, 'day', df.datetime.dt.strftime('%a'))
        df.insert(2, 'month', df.datetime.dt.month)
        df.insert(3, 'year', df.datetime.dt.year)
        
        df = df.drop(columns=['time'])
        
        # Create Time bining (1 hours)
        bins = list(range(0, 25*60, 60))
        labels = [f'{str(i)}-{str(i+1)}' for i in range(0, 24)]
        df['minutes'] = df.datetime.dt.hour * 60 + df.datetime.dt.minute
        # insert bin cokumn in dataframe
        df.insert(1, 'bin', pd.cut(df.minutes, bins=bins, labels=labels).fillna('0-1'))
        df.drop('minutes', axis=1, inplace = True)
        
        return df


class getInformation:
    def __init__(self, df):
        self.df = df

    def summary(self):
        # Days total
        days_total = self.df.datetime.dt.strftime('%d/%m/%Y').nunique()
        # Message total
        message_total = len(self.df.message)
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "number",
            value = days_total,
            title = {"text": "DAYS TOTAL<br><span style='font-size:0.8em;color:gray'>"}, # Subtitle</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>
            number = {'valueformat':','},
            domain = {'row': 0, 'column': 0}))


        fig.add_trace(go.Indicator(
            mode = "number",
            value = message_total,
            number = {'valueformat':','},
            title = {"text": "MESSAGES TOTAL<br><span style='font-size:0.8em;color:gray'>"}, # Subtitle</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>
            domain = {'row': 0, 'column': 1}))

        fig.add_trace(go.Indicator(
            mode = "number",
            value = np.mean(self.df.groupby(['day', 'month', 'year'])['message'].count().reset_index(drop=True)).round(),
            number = {'valueformat':','},
            title = {"text": "AVERAGE MESSAGE PER DAY<br><span style='font-size:0.8em;color:gray'>"}, # Subtitle</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>
            domain = {'row': 0, 'column': 2}))

        fig.update_layout(grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})
        fig.show()

    
    def activity(self, custom=False, start='', end=''):
        # Heatmap plot
        if custom == True:
            # filter_df = self.df[(self.df.month == month) & (self.df.year == year)]
            filter_df = self.df[(self.df.datetime >= datetime.strptime(start, '%d-%m-%Y')) & (self.df.datetime <= datetime.strptime(end, '%d-%m-%Y'))].reset_index(drop=True)
            time_df = filter_df.groupby(['bin'])['message'].count().reset_index()
            group = filter_df.groupby(['day', 'bin'])
            # total = filter_df.groupby(['date', 'user'])['message'].count().reset_index()
        else:
            group = self.df.groupby(['day', 'bin'])
            time_df = self.df.groupby(['bin'])['message'].count().reset_index()
            # total = self.df.groupby(['date', 'user'])['message'].count().reset_index()
        group = group.size().unstack()
        group = group.reindex(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        group = group.fillna(0)
        group.columns.name = 'Time'

        fig = px.imshow(group.to_numpy(),
                        labels=dict(x="Time of day", y="Day of week", color="Number of message"),
                        x=[f'{i} h' for i in range(0, 24)],
                        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        color_continuous_scale='Bluyl',
                        title='ACTIVITY BY TIME OF THE DAY') # width=1200, height=500
        fig.update_xaxes(side="top")
        fig.update_layout(hovermode="x")
        fig.show()

        # Polar plor
        time_df['bin'] = [str(i)+' h' for i in range(24)]

        fig2 = px.line_polar(time_df, r='message', theta='bin', line_close=True,
                            title='ACTIVITY BY TIME') # width=500, height=500
        fig2.update_traces(fill='toself')

        fig2.update_layout(
        polar=dict(
            radialaxis=dict(
            visible=True
            ),
        ),
        showlegend=False
        )

        fig2.show()

    def chronological(self, custom=False, start='', end=''):
        """
        custom = True
        start: day-month-year
        end: day-month-year
        """
        if custom == False:
            tmp_df = self.df.groupby(['date', 'user'])['message'].count().reset_index()
        else:
            tmp_df = self.df[(self.df.datetime >= datetime.strptime(start, '%d-%m-%Y')) & (self.df.datetime <= datetime.strptime(end, '%d-%m-%Y'))].reset_index(drop=True)
            tmp_df = tmp_df.groupby(['date', 'user'])['message'].count().reset_index()
        
        fig = px.bar(data_frame=tmp_df, x='date', y='message',
                     color='user',
                     title='CHRONOLOGICAL GRAPH')
        fig.show()