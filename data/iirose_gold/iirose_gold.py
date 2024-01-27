import asyncio
import os
import csv
import datetime

import plotly.graph_objects as go

from API.api_iirose import APIIirose
from API.decorator.command import on_command, MessageType
from API.api_message import at_user

API = APIIirose()
gold_list = [0, 0, None]
gold_csv_file = f'plugins/iirose_gold/gold_data{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'
t2 = False


@on_command('.股票', False, command_type=[MessageType.room_chat, MessageType.private_chat])
async def gold_text(Message):
    await API.send_msg(Message,
                       '.股票 - 查看当前页面\n'
                       '.股票 播报 - 启用/禁用 股票播报\n'
                       '.股票 图表 - 渲染蜡烛图\n'
                       '.股票 计算 (数字) - 股价计算器')
    pass


@on_command('.股票 ', [True, 4], command_type=[MessageType.room_chat, MessageType.private_chat])
async def gold_core(Message, text):
    global t2
    if Message.is_bot:
        return
    if text[:2] == '播报':
        if t2:
            t2 = False
        else:
            t2 = True
        await API.send_msg(Message, f'股票推送已{"启用" if t2 else "关闭"}！')
    elif text[:2] == '图表':
        gold_price = []

        with open(gold_csv_file, newline='') as csvfile:
            spreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spreader:
                row = row[0].split(',')
                gold_price.append((row[0], row[1]))

        gold_data = {
            'DateTime': [],
            'Open': [],
            'High': [],
            'Low': [],
            'Close': []
        }
        for i in range(3, len(gold_price)):
            iirose_data = datetime.datetime.strptime(gold_price[i][0], '%Y-%m-%d-%H:%M:%S')
            now_data = datetime.datetime.now()

            three_hours_ago = now_data - datetime.timedelta(hours=2)

            if three_hours_ago <= iirose_data <= now_data:
                hour = iirose_data.hour
                minute = iirose_data.minute
                second = iirose_data.second

                gold_data['DateTime'].append(f'{hour if len(str(hour)) != 1 else f"0{hour}"}:{minute if len(str(minute)) != 1 else f"0{minute}"}:{second if len(str(second)) != 1 else f"0{hour}"}')
                open_price = float(gold_price[i - 3][1])
                close_price = float(gold_price[i][1])
                high_price = max(float(p[1]) for p in gold_price[i - 3:i + 1])
                low_price = min(float(p[1]) for p in gold_price[i - 3:i + 1])
                gold_data['Open'].append(open_price)
                gold_data['High'].append(high_price)
                gold_data['Low'].append(low_price)
                gold_data['Close'].append(close_price)

        fig = go.Figure(data=[go.Candlestick(x=gold_data['DateTime'],
                                             open=gold_data['Open'],
                                             high=gold_data['High'],
                                             low=gold_data['Low'],
                                             close=gold_data['Close'],
                                             increasing_line_color='#FF0033',
                                             decreasing_line_color='#009966'
                                             )])

        fig.update_layout(
            title='薇股K图',
            xaxis_title='日期 (2h内)',
            yaxis_title='价格 (花钞)',
            plot_bgcolor='rgb(34,34,34)',
            paper_bgcolor='rgb(17,17,17)'
        )
        fig.write_image("plugins/iirose_gold/my_plot.png", scale=4)
        url = await API.upload_files("plugins/iirose_gold/my_plot.png")
        await API.send_msg(Message, f'{url["url"]}#e')
        os.remove("plugins/iirose_gold/my_plot.png")
    elif text[:2] == '计算':
        with open(gold_csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            now_gold_num = float(rows[-1][1])

        if now_gold_num == 0:
            await API.send_msg(Message, '当前数据为空，请等待更新')
            return
        try:
            num = float(text[3:])
        except:
            await API.send_msg(Message, '请输入纯数字')
        try:
            data = f'{at_user(Message.user_name)}\n当前股价 {round(now_gold_num, 3)} 股/钞 \n{num} 股约等于 {round(num * round(now_gold_num, 4), 3)} 钞'
            try:
                data += f'\n{num} 钞约等于 {round(num / round(now_gold_num, 4), 4)} 股'
            except:
                pass
            await API.send_msg(Message, data)
        except:
            await API.send_msg(Message, '当前数据为空，请等待更新')
    else:
        await API.send_msg(Message, '错误：未知的参数')


async def share_message(Data):
    global gold_list
    try:
        def add_data(gold_data, gold_close, all_gold, all_gold_money):
            global gold_csv_file
            gold_csv_file = f'plugins/iirose_gold/gold_data{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'
            with open(gold_csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([gold_data, gold_close, all_gold, all_gold_money])

        formatted_date = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        add_data(formatted_date, Data.price_share, Data.total_share, Data.total_money)

        if t2:
            change = round(Data.price_share - Data.old_price_share, 4)
            percent_change = round((change / Data.old_price_share) * 100, 2)
            if str(change)[:1] != "-":
                gold_list[0] += 1
                gold_list[1] = 0
                gold_list[2] = True
                result = f"增 {change} 增幅 {percent_change}%"
                gold_result = f"已增加 {gold_list[0] if gold_list[2] else gold_list[1]} 次"
            else:
                gold_list[1] += 1
                gold_list[0] = 0
                gold_list[2] = False
                result = f"减 {str(change)[1:]} 减幅 {percent_change}%"
                gold_result = f"已减少 {gold_list[0] if gold_list[2] else gold_list[1]} 次"

            if Data.price_share == 1.0:
                gold_list[0] = 0
                gold_list[1] = 0
                await API.send_msg_to_room("股票已崩盘")
            await API.send_msg_to_room(
                f'股价提醒'
                f'\n{gold_result}'
                f'\n{result}'
                f'\n股价：{round(Data.price_share, 4)} 钞/股'
                f'\n总股：{Data.total_share} 股'
                f'\n总金：{round(Data.total_money, 4)} 钞'
                f'\n100股约等于{round(100 * Data.price_share, 4)}钞')
    except:
        pass


async def on_init():
    dirs = 'plugins/iirose_gold'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
