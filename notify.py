'''
@File                : notify.py
@Github              : https://github.com/y1ndan/genshin-impact-helper
@Last modified by    : y1ndan
@Last modified time  : 2021-02-02 18:39:15
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
    :param PUSH_CONFIG: JSON格式的自定义推送配置.
        格式:
            {"method":"post","url":"","data":{},"text":"","code":200,"data_type":"data","show_title_and_desp":false,"set_data_title":"","set_data_sub_title":"","set_data_desp":""}
        说明:
            method: 必填,请求方式.默认: post.
            url: 必填,完整的自定义推送链接.
            data: 选填,发送的data.默认为空,可自行添加额外参数.
            text: 必填,响应体返回的状态码的key.例如: server酱的为errno.
            code: 必填,响应体返回的状态码的value.例如: server酱的为0.
            data_type: 选填,发送data的方式,可选params|json|data,默认: data.
            show_title_and_desp: 选填,是否将标题(应用名+运行状态)和运行结果合并.默认: false.
            set_data_title: 必填,填写推送方式data中消息标题的key.例如: server酱的为text.
            set_data_sub_title: 选填,填写推送方式data中消息正文的key.有的推送方式正文的key有次级结构,
                需配合set_data_title构造子级,与set_data_desp互斥.
                例如: 企业微信中,set_data_title填text,set_data_sub_title填content.
            set_data_desp: 选填,填写推送方式data中消息正文的key.例如: server酱的为desp.
                与set_data_sub_title互斥,两者都填则本项不生效.
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
    # Custom Push Config
    PUSH_CONFIG = ''

    def pushTemplate(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        name = kwargs.get('name')
        # needs = kwargs.get('needs')
        token = kwargs.get('token')
        text = kwargs.get('text')
        code = kwargs.get('code')
        if not token:
            log.info(f'{name} 🚫')
            # log.info(f'{name} 推送所需的 {needs} 未设置, 正在跳过...')
            return
        try:
            response = req.to_python(req.request(
                method, url, 2, params, data, json, headers).text)
            rspcode = response[text]
        except Exception as e:
            # 🚫: disabled; 🥳:success; 😳:fail
            log.error(f'{name} 😳\n{e}')
        else:
            if rspcode == code:
                log.info(f'{name} 🥳')
            # Telegram Bot
            elif name == 'Telegram Bot' and rspcode:
                log.info(f'{name} 🥳')
            elif name == 'Telegram Bot' and response[code] == 400:
                log.error(f'{name} 😳\n请主动给 bot 发送一条消息并检查 TG_USER_ID 是否正确')
            elif name == 'Telegram Bot' and response[code] == 401:
                log.error(f'{name} 😳\nTG_BOT_TOKEN 错误')
            else:
                log.error(f'{name} 😳\n{response}')

    def serverChan(self, text, status, desp):
        SCKEY = self.SCKEY
        if 'SCKEY' in os.environ:
            SCKEY = os.environ['SCKEY']

        url = f'https://sc.ftqq.com/{SCKEY}.send'
        data = {
            'text': f'{text} {status}',
            'desp': desp
        }
        conf = ['Server酱', 'SCKEY', SCKEY, 'errno', 0]
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, data=data, name=name, needs=needs, token=token, text=text, code=code)

    def coolPush(self, text, status, desp):
        COOL_PUSH_SKEY = self.COOL_PUSH_SKEY
        if 'COOL_PUSH_SKEY' in os.environ:
            COOL_PUSH_SKEY = os.environ['COOL_PUSH_SKEY']

        COOL_PUSH_MODE = self.COOL_PUSH_MODE
        if 'COOL_PUSH_MODE' in os.environ:
            COOL_PUSH_MODE = os.environ['COOL_PUSH_MODE']

        url = f'https://push.xuthus.cc/{COOL_PUSH_MODE}/{COOL_PUSH_SKEY}'
        data = f'{text} {status}\n\n{desp}'.encode('utf-8')
        conf = ['Cool Push', 'COOL_PUSH_SKEY', COOL_PUSH_SKEY, 'code', 200]
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, data=data, name=name, needs=needs, token=token, text=text, code=code)

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
        elif BARK_KEY and BARK_KEY.find(
            'https') == -1 and BARK_KEY.find('http') == -1:
            BARK_KEY = f'https://api.day.app/{BARK_KEY}'

        BARK_SOUND = self.BARK_SOUND
        if 'BARK_SOUND' in os.environ:
            BARK_SOUND = os.environ['BARK_SOUND']

        url = f'{BARK_KEY}/{text} {status}/{parse.quote(desp)}'
        data = {
            'sound': BARK_SOUND
        }
        conf = ['Bark App', 'BARK_KEY', BARK_KEY, 'code', 200]
        name, needs, token, text, code  = conf

        return self.pushTemplate('get', url, params=data, name=name, needs=needs, token=token, text=text, code=code)

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

        url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
        data = {
            'chat_id': TG_USER_ID,
            'text': f'{text} {status}\n\n{desp}',
            'disable_web_page_preview': True
        }
        conf = ['Telegram Bot', 'TG_BOT_TOKEN 和 TG_USER_ID', token, 'ok', 'error_code']
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, data=data, name=name, needs=needs, token=token, text=text, code=code)

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

        data = {
            'msgtype': 'text',
            'text': {
                'content': f'{text} {status}\n\n{desp}'
            }
        }
        conf = ['钉钉机器人', 'DD_BOT_TOKEN', DD_BOT_TOKEN, 'errcode', 0]
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, data=data, name=name, needs=needs, token=token, text=text, code=code)

    def wwBot(self, text, status, desp):
        WW_BOT_KEY = self.WW_BOT_KEY
        if 'WW_BOT_KEY' in os.environ:
            WW_BOT_KEY = os.environ['WW_BOT_KEY']

        url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WW_BOT_KEY}'
        data = {
            'msgtype': 'text',
            'text': {
                'content': f'{text} {status}\n\n{desp}'
            }
        }
        conf = ['企业微信机器人', 'WW_BOT_KEY', WW_BOT_KEY, 'errcode', 0]
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, json=data, name=name, needs=needs, token=token, text=text, code=code)

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
            log.info('企业微信应用 🚫')
            # log.info('企业微信应用 推送所需的 WW_ID 和 WW_APP_SECRET 未设置, 正在跳过...')

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
            url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
            data = {
                'touser': WW_APP_USERID,
                'msgtype': 'text',
                'agentid': WW_APP_AGENTID,
                'text': {
                    'content': f'{text} {status}\n\n{desp}'
                }
            }
            conf = ['企业微信应用', 'WW_APP_USERID 和 WW_APP_AGENTID', token, 'errcode', 0]
            name, needs, token, text, code  = conf

            return self.pushTemplate('post', url, json=data, name=name, needs=needs, token=token, text=text, code=code)

    def iGot(self, text, status, desp):
        IGOT_KEY = self.IGOT_KEY
        if 'IGOT_KEY' in os.environ:
            IGOT_KEY = os.environ['IGOT_KEY']

        url = f'https://push.hellyw.com/{IGOT_KEY}'
        data = {
            'title': f'{text} {status}',
            'content': desp
        }
        conf = ['iGot', 'IGOT_KEY', IGOT_KEY, 'ret', 0]
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, data=data, name=name, needs=needs, token=token, text=text, code=code)

    def pushPlus(self, text, status, desp):
        PUSH_PLUS_TOKEN = self.PUSH_PLUS_TOKEN
        if 'PUSH_PLUS_TOKEN' in os.environ:
            PUSH_PLUS_TOKEN = os.environ['PUSH_PLUS_TOKEN']

        PUSH_PLUS_USER = self.PUSH_PLUS_USER
        if 'PUSH_PLUS_USER' in os.environ:
            PUSH_PLUS_USER = os.environ['PUSH_PLUS_USER']

        url = 'https://pushplus.hxtrip.com/send'
        data = {
            'token': PUSH_PLUS_TOKEN,
            'title': f'{text} {status}',
            'content': desp,
            'topic': PUSH_PLUS_USER
        }
        conf = ['pushplus', 'PUSH_PLUS_TOKEN', PUSH_PLUS_TOKEN, 'code', 200]
        name, needs, token, text, code  = conf

        return self.pushTemplate('post', url, data=data, name=name, needs=needs, token=token, text=text, code=code)

    def custPush(self, text, status, desp):
        PUSH_CONFIG = self.PUSH_CONFIG
        if 'PUSH_CONFIG' in os.environ:
            PUSH_CONFIG = os.environ['PUSH_CONFIG']

        if not PUSH_CONFIG:
            return log.info(f'自定义推送 🚫')
        cust = req.to_python(PUSH_CONFIG)
        title = f'{text} {status}'
        if cust['show_title_and_desp']:
            title = f'{text} {status}\n\n{desp}'
        if cust['set_data_title'] and cust['set_data_sub_title']:
            cust['data'][cust['set_data_title']] = {
                cust['set_data_sub_title']: title
            }
        elif cust['set_data_title'] and cust['set_data_desp']:
            cust['data'][cust['set_data_title']] = title
            cust['data'][cust['set_data_desp']] = desp
        elif cust['set_data_title']:
            cust['data'][cust['set_data_title']] = title
        conf = [cust['url'], cust['data'], '自定义推送', cust['text'], cust['code']]
        url, data, name, text, code  = conf

        if cust['method'].upper() == 'GET':
            return self.pushTemplate('get', url, params=data, name=name, token='token', text=text, code=code)
        elif cust['method'].upper() == 'POST' and cust['data_type'].lower() == 'json':
            return self.pushTemplate('post', url, json=data, name=name, token='token', text=text, code=code)
        else:
            return self.pushTemplate('post', url, data=data, name=name, token='token', text=text, code=code)

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
        self.custPush(app, status, msg)


if __name__ == '__main__':
    Notify().send(app='原神签到小助手', status='签到状态', msg='内容详情')

