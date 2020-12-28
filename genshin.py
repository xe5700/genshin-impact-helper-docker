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
  def check_url(self):
    return 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?' \
    'region={}&act_id={}&uid={}'

  @property
  def sign_url(self):
    return 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

  @property
  def app_version(self):
    return '2.1.0'

  @property
  def ua(self):
    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) Apple' \
    'WebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/{}'.format(self.app_version)

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

  def get_roles(self):
    logging.info('Start getting user information ...')
    errstr = None

    for i in range(1, 4):
      try:
        jdict = json.loads(
              requests.Session().get(
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
    n = self.md5(Conf.app_version)
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

  def run(self):
    # cn_gf01:  天空岛
    # cn_qd01:  世界树
    self._region = rolesList[i]['region']
    self._region_name = rolesList[i]['region_name']
    self._uid = rolesList[i]['game_uid']

    data = {
      'act_id': Conf.act_id,
      'region': self._region,
      'uid': self._uid
    }

    logging.info('Start signing in the NO.%s role which UID is %s in %s ...' %(
      i+1, str(self._uid).replace(str(self._uid)[3:6],'***',1), self._region_name))
    try:
      jdict = json.loads(requests.Session().post(
        Conf.sign_url, headers = self.get_header(),
        data = json.dumps(data, ensure_ascii=False)).text)
    except Exception as e:
      raise

    return jdict


def makeResult(result:str, data=None):
  return json.dumps(
    {
      'result': result,
      'message': data
    },
    sort_keys=False, indent=2, ensure_ascii=False
  )

def notify(sckey, massage):
  if sckey != '':
    logging.info('正在推送通知...')
    url = 'https://sc.ftqq.com/{}.send'.format(sckey)
    data = {'text':'原神签到小助手', 'desp':massage}
    try:
      jdict = json.loads(
              requests.Session().post(url, data = data).text)
      errmsg = jdict['errmsg']
      if errmsg == 'success':
        logging.info('推送成功')
      else:
        logging.error('推送失败')
        logging.error(jdict)
    except Exception as e:
      logging.error(e)
      raise HTTPError

    return jdict
  else:
    logging.info('未配置SCKEY,正在跳过推送...')


if __name__ == '__main__':
  secret = input().strip().split('#')
  secret.append('')
  cookie = secret[0]
  sckey = secret[1]
  jstr = Roles(cookie).get_roles()
  result = makeResult('Failed', jstr)
  ret = -1

  try:
    rolesList = jstr['data']['list']
    logging.info('Your account has been bound %s role(s)' %(len(rolesList)))

    for i in range(len(rolesList)):
      seconds = random.randint(10, 300)
      logging.info('Sleep for %s seconds ...' %(seconds))
      time.sleep(seconds)

      try:
        jdict = Sign(cookie).run()
        jstr = json.dumps(jdict, ensure_ascii=False)
        code = jdict['retcode']
      except Exception as e:
        jstr = str(e)

      try:
        code
      except NameError:
        code = -1

      # 0:      success
      # -5003:  already signed in
      if code in [0, -5003]:
        result = makeResult('Success', jstr)
        ret = 0

      logging.info(result)

  except Exception as e:
    logging.info(result)

  notify(sckey, result)
  logging.info('签到完成!')
  exit(ret)
