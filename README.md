# Data visualization from LINE chat. :speech_balloon:

Necessary library.
- pandas
- matplotlib
- seaborn

## How to export chat history.
![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture0.jpg)

## Getting start.

run this file `LINE chat analyze.ipynb`
put chat history name in `read_chat()` function
```python
chat = line_function.read_chat('put file name here.')
```
Variable `chat` i the chat history data received as a text file.

```python
df = line_function.reformat(chat)
```
Variable `df` Is the chat history data, transforms the format into a data frame through the function `line_function.reformat()`

**กราฟแสดงจำนวนข้อความของเราและคู่สนทนา**

![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture1.png)

**กราฟแสดงจำนวนข้อความที่ส่งหากันในแต่ละวัน**

![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture2.PNG)

**กราฟแสดงจำนวนข้อความที่ส่งหากันโดยแบ่งตามคนส่ง**

![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture3.png)

**กราฟแสดงจำนวนข้อความที่ส่งหากันโดยแบ่งตามคนส่ง(แสดงตามเดือนที่เลือก)**

![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture4.png)

**กราฟแสดงจำนวนข้อความที่ส่งหากันทั้งหมดโดยแยกตามช่วงเวลา**

![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture5.PNG)

**กราฟแสดงวันและเวลาไหนที่มีการคส่งข้อความหากันมากที่สุด(ยิ่งสีเข้มแสดงว่ามีการส่งข้อความหากันมาก)**

![alt text](https://github.com/wsirigate/Line_chat_visualize/blob/master/img/Capture6.PNG)
