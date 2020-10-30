#!/usr/bin/env python3

import requests
import json
import uuid
import logging
from time import sleep
from random import randint
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
  def ua(self):
    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) '  \
            'AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.1.0'


class Conf(metaclass=ConfMeta):
  pass


class UID(object):
  def __init__(self, cookie:str=None):
    if type(cookie) is not str:
      raise TypeError("%s want a %s but got %s" %(
          self.__class__, type(__name__), type(cookie)))

    self._cookie = cookie
    self._url = "https://api-takumi.mihoyo.com/binding/api/"   \
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

  def get_uid(self):
    try:
      jdict = json.loads(
              requests.Session().get(
                  self._url, headers = self.get_header()).text)
    except Exception as e:
      logging.error(e)
      raise HTTPError

    try:
      return jdict['data']['list'][0]['game_uid']
    except:
      raise KeyError(str(jdict))


class Sign(object):
  def __init__(self, cookie:str=None):
    if type(cookie) is not str:
      raise TypeError("%s want a %s but got %s" %(
          self.__class__, type(__name__), type(cookie)))

    self._url = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

    uid = UID(cookie)
    errstr = None

    for i in range(1, 4):
      try:
        self._uid = uid.get_uid()
      except HTTPError as e:
        logging.error("HTTP error when get UID, retry %s times ..." %(i))
        logging.error("error is %s" %(e))
        errstr = str(e)
        continue
      except KeyError as e:
        logging.error("Wrong response to get UID, retry %s times ..." %(i))
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
      self._uid
    except AttributeError:
      raise Exception(errstr)

    self._cookie = cookie

  def get_header(self):
    actid = 'e202009291139501'
    ref = "%s?bbs_auth_required=%s&act_id=%s&utm_source=%s" \
          "&utm_medium=%s&utm_campaign=%s" %(
            Conf.index_url, 'true', actid, 'bbs', 'mys', 'icon')

    return {
        'User-Agent': Conf.ua,
        'Referer': ref,
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': self._cookie,
        'x-rpc-device_id': str(uuid.uuid3(
            uuid.NAMESPACE_URL, self._cookie)).replace('-','').upper()
    }

  def run(self):
    logging.info('UID is %s' %(str(self._uid).replace(str(self._uid)[3:6],'***',1)))

    data = {
        'act_id': 'e202009291139501',
        'region': 'cn_gf01',
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
  seconds = randint(10, 300)
  logging.info('sleep for %s seconds ...' %(seconds))

  sleep(seconds)

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

