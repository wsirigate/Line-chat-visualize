# Data visualization from LINE chat. :speech_balloon:

## How to export chat history.
![export chat history](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/export_chat.png)
hamburger menu icon -> Oter settings -> Export chat history -> sent!

## Getting start.

Run this file `Line-Visualization.ipynb`
put your chat history name instead of 'LINE_Chat_with_someone.txt'
```python
# Read chat file
df = Open('LINE_Chat_with_someone.txt').data()
# Use for visulize the data
chat = getInformation(df)
```

Use `chat.summary()` to show summary information from the chat history.
```python
chat.summary()
```
![summary plot](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/summary.png)

Use `chat.activity()` to show activity by time
```python
chat.activity()
```
![chat activity heatmap](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/heatmap.png)
![chat activity polar](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/polar.png)

```python
chat.chronological()
```
![chat activity chronological](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/chronological.png)

by the way you also can customize the start date and end date by using this parameter `chat.activity(custom=True, start='dd-mm-yyyy', end='dd-mm-yyyy')`
```python
# customize time window
chat.activity(custom=True, start='01-08-2020', end='30-12-2020')
```
![chat activity heatmap](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/heatmap_custom.png)
![chat activity polar](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/polar_custom.png)
```python
# customize time window
chat.chronological(custom=True, start='01-08-2020', end='31-12-2020')
```
![chat activity chronological](https://github.com/wsirigate/Line-chat-visualize/blob/c2755b20a99c7184afa3d034c8651da02c3826fd/img/chronological_custom.png)
