import hashlib
import json
import random
import string
import time
import uuid

import requests
from requests.exceptions import *

from settings import *


def hexdigest(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


class Base(object):
    def __init__(self, cookies: str = None):
        if not isinstance(cookies, str):
            raise TypeError('%s want a %s but got %s' % (
                self.__class__, type(__name__), type(cookies)))
        self._cookie = cookies

    def get_header(self):
        header = {
            'User-Agent': CONFIG.USER_AGENT,
            'Referer': CONFIG.REFERER_URL,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookie
        }
        return header

    @staticmethod
    def to_python(json_str: str):
        return json.loads(json_str)

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)


class Roles(Base):
    def get_awards(self):
        response = dict
        try:
            content = requests.Session().get(CONFIG.AWARD_URL, headers=self.get_header()).text
            response = self.to_python(content)
        except json.JSONDecodeError as e:
            log.error(e)

        return response

    def get_roles(self, max_attempt_number: int = 4):
        log.info('准备获取账号信息...')
        error = None
        response = dict()

        for i in range(1, max_attempt_number):
            try:
                content = requests.Session().get(CONFIG.ROLE_URL, headers=self.get_header()).text
                response = self.to_python(content)
            except HTTPError as error:
                log.error('HTTP error when get user game roles, retry %s time(s) ...' % i)
                log.error('error is %s' % error)
                continue
            except KeyError as error:
                log.error('Wrong response to get user game roles, retry %s time(s) ...' % i)
                log.error('response is %s' % error)
                continue
            except Exception as error:
                log.error('Unknown error %s, die' % error)
                raise error
            error = None
            break

        if error:
            log.error('Maximum retry times have been reached, error is %s ' % error)
            raise error
        if response.get('retcode', 1) != 0 or response.get('data', None) is None:
            log.error(response)
            exit(-1)

        log.info("账号信息获取完毕")
        return response


class Sign(Base):
    def __init__(self, cookies: str = None):
        super(Sign, self).__init__(cookies)
        self._region_list = []
        self._region_name_list = []
        self._uid_list = []

    @staticmethod
    def get_ds():
        n = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'  # v2.3.0 web @povsister & @journey-ad
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = hexdigest('salt=' + n + '&t=' + i + '&r=' + r)
        return '{},{},{}'.format(i, r, c)

    def get_header(self):
        header = super(Sign, self).get_header()
        header.update({
            'x-rpc-device_id': str(uuid.uuid3(uuid.NAMESPACE_URL, self._cookie)).replace('-', '').upper(),
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
            notify(sc_secret, '失败', user_game_roles.get('message', 'role list empty'))
            exit(-1)

        log.info('当前账号绑定了 {} 个角色'.format(len(role_list)))
        info_list = []
        # cn_gf01:  天空岛
        # cn_qd01:  世界树
        self._region_list = [(i.get('region', 'NA')) for i in role_list]
        self._region_name_list = [(i.get('region_name', 'NA')) for i in role_list]
        self._uid_list = [(i.get('game_uid', 'NA')) for i in role_list]

        log.info('准备获取签到信息...')
        for i in range(len(self._uid_list)):
            info_url = CONFIG.INFO_URL.format(self._region_list[i], CONFIG.ACT_ID, self._uid_list[i])
            try:
                content = requests.Session().get(info_url, headers=self.get_header()).text
                info_list.append(self.to_python(content))
            except Exception as e:
                log.error(e)

        if not info_list:
            log.error("user sign info list is empty, exit...")
            exit(-1)
        log.info("签到信息获取完毕")
        return info_list

    def run(self):
        log.info('任务开始')
        status = "成功"
        messages = {
            'success': [],
            'failed': [],
            'already_signed_in': [],
        }

        info_list = self.get_info()
        for i in range(len(info_list)):
            today = info_list[i]['data']['today']
            total_sign_day = info_list[i]['data']['total_sign_day']
            award = Roles(self._cookie).get_awards()['data']['awards']
            uid = str(self._uid_list[i]).replace(str(self._uid_list[i])[3:6], '***', 1)

            # 已经签到, 处理下一个用户
            if info_list[i]['data']['is_sign'] is True:
                messages.get('already_signed_in', []).append("旅行者 {} 号, 你已经签到过了".format(i + 1))
                continue
            if info_list[i]['data']['first_bind'] is True:
                messages.get('failed', []).append("旅行者 {} 号, 请先前往米游社App手动签到一次".format(i + 1))
                exit(-1)

            data = {
                'act_id': CONFIG.ACT_ID,
                'region': self._region_list[i],
                'uid': self._uid_list[i]
            }

            log.info('准备为旅行者 {} 号签到... {}'.format(i + 1, self.to_json({
                'Region': self._region_name_list[i],
                'UID': uid
            })))
            try:
                content = requests.Session().post(
                    CONFIG.SIGN_URL,
                    headers=self.get_header(),
                    data=json.dumps(data, ensure_ascii=False)).text
                response = self.to_python(content)
            except Exception as e:
                raise e
            code = response.get('retcode', 99999)
            # 0:      success
            # -5003:  already signed in
            if code == 0:
                message = self.message.format(
                        today,
                        self._region_name_list[i],
                        uid,
                        award['name'],
                        award['cnt'],
                        total_sign_day + 1,
                        response['message'],
                        ''
                )
                messages.get('success', []).append(message)
            else:
                messages.get('failed', []).append(response)

        if messages.get('failed', []):
            status = "失败"

        return notify(sc_secret, status, messages)

    @property
    def message(self):
        return '''
        {:#^30}
        🔅[{}]{}
        今日奖励: {} × {}
        本月累签: {} 天
        签到结果: {}
        {:#^30}
        '''


def notify(secret: str, status: str, message):
    if secret.startswith('SC'):
        log.info('准备推送通知...')
        url = 'https://sc.ftqq.com/{}.send'.format(secret)
        data = {'text': '原神签到小助手 签到{}'.format(status), 'desp': message}
        try:
            response = Sign.to_python(requests.Session().post(url, data=data).text)
        except Exception as e:
            log.error(e)
            raise HTTPError
        else:
            errmsg = response['errmsg']
            if errmsg == 'success':
                log.info('推送成功')
            else:
                log.error('{}: {}'.format('推送失败', response))
    else:
        log.info('未配置SCKEY,正在跳过推送')
    if isinstance(message, list) or isinstance(message, dict):
        message = Sign.to_json(message)
    log.info('签到{}: {}'.format(status, message))
    return log.info('任务结束')


if __name__ == '__main__':
    secret = input().strip().split('#')
    secret.append('')
    cookie = secret[0]
    sc_secret = secret[1]

    Sign(cookie).run()
