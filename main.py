import requests, time

cookie = 'put your cookie here'
rolimons = requests.get('https://www.rolimons.com/itemapi/itemdetails').json()['items']
userId = requests.get('https://api.roblox.com/xboxlive/get-roblox-userInfo', cookies={'.ROBLOSECURITY': cookie}).json()['userId']

cursor = ''
spent = 0
gained = 0
payout = 0
traded = 0

def checkSold(tradeId):
    global traded
    myvalue = theirvalue = 0
    while True:
        resp = requests.get(
            f'https://trades.roblox.com/v1/trades/{tradeId}',
            cookies={'.ROBLOSECURITY': cookie}
        )
        if resp.status_code == 200:
            data = resp.json()['offers']
            for i in data[0]['userAssets']:
                myvalue += rolimons[str(i['assetId'])][4]
            for i in data[1]['userAssets']:
                theirvalue += rolimons[str(i['assetId'])][4]
            if theirvalue <= myvalue*0.5:
                traded += myvalue
                return True
            else: return False
        else:
            print('waiting trade')
            time.sleep(60)

resp = requests.get(
    f'https://economy.roblox.com/v2/users/{userId}/transactions?cursor=&limit=100&transactionType=GroupPayout',
    cookies={'.ROBLOSECURITY': cookie}
).json()['data']
for p in resp:
    payout += p['currency']['amount']

while cursor != None:
    resp = requests.get(
        f'https://economy.roblox.com/v2/users/{userId}/transactions?cursor={cursor}&limit=100&transactionType=Purchase',
        cookies={'.ROBLOSECURITY': cookie}
    )
    if resp.status_code == 200:
        data = resp.json()['data']
        for item in data:
            if 'id' in item['details']:
                assetId = str(item['details']['id'])
                if assetId in rolimons:
                    gained += rolimons[assetId][4]
                    spent += item['currency']['amount']
        cursor = resp.json()['nextPageCursor']
    else:
        print('waiting 60 seconds')
        time.sleep(60)

cursor = ''
while cursor != None:
    resp = requests.get(
        f'https://trades.roblox.com/v1/trades/completed?cursor={cursor}&limit=100&sortOrder=Desc',
        cookies={'.ROBLOSECURITY': cookie}
    )
    if resp.status_code == 200:
        data = resp.json()['data']
        checked = 0
        for i in data:
            checkSold(i['id'])
            checked += 1
            print(f'Trades Checked: {checked}/{len(data)}')
        cursor = resp.json()['nextPageCursor']
    else:
        print('waiting trades seconds')
        time.sleep(60)


spent = str(spent).replace('-', '')
print(f'\n\nValue Gained: {"{:,}".format(int(gained))}\nRobux Spent: {"{:,}".format(int(spent))}\nOverall Payout: {"{:,}".format(int(payout))}\nValue USD Sold: {"{:,}".format(int(traded))} (based on completed trades)')
