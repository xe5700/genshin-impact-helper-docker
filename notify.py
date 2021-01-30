'''
@File                : notify.py
@Github              : https://github.com/y1ndan/genshin-impact-helper
@Last modified by    : y1ndan
@Last modified time  : 2021-01-30 15:43:57
'''
import os
import time
import hmac
import hashlib
import base64

from urllib import parse
from settings import log, req


class Notify(object):
    """Push all in one
    :param SCKEY: Server酱的SCKEY.详见文档: https://sc.ftqq.com/
    :param COOL_PUSH_SKEY: Cool Push的SKEY.详见文档: https://cp.xuthus.cc/
    :param COOL_PUSH_MODE: Cool Push的推送方式.可选私聊(send)、群组(group)或者微信(wx),默认: send
    :param BARK_KEY: Bark的IP或设备码.例如: https://api.day.app/xxxxxx
    :param BARK_SOUND: Bark的推送铃声.在APP内查看铃声列表,默认: healthnotification
    :param TG_BOT_TOKEN: Telegram Bot的token.向bot father申请bot时生成.
    :param TG_USER_ID: Telegram推送对象的用户ID.
    :param DD_BOT_TOKEN: 钉钉机器人WebHook地址中access_token后的字段.
    :param DD_BOT_SECRET: 钉钉加签密钥.在机器人安全设置页面,加签一栏下面显示的以SEC开头的字符串.
    :param WW_BOT_KEY: 企业微信机器人WebHook地址中key后的字段.
        详见文档: https://work.weixin.qq.com/api/doc/90000/90136/91770
    :param WW_ID: 企业微信的企业ID(corpid).在'管理后台'->'我的企业'->'企业信息'里查看.
        详见文档: https://work.weixin.qq.com/api/doc/90000/90135/90236
    :param WW_APP_SECRET: 企业微信应用的secret.在'管理后台'->'应用与小程序'->'应用'->'自建',点进某应用里查看.
    :param WW_APP_USERID: 企业微信应用推送对象的用户ID.在'管理后台'->'通讯录',点进某用户的详情页里查看,默认: @all
    :param WW_APP_AGENTID: 企业微信应用的agentid.在'管理后台'->'应用与小程序'->'应用',点进某应用里查看.
    :param IGOT_KEY: iGot的KEY.例如: https://push.hellyw.com/xxxxxx
    :param PUSH_PLUS_TOKEN: pushplus一对一推送或一对多推送的token.
        不配置PUSH_PLUS_USER则默认为一对一推送.详见文档: https://pushplus.hxtrip.com/
    :param PUSH_PLUS_USER: pushplus一对多推送的群组编码.
        在'一对多推送'->'您的群组'(如无则新建)->'群组编码'里查看,如果是创建群组人,也需点击“查看二维码”扫描绑定,否则不能接受群组消息.
    """
    # Github Actions用户请到Repo的Settings->Secrets里设置变量,变量名字必须与上述参数变量名字完全一致,否则无效!!!
    # Name=<变量名字>,Value=<获取的值>
    # Server Chan
    SCKEY = ''
    # Cool Push
    COOL_PUSH_SKEY = ''
    COOL_PUSH_MODE = 'send'
    # iOS Bark App
    BARK_KEY = ''
    BARK_SOUND = 'healthnotification'
    # Telegram Bot
    TG_BOT_TOKEN = ''
    TG_USER_ID = ''
    # DingTalk Bot
    DD_BOT_TOKEN = ''
    DD_BOT_SECRET = ''
    # WeChat Work Bot
    WW_BOT_KEY = ''
    # WeChat Work App
    WW_ID = ''
    WW_APP_SECRET = ''
    WW_APP_USERID = '@all'
    WW_APP_AGENTID = ''
    # iGot聚合推送
    IGOT_KEY = ''
    # pushplus
    PUSH_PLUS_TOKEN = ''
    PUSH_PLUS_USER = ''

    def pushTemplate(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        name = kwargs.get('name')
        needs = kwargs.get('needs')
        token = kwargs.get('token')
        text = kwargs.get('text')
        code = kwargs.get('code')
        if not token:
            log.info(f'{name} 推送所需的 {needs} 未设置, 正在跳过...')
            return
        try:
            response = req.to_python(req.request(
                method, url, params, data, json, headers).text)
            rspcode = response[text]
        except Exception as e:
            log.error(e)
        else:
            if rspcode == code:
                log.info(f'{name} 推送成功')
            # Telegram Bot
            elif name == 'Telegram Bot' and rspcode:
                log.info(f'{name} 推送成功')
            elif name == 'Telegram Bot' and response[code] == 400:
                log.error(f'{name} 推送失败:\n请主动给 bot 发送一条消息并检查 TG_USER_ID 是否正确')
            elif name == 'Telegram Bot' and response[code] == 401:
                log.error(f'{name} 推送失败:\nTG_BOT_TOKEN 错误')
            else:
                log.error(f'{name} 推送失败:\n{response}')

    def serverChan(self, text, status, desp):
        SCKEY = self.SCKEY
        if 'SCKEY' in os.environ:
            SCKEY = os.environ['SCKEY']

        conf = {
            'name': 'Server酱',
            'needs': 'SCKEY',
            'token': SCKEY,
            'text': 'errno',
            'code': 0,
            'url': f'https://sc.ftqq.com/{SCKEY}.send',
            'data': {
                'text': f'{text} {status}',
                'desp': desp
            }
        }

        return self.pushTemplate('post', conf['url'], data=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def coolPush(self, text, status, desp):
        COOL_PUSH_SKEY = self.COOL_PUSH_SKEY
        if 'COOL_PUSH_SKEY' in os.environ:
            COOL_PUSH_SKEY = os.environ['COOL_PUSH_SKEY']

        COOL_PUSH_MODE = self.COOL_PUSH_MODE
        if 'COOL_PUSH_MODE' in os.environ:
            COOL_PUSH_MODE = os.environ['COOL_PUSH_MODE']

        conf = {
            'name': 'Cool Push',
            'needs': 'COOL_PUSH_SKEY',
            'token': COOL_PUSH_SKEY,
            'text': 'code',
            'code': 200,
            'url': f'https://push.xuthus.cc/{COOL_PUSH_MODE}/{COOL_PUSH_SKEY}',
            'data': f'{text} {status}\n\n{desp}'.encode('utf-8')
        }

        return self.pushTemplate('post', conf['url'], data=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def bark(self, text, status, desp):
        BARK_KEY = self.BARK_KEY
        if 'BARK_KEY' in os.environ:
            # 自建服务端的用户
            if os.environ['BARK_KEY'].find(
                'https') != -1 or os.environ['BARK_KEY'].find('http') != -1:
                BARK_KEY = os.environ['BARK_KEY']
            else:
                BARK_KEY = f"https://api.day.app/{os.environ['BARK_KEY']}"
        # 本地只填写设备码的用户
        elif BARK_KEY and BARK_KEY.find('https') == -1 and BARK_KEY.find('http') == -1:
            BARK_KEY = f'https://api.day.app/{BARK_KEY}'

        BARK_SOUND = self.BARK_SOUND
        if 'BARK_SOUND' in os.environ:
            BARK_SOUND = os.environ['BARK_SOUND']

        conf = {
            'name': 'Bark App',
            'needs': 'BARK_KEY',
            'token': BARK_KEY,
            'text': 'code',
            'code': 200,
            'url': f'{BARK_KEY}/{text} {status}/{parse.quote(desp)}',
            'data': {
                'sound': BARK_SOUND
            }
        }

        return self.pushTemplate('get', conf['url'], params=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def tgBot(self, text, status, desp):
        TG_BOT_TOKEN = self.TG_BOT_TOKEN
        if 'TG_BOT_TOKEN' in os.environ:
            TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']

        TG_USER_ID = self.TG_USER_ID
        if 'TG_USER_ID' in os.environ:
            TG_USER_ID = os.environ['TG_USER_ID']

        token = ''
        if TG_BOT_TOKEN and TG_USER_ID:
            token = 'token'

        conf = {
            'name': 'Telegram Bot',
            'needs': 'TG_BOT_TOKEN 和 TG_USER_ID',
            'token': token,
            'text': 'ok',
            'code': 'error_code',
            'url': f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
            'data': {
                'chat_id': TG_USER_ID,
                'text': f'{text} {status}\n\n{desp}',
                'disable_web_page_preview': True
            }
        }

        return self.pushTemplate('post', conf['url'], data=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def ddBot(self, text, status, desp):
        DD_BOT_TOKEN = self.DD_BOT_TOKEN
        if 'DD_BOT_TOKEN' in os.environ:
            DD_BOT_TOKEN = os.environ['DD_BOT_TOKEN']

        DD_BOT_SECRET = self.DD_BOT_SECRET
        if 'DD_BOT_SECRET' in os.environ:
            DD_BOT_SECRET = os.environ['DD_BOT_SECRET']

        url = ''
        if DD_BOT_TOKEN:
            url = 'https://oapi.dingtalk.com/robot/send?' \
                f'access_token={DD_BOT_TOKEN}'
            if DD_BOT_SECRET:
                secret = DD_BOT_SECRET
                timestamp = int(round(time.time() * 1000))
                secret_enc = bytes(secret).encode('utf-8')
                string_to_sign = f'{timestamp}\n{secret}'
                string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
                hmac_code = hmac.new(
                    secret_enc, string_to_sign_enc,
                    digestmod=hashlib.sha256).digest()
                sign = parse.quote_plus(base64.b64encode(hmac_code))
                url = 'https://oapi.dingtalk.com/robot/send?access_' \
                    f'token={DD_BOT_TOKEN}&timestamp={timestamp}&sign={sign}'

        conf = {
            'name': '钉钉机器人',
            'needs': 'DD_BOT_TOKEN',
            'token': DD_BOT_TOKEN,
            'text': 'errcode',
            'code': 0,
            'url': url,
            'data': {
                'msgtype': 'text',
                'text': {
                    'content': f'{text} {status}\n\n{desp}'
                }
            }
        }

        return self.pushTemplate('post', conf['url'], data=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def wwBot(self, text, status, desp):
        WW_BOT_KEY = self.WW_BOT_KEY
        if 'WW_BOT_KEY' in os.environ:
            WW_BOT_KEY = os.environ['WW_BOT_KEY']

        conf = {
            'name': '企业微信机器人',
            'needs': 'WW_BOT_KEY',
            'token': WW_BOT_KEY,
            'text': 'errcode',
            'code': 0,
            'url': f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WW_BOT_KEY}',
            'data': {
                'msgtype': 'text',
                'text': {
                    'content': f'{text} {status}\n\n{desp}'
                }
            }
        }

        return self.pushTemplate('post', conf['url'], json=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def get_wwtoken(self):
        WW_ID = self.WW_ID
        if 'WW_ID' in os.environ:
            WW_ID = os.environ['WW_ID']

        WW_APP_SECRET = self.WW_APP_SECRET
        if 'WW_APP_SECRET' in os.environ:
            WW_APP_SECRET = os.environ['WW_APP_SECRET']

        if WW_ID and WW_APP_SECRET:
            url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
            data = {
                'corpid': WW_ID,
                'corpsecret': WW_APP_SECRET
            }

            try:
                response = req.to_python(
                    req.request('get', url, params=data).text)
                rspcode = response['errcode']
            except Exception as e:
                log.error(e)
            else:
                if rspcode == 0:
                    log.info('access_token 获取成功')
                    return response['access_token']
                else:
                    log.error(f'access_token 获取失败:\n{response}')
        else:
            log.info('企业微信应用 推送所需的 WW_ID 和 WW_APP_SECRET 未设置, 正在跳过...')

    def wwApp(self, text, status, desp):
        WW_APP_USERID = self.WW_APP_USERID
        if 'WW_APP_USERID' in os.environ:
            WW_APP_USERID = os.environ['WW_APP_USERID']

        WW_APP_AGENTID = self.WW_APP_AGENTID
        if 'WW_APP_AGENTID' in os.environ:
            WW_APP_AGENTID = os.environ['WW_APP_AGENTID']

        token = ''
        if WW_APP_USERID and WW_APP_AGENTID:
            token = 'token'
        access_token = self.get_wwtoken()

        if access_token:
            conf = {
                'name': '企业微信应用',
                'needs': 'WW_APP_USERID 和 WW_APP_AGENTID',
                'token': token,
                'text': 'errcode',
                'code': 0,
                'url': f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}',
                'data': {
                    'touser': WW_APP_USERID,
                    'msgtype': 'text',
                    'agentid': WW_APP_AGENTID,
                    'text': {
                        'content': f'{text} {status}\n\n{desp}'
                    }
                }
            }

            return self.pushTemplate('post', conf['url'], json=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def iGot(self, text, status, desp):
        IGOT_KEY = self.IGOT_KEY
        if 'IGOT_KEY' in os.environ:
            IGOT_KEY = os.environ['IGOT_KEY']

        conf = {
            'name': 'iGot',
            'needs': 'IGOT_KEY',
            'token': IGOT_KEY,
            'text': 'ret',
            'code': 0,
            'url': f'https://push.hellyw.com/{IGOT_KEY}',
            'data': {
                'title': f'{text} {status}',
                'content': desp
            }
        }

        return self.pushTemplate('post', conf['url'], data=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

    def pushPlus(self, text, status, desp):
        PUSH_PLUS_TOKEN = self.PUSH_PLUS_TOKEN
        if 'PUSH_PLUS_TOKEN' in os.environ:
            PUSH_PLUS_TOKEN = os.environ['PUSH_PLUS_TOKEN']

        PUSH_PLUS_USER = self.PUSH_PLUS_USER
        if 'PUSH_PLUS_USER' in os.environ:
            PUSH_PLUS_USER = os.environ['PUSH_PLUS_USER']

        conf = {
            'name': 'pushplus',
            'needs': 'PUSH_PLUS_TOKEN',
            'token': PUSH_PLUS_TOKEN,
            'text': 'code',
            'code': 200,
            'url': 'https://pushplus.hxtrip.com/send',
            'data': {
                'token': PUSH_PLUS_TOKEN,
                'title': f'{text} {status}',
                'content': desp,
                'topic': PUSH_PLUS_USER
            }
        }

        return self.pushTemplate('post', conf['url'], data=conf['data'], name=conf['name'], needs=conf['needs'], token=conf['token'], text=conf['text'], code=conf['code'])

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
        self.wwApp(app, status, msg)
        self.iGot(app, status, msg)
        self.pushPlus(app, status, msg)


if __name__ == '__main__':
    Notify().send(app='原神签到小助手', status='签到状态', msg='内容详情')
