import json
import requests


def send_single_sms(apikey, code, mobile):
    # 发送单条短信
    url = 'https://sms.yunpian.com/v2/sms/single_send.json'
    text = f'【蒋宗佑 test】您的验证码是{code}。如非本人操作，请忽略本短信'
    res = requests.post(url, data={
        'apikey': apikey,
        'mobile': mobile,
        'text': text,
    })
    re_json = json.loads(res.text)
    return re_json


if __name__ == '__main__':
    res = send_single_sms('cdb6f4b3860c552f790176a9e4f3fd85', '0000', '18572355511')
    if res['code'] == 0:
        print('发送成功')
    else:
        print(f'发送失败: {res.msg}')
    print(res)
