'''
@File                : notify.py
@Github              : https://github.com/y1ndan/genshin-impact-helper
@Last modified by    : y1ndan
@Last modified time  : 2021-01-13 11:01:10
'''
import json
import os
import time
import hmac
import hashlib
import base64

import requests
from requests.exceptions import HTTPError
from urllib import parse

from settings import log


class Notify(object):
    @staticmethod
    def to_python(json_str: str):
        return json.loads(json_str)

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    # ============================== Server Chan ==============================
    # 此处填你申请的SCKEY
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=SCKEY,Value=<获取的值>
    SCKEY = ''

    if os.environ.get('SCKEY', '') != '':
        SCKEY = os.environ['SCKEY']

    # ============================== Cool Push ================================
    # 此处填你申请的SKEY(详见文档: https://cp.xuthus.cc/)
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=COOL_PUSH_SKEY,Value=<获取的值>
    COOL_PUSH_SKEY = ''
    # 此处填写私聊(send)或群组(group)或者微信(wx)推送方式，默认私聊推送
    # 注: Github Actions用户若要更改,请到Settings->Secrets里设置,Name=COOL_PUSH_MODE,Value=<group或wx>
    COOL_PUSH_MODE = 'send'

    if os.environ.get('COOL_PUSH_SKEY', '') != '':
        COOL_PUSH_SKEY = os.environ['COOL_PUSH_SKEY']
    if os.environ.get('COOL_PUSH_MODE', '') != '':
        COOL_PUSH_MODE = os.environ['COOL_PUSH_MODE']

    # ============================== iOS Bark App =============================
    # 此处填你Bark App的信息(IP/设备码,例如: https://api.day.app/XXXXXXXX)
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=BARK_KEY,Value=<获取的值>
    BARK_KEY = ''
    # BARK App推送铃声,铃声列表去App内查看
    # 注: Github Actions用户若要更改,请到Settings->Secrets里设置,Name=BARK_SOUND,Value=<铃声名称>
    BARK_SOUND = 'healthnotification'

    if os.environ.get('BARK_KEY', '') != '':
        if os.environ['BARK_KEY'].find(
                'https') != -1 or os.environ['BARK_KEY'].find('http') != -1:
            # 兼容BARK自建服务端用户
            BARK_KEY = os.environ['BARK_KEY']
        else:
            BARK_KEY = 'https://api.day.app/' + os.environ['BARK_KEY']
    elif os.environ.get('BARK_SOUND', '') != '':
        BARK_SOUND = os.environ['BARK_SOUND']
    elif BARK_KEY != '' or BARK_KEY.find('https') != -1 or BARK_KEY.find(
            'http') != -1:
        # 兼容BARK本地用户只填写设备码的情况
        BARK_KEY = 'https://api.day.app/' + BARK_KEY

    # ============================== Telegram Bot =============================
    # 此处填你telegram bot的Token,例如: 1077xxx4424:AAFjv0FcqxxxxxxgEMGfi22B4yh15R5uw
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=TG_BOT_TOKEN,Value=<获取的值>
    TG_BOT_TOKEN = ''
    # 此处填你接收通知消息的telegram用户的id,例如: 129xxx206
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=TG_USER_ID,Value=<获取的值>
    TG_USER_ID = ''

    if os.environ.get('TG_BOT_TOKEN', '') != '':
        TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
    if os.environ.get('TG_USER_ID', '') != '':
        TG_USER_ID = os.environ['TG_USER_ID']

    # ============================== DingTalk Bot =============================
    # 此处填你钉钉机器人的webhook,例如: 5a544165465465645d0f31dca676e7bd07415asdasd
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=DD_BOT_TOKEN,Value=<获取的值>
    DD_BOT_TOKEN = ''
    # 加签密钥,机器人安全设置页面,加签一栏下面显示的SEC开头的字符串
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=DD_BOT_SECRET,Value=<获取的值>
    DD_BOT_SECRET = ''

    if os.environ.get('DD_BOT_TOKEN', '') != '':
        DD_BOT_TOKEN = os.environ['DD_BOT_TOKEN']
    if os.environ.get('DD_BOT_SECRET', '') != '':
        DD_BOT_SECRET = os.environ['DD_BOT_SECRET']

    # ============================== WeChat Work Bot ==========================
    # 此处填你企业微信机器人的webhook(详见文档 https://work.weixin.qq.com/api/doc/90000/90136/91770) 例如: 693a91f6-7xxx-4bc4-97a0-0ec2sifa5aaa
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=WW_BOT_KEY,Value=<获取的值>
    WW_BOT_KEY = ''

    if os.environ.get('WW_BOT_KEY', '') != '':
        WW_BOT_KEY = os.environ['WW_BOT_KEY']

    # ============================== iGot聚合推送 =================================
    # 此处填你iGot的信息(推送key,例如: https://push.hellyw.com/XXXXXXXX)
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=IGOT_KEY,Value=<获取的值>
    IGOT_KEY = ''

    if os.environ.get('IGOT_KEY', '') != '':
        IGOT_KEY = os.environ['IGOT_KEY']

    # ============================== push+ ====================================
    # 官方文档: https://pushplus.hxtrip.com/
    # PUSH_PLUS_TOKEN: 微信扫码登录后一对一推送或一对多推送下面的token(您的Token)，不配置PUSH_PLUS_USER则默认为一对一推送
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=PUSH_PLUS_TOKEN,Value=<获取的值>
    PUSH_PLUS_TOKEN = ''
    # PUSH_PLUS_USER: 一对多推送的“群组编码”（一对多推送下面->您的群组(如无则新建)->群组编码，如果您是创建群组人。也需点击“查看二维码”扫描绑定，否则不能接受群组消息推送）
    # 注: Github Actions用户请到Settings->Secrets里设置,Name=PUSH_PLUS_USER,Value=<获取的值>
    PUSH_PLUS_USER = ''

    if os.environ.get('PUSH_PLUS_TOKEN', '') != '':
        PUSH_PLUS_TOKEN = os.environ['PUSH_PLUS_TOKEN']
    if os.environ.get('PUSH_PLUS_USER', '') != '':
        PUSH_PLUS_USER = os.environ['PUSH_PLUS_USER']

    def serverChan(self, text, status, desp):
        if Notify.SCKEY != '':
            url = 'https://sc.ftqq.com/{}.send'.format(Notify.SCKEY)
            data = {'text': '{} {}'.format(text, status), 'desp': desp}
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['errno'] == 0:
                    log.info('Server酱推送成功')
                elif response['errno'] == 1024:
                    # SCKEY错误或一分钟内发送相同内容
                    log.error('Server酱推送失败:\n{}'.format(response['errmsg']))
                else:
                    log.error('Server酱推送失败:\n{}'.format(response))
        else:
            log.info('您未配置Server酱推送所需的SCKEY,取消Server酱推送')
            pass

    def coolPush(self, text, status, desp):
        if Notify.COOL_PUSH_SKEY != '':
            url = 'https://push.xuthus.cc/{}/{}'.format(
                Notify.COOL_PUSH_MODE, Notify.COOL_PUSH_SKEY)
            data = '{} {}\n\n{}'.format(text, status, desp).encode('utf-8')
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['code'] == 200:
                    log.info('Cool Push推送成功')
                else:
                    log.error('Cool Push推送失败:\n{}'.format(response))
        else:
            log.info('您未配置Cool Push推送所需的COOL_PUSH_SKEY,取消Cool Push推送')
            pass

    def bark(self, text, status, desp):
        if Notify.BARK_KEY != '':
            url = '{}/{} {}/{}?sound={}'.format(Notify.BARK_KEY, 
                text, status, parse.quote(desp), Notify.BARK_SOUND)
            try:
                response = self.to_python(requests.get(url).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['code'] == 200:
                    log.info('Bark推送成功')
                elif response['code'] == 400:
                    log.error('Bark推送失败:\n{}'.format(response['message']))
                else:
                    log.error('Bark推送失败:\n{}'.format(response))
        else:
            log.info('您未配置Bark推送所需的BARK_KEY,取消Bark推送')
            pass

    def tgBot(self, text, status, desp):
        if Notify.TG_BOT_TOKEN != '' or Notify.TG_USER_ID != '':
            url = 'https://api.telegram.org/bot{}/sendMessage'.format(
                Notify.TG_BOT_TOKEN)
            data = {
                'chat_id': Notify.TG_USER_ID,
                'text': '{} {}\n\n{}'.format(text, status, desp),
                'disable_web_page_preview': True
            }
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['ok']:
                    log.info('Telegram推送成功')
                elif response['error_code'] == 400:
                    log.error('请主动给bot发送一条消息并检查接收用户ID是否正确')
                elif response['error_code'] == 401:
                    log.error('TG_BOT_TOKEN错误')
                else:
                    log.error('Telegram推送失败:\n{}'.format(response))
        else:
            log.info('您未配置Telegram推送所需的TG_BOT_TOKEN和TG_USER_ID,取消Telegram推送')
            pass

    def ddBot(self, text, status, desp):
        if Notify.DD_BOT_TOKEN != '':
            url = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(
                Notify.DD_BOT_TOKEN)
            data = {
                'msgtype': 'text',
                'text': {
                    'content': '{} {}\n\n{}'.format(text, status, desp)
                }
            }
            if Notify.DD_BOT_SECRET != '':
                secret = Notify.DD_BOT_SECRET
                timestamp = int(round(time.time() * 1000))
                secret_enc = bytes(secret).encode('utf-8')
                string_to_sign = '{}\n{}'.format(timestamp, secret)
                string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
                hmac_code = hmac.new(
                    secret_enc, string_to_sign_enc,
                    digestmod=hashlib.sha256).digest()
                sign = parse.quote_plus(base64.b64encode(hmac_code))
                url = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(
                    Notify.DD_BOT_TOKEN, timestamp, sign)
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['errcode'] == 0:
                    log.info('钉钉推送成功')
                else:
                    log.error('钉钉推送失败:\n{}'.format(response))
        else:
            log.info('您未配置钉钉推送所需的DD_BOT_TOKEN或DD_BOT_SECRET,取消钉钉推送')
            pass

    def wwBot(self, text, status, desp):
        if Notify.WW_BOT_KEY != '':
            url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'.format(
                Notify.WW_BOT_KEY)
            data = {
                'msgtype': 'text',
                'text': {
                    'content': '{} {}\n\n{}'.format(text, status, desp)
                }
            }
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['errcode'] == 0:
                    log.info('企业微信推送成功')
                else:
                    log.error('企业微信推送失败:\n{}'.format(response))
        else:
            log.info('您未配置企业微信推送所需的WW_BOT_KEY,取消企业微信推送')
            pass

    def iGot(self, text, status, desp):
        if Notify.IGOT_KEY != '':
            url = 'https://push.hellyw.com/{}'.format(Notify.IGOT_KEY)
            data = {'title': '{} {}'.format(text, status), 'content': desp}
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['ret'] == 0:
                    log.info('iGot推送成功')
                else:
                    log.error('iGot推送失败:\n{}'.format(response))
        else:
            log.info('您未配置iGot推送所需的IGOT_KEY,取消iGot推送')
            pass

    def pushPlus(self, text, status, desp):
        if Notify.PUSH_PLUS_TOKEN != '':
            url = 'https://pushplus.hxtrip.com/send'
            data = {
                'token': Notify.PUSH_PLUS_TOKEN,
                'title': '{} {}'.format(text, status),
                'content': desp,
                'topic': Notify.PUSH_PLUS_USER
            }
            try:
                response = self.to_python(requests.post(url, data=data).text)
            except Exception as e:
                log.error(e)
                raise HTTPError
            else:
                if response['code'] == 200:
                    log.info('pushplus推送成功')
                else:
                    log.error('pushplus推送失败:\n{}'.format(response))
        else:
            log.info('您未配置pushplus推送所需的PUSH_PLUS_TOKEN,取消pushplus推送')
            pass

    def send(self, **kwargs):
        app = '原神签到小助手'
        status = kwargs.get('status', '')
        msg = kwargs.get('msg', '')
        if isinstance(msg, list) or isinstance(msg, dict):
            # msg = self.to_json(msg)
            msg = '\n\n'.join(msg)
        log.info(f'签到结果: {status}\n\n{msg}')
        log.info('准备推送通知...')

        self.serverChan(app, status, msg)
        self.coolPush(app, status, msg)
        self.bark(app, status, msg)
        self.tgBot(app, status, msg)
        self.ddBot(app, status, msg)
        self.wwBot(app, status, msg)
        self.iGot(app, status, msg)
        self.pushPlus(app, status, msg)


if __name__ == '__main__':
    Notify().send(app='原神签到小助手', status='签到状态', msg='内容详情')

