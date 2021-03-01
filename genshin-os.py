import hashlib
import json
import time
import os

from settings import log, CONFIG, req
from notify import Notify


def hexdigest(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


class Base(object):
    def __init__(self, cookies: str = None):
        if not isinstance(cookies, str):
            raise TypeError('%s want a %s but got %s' %
                            (self.__class__, type(__name__), type(cookies)))
        self._cookie = cookies

    def get_header(self):
        header = {
            'User-Agent': CONFIG.WB_USER_AGENT,
            'Referer': CONFIG.OS_REFERER_URL,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookie
        }
        return header


class Roles(Base):
    def get_awards(self):
        response = {}
        try:
            response = req.to_python(req.request(
                'get', CONFIG.OS_REWARD_URL, headers=self.get_header()).text)
        except json.JSONDecodeError as e:
            raise Exception(e)

        return response


class Sign(Base):
    def __init__(self, cookies: str = None):
        super(Sign, self).__init__(cookies)
        self.uid = uid

    def get_header(self):
        header = super(Sign, self).get_header()
        return header

    def get_info(self):
        log.info('准备获取签到信息...')
        info_url = CONFIG.OS_INFO_URL
        try:
            response = req.request(
                'get', info_url, headers=self.get_header()).text
        except Exception as e:
            raise Exception(e)

        log.info('签到信息获取完毕')
        return req.to_python(response)

    def run(self):
        info_list = self.get_info()
        message_list = []
        if info_list:
            today = info_list.get('data',{}).get('today')
            total_sign_day = info_list.get('data',{}).get('total_sign_day')
            awards = Roles(self._cookie).get_awards().get('data',{}).get('awards')
            uid = str(self.uid).replace(
                str(self.uid)[1:7], '******', 1)

            log.info(f'准备为旅行者 {uid} 签到...')
            time.sleep(10)
            message = {
                'today': today,
                'region_name': '',
                'uid': uid,
                'total_sign_day': total_sign_day,
                'end': '',
            }
            if info_list.get('data',{}).get('is_sign') is True:
                message['award_name'] = awards[total_sign_day - 1]['name']
                message['award_cnt'] = awards[total_sign_day - 1]['cnt']
                message['status'] = f"👀 Traveler, you've already checked in today"
                message_list.append(self.message.format(**message))
                return ''.join(message_list)
            else:
                message['award_name'] = awards[total_sign_day]['name']
                message['award_cnt'] = awards[total_sign_day]['cnt']
            if info_list.get('data',{}).get('first_bind') is True:
                message['status'] = f'💪 Please check in manually once'
                message_list.append(self.message.format(**message))
                return ''.join(message_list)

            data = {
                'act_id': CONFIG.OS_ACT_ID
            }

            try:
                response = req.to_python(req.request(
                    'post', CONFIG.OS_SIGN_URL, headers=self.get_header(),
                    data=json.dumps(data, ensure_ascii=False)).text)
            except Exception as e:
                raise Exception(e)
            code = response.get('retcode', 99999)
            # 0:      success
            # -5003:  already checked in
            if code != 0:
                message_list.append(response)
                return ''.join(message_list)
            message['total_sign_day'] = total_sign_day + 1
            message['status'] = response['message']
            message_list.append(self.message.format(**message))
        log.info('签到完毕')

        return ''.join(message_list)

    @property
    def message(self):
        return CONFIG.MESSAGE_TEMPLATE


if __name__ == '__main__':
    log.info(f'🌀Genshin Impact Helper v{CONFIG.GIH_VERSION}')
    log.info('If you fail to check in, please try to update!')
    log.info('任务开始')
    notify = Notify()
    msg_list = []
    ret = success_num = fail_num = 0
    """HoYoLAB Community's COOKIE
    :param OS_COOKIE: 米游社国际版的COOKIE.多个账号的COOKIE值之间用 # 号隔开,例如: 1#2#3#4
    """
    # Github Actions用户请到Repo的Settings->Secrets里设置变量,变量名字必须与上述参数变量名字完全一致,否则无效!!!
    # Name=<变量名字>,Value=<获取的值>
    OS_COOKIE = ''

    if os.environ.get('OS_COOKIE', '') != '':
        OS_COOKIE = os.environ['OS_COOKIE']

    cookie_list = OS_COOKIE.split('#')
    log.info(f'检测到共配置了 {len(cookie_list)} 个帐号')
    for i in range(len(cookie_list)):
        log.info(f'准备为 NO.{i + 1} 账号签到...')
        try:
            ltoken = cookie_list[i].split('ltoken=')[1].split(';')[0]
            uid = cookie_list[i].split('account_id=')[1].split(';')[0]
            msg = f'	NO.{i + 1} 账号:{Sign(cookie_list[i]).run()}'
            msg_list.append(msg)
            success_num = success_num + 1
        except Exception as e:
            msg = f'	NO.{i + 1} 账号:\n    {e}'
            msg_list.append(msg)
            fail_num = fail_num + 1
            log.error(msg)
            ret = -1
        continue
    notify.send(status=f'成功: {success_num} | 失败: {fail_num}', msg=msg_list)
    if ret != 0:
        log.error('异常退出')
        exit(ret)
    log.info('任务结束')

