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
  def index_url(self):
    return 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html'

  @property
  def app_version(self):
    return '2.1.0'

  @property
  def ua(self):
    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) ' \
           'AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/%s' %(self.app_version)


class Conf(metaclass=ConfMeta):
  pass


class Roles(object):
  def __init__(self, cookie:str=None):
    if type(cookie) is not str:
      raise TypeError("%s want a %s but got %s" %(
          self.__class__, type(__name__), type(cookie)))

    self._cookie = cookie
    self._url = "https://api-takumi.mihoyo.com/binding/api/" \
                "getUserGameRolesByCookie?game_biz=%s" %('hk4e_cn')

  def get_header(self):
    actid = 'e202009291139501'
    ref = "%s?bbs_auth_required=%s&act_id=%s&utm_source=%s" \
          "&utm_medium=%s&utm_campaign=%s" %(
            Conf.index_url, 'true', actid, 'bbs', 'mys', 'icon')

    return {
        'User-Agent': Conf.ua,
        'Referer': ref,
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': self._cookie
    }

  def get_roles(self):
    try:
      jdict = json.loads(
              requests.Session().get(
                  self._url, headers = self.get_header()).text)
    except Exception as e:
      logging.error(e)
      raise HTTPError

    return jdict


class Sign(object):
  def __init__(self, cookie:str=None):
    if type(cookie) is not str:
      raise TypeError("%s want a %s but got %s" %(
          self.__class__, type(__name__), type(cookie)))

    self._url = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

    roles = Roles(cookie)
    errstr = None

    for i in range(1, 4):
      try:
        self._roles = roles.get_roles()
      except HTTPError as e:
        logging.error("HTTP error when get user game roles, retry %s times ..." %(i))
        logging.error("error is %s" %(e))
        errstr = str(e)
        continue
      except KeyError as e:
        logging.error("Wrong response to get user game roles, retry %s times ..." %(i))
        logging.error("response is %s" %(e))
        errstr = str(e)
        continue
      except Exception as e:
        logging.error("Unknown error %s, die" %(e))
        errstr = str(e)
        raise
      else:
        break

    try:
      self._roles
    except AttributeError:
      raise Exception(errstr)

    # cn_gf01:    Official server
    # cn_qd01:    Bilibili server
    try:
      self._region = self._roles['data']['list'][0]['region']
    except:
      raise KeyError(str(self._roles))

    try:
      self._uid = self._roles['data']['list'][0]['game_uid']
    except:
      raise KeyError(str(self._roles))

    self._cookie = cookie

  # Provided by Steesha
  def md5(self, text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return (md5.hexdigest())

  def get_DS(self):
    n = self.md5(Conf.app_version)
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = self.md5("salt=" + n + "&t="+ i + "&r=" + r)
    return i + "," + r + "," + c

  def get_header(self):
    actid = 'e202009291139501'
    ref = "%s?bbs_auth_required=%s&act_id=%s&utm_source=%s" \
          "&utm_medium=%s&utm_campaign=%s" %(
            Conf.index_url, 'true', actid, 'bbs', 'mys', 'icon')

    return {
        'x-rpc-device_id': str(uuid.uuid3(
            uuid.NAMESPACE_URL, self._cookie)).replace('-','').upper(),
        'x-rpc-client_type': '5',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': Conf.ua,
        'Referer': ref,
        'x-rpc-app_version': Conf.app_version,
        'DS': self.get_DS(),
        'Cookie': self._cookie
    }

  def run(self):
    logging.info('UID is %s' %(str(self._uid).replace(str(self._uid)[3:6],'***',1)))

    data = {
        'act_id': 'e202009291139501',
        'region': self._region,
        'uid': self._uid
    }

    try:
      jdict = json.loads(requests.Session().post(
          self._url, headers = self.get_header(),
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


if __name__ == "__main__":
  seconds = random.randint(10, 300)
  logging.info('Sleep for %s seconds ...' %(seconds))

  time.sleep(seconds)

  try:
    jdict = Sign(input().strip()).run()
    jstr = json.dumps(jdict, ensure_ascii=False)
    code = jdict['retcode']
  except Exception as e:
    jstr = str(e)

  result = makeResult('Failed', jstr)

  try:
    code
  except NameError:
    code = -1

  # 0:        success
  # -5003:    already signed in
  if code in [0, -5003]:
    result = makeResult('Success', jstr)
    logging.info(result)
  else:
    logging.info(result)
    exit(-100)
