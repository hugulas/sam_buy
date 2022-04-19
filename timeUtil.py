import time

# 日期转毫秒时间戳
def getTimestamp(date):
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    #转换成时间戳
    timestamp = time.mktime(timeArray)

    print(int(round(timestamp * 1000)))

# 毫秒时间戳转日期
def getDate(timestamp):

    # 转换成localtime
    time_local = time.localtime(timestamp / 1000)

    # 转换成新的时间格式(2016-05-05 20:28:54)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

    print(date)

if __name__ == '__main__':
    date = "2022-04-20 09:00:00"
    getTimestamp(date)

    timestamp = 1650416400000
    getDate(timestamp)