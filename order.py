import json
import requests
from time import sleep
import threading
import random
import time
import datetime
import copy


def getCapacityData():
    global deliveryTime

    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/delivery/portal/getCapacityData'
    data = {
        "perDateList": date_list,
        "storeDeliveryTemplateId": storeDeliveryTemplateId
    }
    try:
        ret = requests.post(url=myUrl, headers=global_headers, data=json.dumps(data))
        # print(ret.text)
        myRet = ret.json()
        print('#获取可用配送时间中')
        list1 = myRet['data']['capcityResponseList']
        for days in list1:
            for time in days['list']:
                # print(time['startTime'] + " , " + time['endTime'])
                startRealTime = time['startRealTime']
                endRealTime = time['endRealTime']
                deliveryTimeArr = [startRealTime, endRealTime]
                timeKey = startRealTime + endRealTime
                deliveryTime[timeKey] = deliveryTimeArr
                # if not time_list[i].get('timeISFull'):
                #     print('配送时间 可用:')
                # else:
                #     print('配送时间 已满:')
    except Exception as e:
        print('getCapacityData [Error]: ' + str(e))


def order(body_data):
    global isGo
    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/trade/settlement/commitPay'
    # print(global_headers)
    # print(body_data)
    try:
        ret = requests.post(url=myUrl, headers=global_headers, data=json.dumps(body_data))
        print(ret.text)
        myRet = ret.json()
        status = myRet.get('success')
        if status:
            print('【成功】哥，咱家有菜了~')
            isGo = False
            # 通知自由发挥
            import os
            file = r"nb.mp3"
            os.system(file)
            exit()

    except Exception as e:
        print('order [Error]: ' + str(e))

# 轮巡发货时间查询,建议2-4秒一次
def runGetCapacityData():
    print('runGetCapacityData start')
    while isGo:
        getCapacityData()
        for k, v in deliveryTime.items():
            #打印拿到的时间
            starttimeArray = time.localtime(int(v[0]) /1000)
            startStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", starttimeArray)
            endtimeArray = time.localtime(int(v[1]) /1000)
            endStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", endtimeArray)
            print("当前获得的配送时间区域: " + str(startStyleTime) + " 至 " + str(endStyleTime))
            sleep_time = random.randint(2, 4)
            sleep(sleep_time)


# 下订单线程,间隔时间建议1-2
def runOrder(body_data):
    while isGo:
        order(body_data)
        sleep_time = random.randint(1, 2)
        sleep(sleep_time)

# 根据发货时间列表,创建下订单线程,1秒一次
def runCreateData():
    global global_data
    global threadPool
    while isGo:
        if len(deliveryTime) > 0 and len(threadPool) < len(deliveryTime) * threadCount:
            for k, v in deliveryTime.items():
                body_data = copy.deepcopy(global_data)
                body_data['settleDeliveryInfo']['expectArrivalTime'] = v[0]
                body_data['settleDeliveryInfo']['expectArrivalEndTime'] = v[1]
                for i in range(1,threadCount + 1):
                    tOrder = threading.Thread(target=runOrder,args=(body_data, ))
                    tOrder.setName(k + ":" + str(i))
                    tOrder.start()
                    threadPool.append(tOrder)

        sleep(1)



if __name__ == '__main__':
    # 线程结束标志位,抢购成功结束程序
    isGo = True
    # 单个时间段下单线程数
    threadCount = 1
    # 下单线程池
    threadPool = []
    # 当前支持的配送时间段,用于多时段抢购
    deliveryTime = {}

    # 盲猜一个配送时间可以在这里修改,用于打提前量
    # deliveryTime["424"]= ["1650762000000", ""]

    # 查询配送信息的一周动态组装
    date_list = []
    for i in range(0, 7):
        date_list.append((datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))

    # 组装header
    fr = open('file/headers.txt', 'r')
    global_headers = json.loads(fr.read())
    fr.close()

    # 组装data
    fr = open('file/data.txt', 'r')
    global_data = json.loads(fr.read())
    fr.close()

    # 设定下getCapacityData的头信息
    storeDeliveryTemplateId = global_data['deliveryInfoVO'].get('storeDeliveryTemplateId')

    # 发货时间查询启动
    t1 = threading.Thread(target=runGetCapacityData,args=())
    t1.start()

    # 尽量等第一次时间查询完再启动下单线程
    sleep(2)

    # 不同时间段的下单线程启动程序
    t2 = threading.Thread(target=runCreateData,args=())
    t2.start()


