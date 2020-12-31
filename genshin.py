#!/usr/bin/env python3

import requests
import json
import uuid
import logging
import time
import random
import hashlib
import string
from requests.exceptions import *

logging.basicConfig(
  level = logging.INFO,
  format = '%(asctime)s %(levelname)s %(message)s',
  datefmt = '%Y-%m-%dT%H:%M:%S')


class ConfMeta(type):
  @property
  def ref_url(self):
    return 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?' \
    'bbs_auth_required={}&act_id={}&utm_source={}&utm_medium={}&' \
    'utm_campaign={}'.format('true', self.act_id, 'bbs', 'mys', 'icon')

  @property
  def award_url(self):
    return 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?' \
    'act_id={}'.format(self.act_id)

  @property
  def role_url(self):
    return 'https://api-takumi.mihoyo.com/binding/api/' \
    'getUserGameRolesByCookie?game_biz={}'.format('hk4e_cn')

  @property
  def info_url(self):
    return 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?' \
    'region={}&act_id={}&uid={}'

  @property
  def sign_url(self):
    return 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

  @property
  def app_version(self):
    return '2.2.1'

  @property
  def ua(self):
    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) Apple' \
    'WebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.2.0'

  @property
  def act_id(self):
    return 'e202009291139501'


class Conf(metaclass=ConfMeta):
  pass


class Roles(object):
  def __init__(self, cookie:str=None):
    if type(cookie) is not str:
      raise TypeError('%s want a %s but got %s' %(
        self.__class__, type(__name__), type(cookie)))
    self._cookie = cookie

  def get_header(self):
    return {
      'User-Agent': Conf.ua,
      'Referer': Conf.ref_url,
      'Accept-Encoding': 'gzip, deflate, br',
      'Cookie': self._cookie
    }

  def get_awards(self):
    try:
      jdict = json.loads(
              requests.Session().get(
                Conf.award_url, headers = self.get_header()).text)
    except Exception as e:
      logging.error(e)

    return jdict

  def get_roles(self):
    logging.info('准备获取账号信息...')
    errstr = None

    for i in range(1, 4):
      try:
        jdict = json.loads(requests.Session().get(
          Conf.role_url, headers = self.get_header()).text)
      except HTTPError as e:
        logging.error('HTTP error when get user game roles, ' \
        'retry %s time(s) ...' %(i))
        logging.error('error is %s' %(e))
        errstr = str(e)
        continue
      except KeyError as e:
        logging.error('Wrong response to get user game roles, ' \
        'retry %s time(s) ...' %(i))
        logging.error('response is %s' %(e))
        errstr = str(e)
        continue
      except Exception as e:
        logging.error('Unknown error %s, die' %(e))
        errstr = str(e)
        raise
      else:
        break

    try:
      jdict
    except AttributeError:
      raise Exception(errstr)

    return jdict


class Sign(object):
  def __init__(self, cookie:str=None):
    if type(cookie) is not str:
      raise TypeError('%s want a %s but got %s' %(
        self.__class__, type(__name__), type(cookie)))
    self._cookie = cookie

  # Provided by Steesha
  def md5(self, text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

  def get_DS(self):
    # n = self.md5(Conf.app_version) # V2.1.0
    n = 'cx2y9z9a29tfqvr1qsq6c7yz99b5jsqt'
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = self.md5('salt=' + n + '&t='+ i + '&r=' + r)
    return '{},{},{}'.format(i, r, c)

  def get_header(self):
    return {
      'x-rpc-device_id': str(uuid.uuid3(
        uuid.NAMESPACE_URL, self._cookie)).replace('-','').upper(),
      # 1:  ios
      # 2:  android
      # 4:  pc web
      # 5:  mobile web
      'x-rpc-client_type': '5',
      'Accept-Encoding': 'gzip, deflate, br',
      'User-Agent': Conf.ua,
      'Referer': Conf.ref_url,
      'x-rpc-app_version': Conf.app_version,
      'DS': self.get_DS(),
      'Cookie': self._cookie
    }

  def get_info(self):
    roles = Roles(self._cookie).get_roles()
    try:
      rolesList = roles['data']['list']
    except Exception as e:
      message = roles['message']
      notify(sckey, '失败', message)
      exit(-1)
    else:
      logging.info('当前账号绑定了 {} 个角色'.format(len(rolesList)))
      infoList = []
      # cn_gf01:  天空岛
      # cn_qd01:  世界树
      self._regionList = [(i.get('region', 'NA')) for i in rolesList]
      self._regionNameList = [(i.get('region_name', 'NA')) for i in rolesList]
      self._uidList = [(i.get('game_uid', 'NA')) for i in rolesList]

      logging.info('准备获取签到信息...')
      for i in range(len(self._uidList)):
        info_url = Conf.info_url.format(self._regionList[i], 
        Conf.act_id, self._uidList[i])
        try:
          infoList.append(json.loads(requests.Session().get(
            info_url, headers = self.get_header()).text))
        except Exception as e:
          logging.error(e)

      return infoList

  def run(self):
    logging.info('任务开始')
    messageList = []
    infoList = self.get_info()
    for i in range(len(infoList)):
      if infoList[i]['data']['is_sign'] is True:
      #if infoList[i]['data']['is_sign'] is False:
        message = '旅行者 {} 号,你已经签到过了'.format(i + 1)
        notify(sckey, '成功', message)
      elif infoList[i]['data']['first_bind'] is True:
        message = '旅行者 {} 号,请先前往米游社绑定账号'.format(i + 1)
        notify(sckey, '失败', message)
        exit(-1)
      else:
        today = infoList[i]['data']['today']
        totalSignDay = infoList[i]['data']['total_sign_day']
        award = Roles(self._cookie).get_awards()['data']['awards'][totalSignDay - 1]
        uid = str(self._uidList[i]).replace(
          str(self._uidList[i])[3:6], '***', 1)
        data = {
          'act_id': Conf.act_id,
          'region': self._regionList[i],
          'uid': self._uidList[i]
        }

        logging.info('准备为旅行者 {} 号签到...' \
        '\nRegion: {}\nUID: {}'.format(i + 1, self._regionNameList[i], uid))
        try:
          jdict = json.loads(requests.Session().post(
            Conf.sign_url, headers = self.get_header(),
            data = json.dumps(data, ensure_ascii=False)).text)
        except Exception as e:
          raise
        else:
          code = jdict['retcode']
          # 0:      success
          # -5003:  already signed in
          if code == 0:
            status = '成功'
            messageList.append(self.message().format(today, 
            self._regionNameList[i], uid, award['name'], award['cnt'], 
            totalSignDay, jdict['message'], ''))
          else:
            status = '失败'
            messageList = jdict

        return notify(sckey, status, messageList)

  def message(self):
    return '''
    {:#^30}
    🔅[{}]{}
    今日奖励: {} × {}
    本月累签: {} 天
    签到结果: {}
    {:#^30}
    '''


def notify(sckey, status, message):
  if sckey.startswith('SC'):
    logging.info('准备推送通知...')
    url = 'https://sc.ftqq.com/{}.send'.format(sckey)
    data = {'text': '原神签到小助手 签到{}'.format(status), 'desp': message}
    try:
      jdict = json.loads(
              requests.Session().post(url, data = data).text)
    except Exception as e:
      logging.error(e)
      raise HTTPError
    else:
      errmsg = jdict['errmsg']
      if errmsg == 'success':
        logging.info('推送成功')
      else:
        logging.error('{}: {}'.format('推送失败', jdict))
  else:
    logging.info('未配置SCKEY,正在跳过推送')

  logging.info('签到{}: {}'.format(status, message)) 
  return logging.info('任务结束')


if __name__ == '__main__':
  secret = input().strip().split('#')
  secret.append('')
  cookie = secret[0]
  sckey = secret[1]
  seconds = random.randint(10, 300)
  #seconds = random.randint(1, 3)

  logging.info('将在 {} 秒后开始任务...'.format(seconds))
  time.sleep(seconds)

  Sign(cookie).run()

