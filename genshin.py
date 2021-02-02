'''
@File                : genshin.py
@Github              : https://github.com/y1ndan/genshin-impact-helper
@Last modified by    : y1ndan
@Last modified time  : 2021-02-02 14:10:30
'''
import hashlib
import json
import random
import string
import time
import uuid
import os

from settings import log, CONFIG, req
from notify import Notify


def version():
    return 'v1.6.11'

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
            'User-Agent': CONFIG.USER_AGENT,
            'Referer': CONFIG.REFERER_URL,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookie
        }
        return header


class Roles(Base):
    def get_awards(self):
        response = {}
        try:
            response = req.to_python(req.request(
                'get', CONFIG.AWARD_URL, headers=self.get_header()).text)
        except json.JSONDecodeError as e:
            raise Exception(e)

        return response

    def get_roles(self):
        log.info('准备获取账号信息...')
        response = {}
        try:
            response = req.to_python(req.request(
                'get', CONFIG.ROLE_URL, headers=self.get_header()).text)
            message = response['message']
        except Exception as e:
            raise Exception(e)
        if response.get(
            'retcode', 1) != 0 or response.get('data', None) is None:
            raise Exception(message)

        log.info('账号信息获取完毕')
        return response


class Sign(Base):
    def __init__(self, cookies: str = None):
        super(Sign, self).__init__(cookies)
        self._region_list = []
        self._region_name_list = []
        self._uid_list = []

    @staticmethod
    def get_ds():
        # v2.3.0-web @povsister & @journey-ad
        n = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = hexdigest('salt=' + n + '&t=' + i + '&r=' + r)
        return '{},{},{}'.format(i, r, c)

    def get_header(self):
        header = super(Sign, self).get_header()
        header.update({
            'x-rpc-device_id':str(uuid.uuid3(
                uuid.NAMESPACE_URL, self._cookie)).replace('-', '').upper(),
            # 1:  ios
            # 2:  android
            # 4:  pc web
            # 5:  mobile web
            'x-rpc-client_type': '5',
            'x-rpc-app_version': CONFIG.APP_VERSION,
            'DS': self.get_ds(),
        })
        return header

    def get_info(self):
        user_game_roles = Roles(self._cookie).get_roles()
        role_list = user_game_roles.get('data', {}).get('list', [])

        # role list empty
        if not role_list:
            raise Exception(user_game_roles.get('message', 'Role list empty'))

        log.info(f'当前账号绑定了 {len(role_list)} 个角色')
        info_list = []
        # cn_gf01:  天空岛
        # cn_qd01:  世界树
        self._region_list = [(i.get('region', 'NA')) for i in role_list]
        self._region_name_list = [(i.get('region_name', 'NA'))
            for i in role_list]
        self._uid_list = [(i.get('game_uid', 'NA')) for i in role_list]

        log.info('准备获取签到信息...')
        for i in range(len(self._uid_list)):
            info_url = CONFIG.INFO_URL.format(
                self._region_list[i], CONFIG.ACT_ID, self._uid_list[i])
            try:
                content = req.request(
                    'get', info_url, headers=self.get_header()).text
                info_list.append(req.to_python(content))
            except Exception as e:
                raise Exception(e)

        if not info_list:
            raise Exception('User sign info list is empty')
        log.info('签到信息获取完毕')
        return info_list

    def run(self):
        info_list = self.get_info()
        message_list = []
        for i in range(len(info_list)):
            today = info_list[i]['data']['today']
            total_sign_day = info_list[i]['data']['total_sign_day']
            awards = Roles(self._cookie).get_awards()['data']['awards']
            uid = str(self._uid_list[i]).replace(
                str(self._uid_list[i])[1:8], '******', 1)

            log.info(f'准备为旅行者 {i + 1} 号签到...')
            time.sleep(10)
            message = {
                'today': today,
                'region_name': self._region_name_list[i],
                'uid': uid,
                'total_sign_day': total_sign_day,
                'end': '',
            }
            if info_list[i]['data']['is_sign'] is True:
                message['award_name'] = awards[total_sign_day - 1]['name']
                message['award_cnt'] = awards[total_sign_day - 1]['cnt']
                message['status'] = f'👀 旅行者 {i + 1} 号, 你已经签到过了哦'
                message_list.append(self.message.format(**message))
                continue
            else:
                message['award_name'] = awards[total_sign_day]['name']
                message['award_cnt'] = awards[total_sign_day]['cnt']
            if info_list[i]['data']['first_bind'] is True:
                message['status'] = f'💪 旅行者 {i + 1} 号, 请先前往米游社App手动签到一次'
                message_list.append(self.message.format(**message))
                continue

            data = {
                'act_id': CONFIG.ACT_ID,
                'region': self._region_list[i],
                'uid': self._uid_list[i]
            }

            try:
                response = req.to_python(req.request(
                    'post', CONFIG.SIGN_URL, headers=self.get_header(),
                    data=json.dumps(data, ensure_ascii=False)).text)
            except Exception as e:
                raise Exception(e)
            code = response.get('retcode', 99999)
            # 0:      success
            # -5003:  already signed in
            if code != 0:
                message_list.append(response)
                continue
            message['total_sign_day'] = total_sign_day + 1
            message['status'] = response['message']
            message_list.append(self.message.format(**message))
        log.info('签到完毕')

        return ''.join(message_list)

    @property
    def message(self):
        return CONFIG.MESSGAE_TEMPLATE


if __name__ == '__main__':
    log.info(f'🌀原神签到小助手 {version()}')   
    log.info('若签到失败, 请尝试更新!')
    log.info('任务开始')
    notify = Notify()
    msg_list = []
    ret = success_num = fail_num = 0
    """miHoYo BBS COOKIE
    :param COOKIE: 米游社的COOKIE.多个账号的COOKIE值之间用 # 号隔开,例如: 1#2#3#4
    """
    # Github Actions用户请到Repo的Settings->Secrets里设置变量,变量名字必须与上述参数变量名字完全一致,否则无效!!!
    # Name=<变量名字>,Value=<获取的值>
    COOKIE = ''

    if os.environ.get('COOKIE', '') != '':
        COOKIE = os.environ['COOKIE']

    cookie_list = COOKIE.split('#')
    log.info(f'检测到共配置了 {len(cookie_list)} 个帐号')
    for i in range(len(cookie_list)):
        log.info(f'准备为 NO.{i + 1} 账号签到...')
        try:
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

