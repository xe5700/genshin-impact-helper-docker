'''
@File                : weibo.py
@Github              : https://github.com/y1ndan/genshin-impact-helper
@Author              : y1ndan
@Created on          : 2021-02-05 21:30:30
'''
import os
import re

from time import sleep
from bs4 import BeautifulSoup

from settings import log, CONFIG, req
from notify import Notify


class Weibo():
    def __init__(self, wb_cookie: str = None):
        self.wb_cookie = wb_cookie

    def get_header(self):
        header = {
            'User-Agent': CONFIG.WB_USER_AGENT,
            'Referer': 'https://m.weibo.cn',
            'Cookie': self.wb_cookie
        }
        return header

    def get_super_list(self):
        log.info('准备获取超话列表...')
        try:
            response = req.request('get', CONFIG.SUPER_URL,
                headers=self.get_header(), allow_redirects=False)
        except Exception as e:
            log.error(e)
        else:
            if response.status_code == 200:
                log.info('🥳 weibo: 超话列表获取成功')
                return req.to_python(response.text)
            elif response.status_code == 302:
                log.error('😳 weibo: 登录可能失效, 尝试重新登录')
            else:
                log.error('😳 weibo: 超话列表获取失败')

        log.info('超话列表获取完毕')
        return

    def resolve_data(self):
        super_list = self.get_super_list()
        if not super_list:
            log.info('取消解析数据信息')
            return
        log.info('准备解析数据信息...')
        follow_list = []
        try:
            card_group = super_list['data']['cards'][0]['card_group'][1:-1]
        except Exception as e:
            log.error(e)
        else:
            for card in card_group:
                follow = {
                    'title_sub':card['title_sub'],
                    'containerid': card['scheme'].split('&')[0].split('=')[1],
                    'lv': int(re.findall('\d+', card['desc1'])[0]),
                    'is_sign': card['buttons'][0]['name'],
                    'sign_url': False
                }
                scheme = card['buttons'][0]['scheme']
                if scheme:
                    follow['sign_url'] = f'https://m.weibo.cn{scheme}'
                follow_list.append(follow)
        log.info(f'解析到 {len(follow_list)} 条数据')
        if follow_list:
            for follow in follow_list:
                log.info(f'⚜️ [Lv.{follow["lv"]}]{follow["title_sub"]}')

        log.info('数据信息解析完毕')
        return follow_list

    def super_sign(self):
        follow_list = self.resolve_data()
        if not follow_list:
            log.info('取消微博超话签到')
            return
        for follow in follow_list:
            lv = f'[Lv.{follow["lv"]}]'
            name = follow['title_sub']
            log.info(f'准备为 {name} 超话签到...')
            sleep(5)
            if follow['is_sign'] == '已签':
                log.info(f'👀 {lv}{name}: 已经签到过了哦')
                continue
            elif follow['is_sign'] == '签到':
                url = follow['sign_url']
                try:
                    response = req.to_python(req.request(
                        'post', url, headers=self.get_header()).text)
                except Exception as e:
                    log.error(e)
                else:
                    if response['ok'] == 1:
                        log.info(f'🥳 {lv}{name}: 签到成功')
                    else:
                        log.info(f'😳 {lv}{name}: 签到失败\n{response}')

        log.info('微博超话签到完毕')
        return


class RedeemCode(object):
    def __init__(self, ka_cookie: str = None):
        self.ka_cookie = ka_cookie
        self.header = Weibo().get_header()

    def get_id(self):
        log.info('准备获取活动信息...')
        id_list = []
        try:
            response = req.to_python(req.request(
                'get', CONFIG.YS_URL, headers=self.header).text)
            group = response['data']['cards'][3]['card_group'][0]['group']
        except Exception as e:
            log.error(f'活动信息获取失败:\n{e}')
        else:
            for ids in group:
                if '礼包' in ids.get('title_sub', ''):
                    id = re.findall('(?<=gift\/)(.*)\?channel', ids['scheme'])[0]
                    log.info(f'└─🎁 {ids["title_sub"]}')
                    id_list.append(id)
            if not id_list:
                log.info('原神超话暂无活动')

        log.info('活动信息获取完毕')
        return id_list

    def get_code(self, id):
        item = f'🎁 {id}'
        log.info(f'准备领取 {item} 的兑换码...')
        data = {
            'gid': 10725,
            'itemId': id,
            'channel': 'wblink'
        }
        self.header['Referer'] = f'https://ka.sina.com.cn/html5/gift/{id}'
        self.header['Cookie'] = self.ka_cookie

        retry = 3
        sec = 5
        for i in range(retry):
            sleep(sec)
            log.info(f'♻️ 第 {i + 1} 次领取 {id} 的兑换码...')
            try:
                response = req.to_python(req.request(
                    'get', CONFIG.KA_URL, params=data, headers=self.header).text)
            except Exception as e:
                log.error(e)
            else:
                if response.get('k'):
                    log.info(f'{item} 的兑换码领取成功')
                    return response['data']['kahao']
                elif response.get('code') == '2002' and '头像' in response.get('msg', ''):
                    log.error(f'🥳 {id}: 每天只能领取一张或该兑换码已经领取过了哦')
                    break
                elif response.get('code') == '2002' and '签到' or '尚未' in response.get('msg', ''):
                    log.error(f'😳 {id}: {response["msg"]}')
                    break
                elif response.get('code') == '2002':
                    log.error(f'😳 {id}: {response["msg"]}')
                elif 'login' in response.get('msg', ''):
                    log.error('登录失效, 请重新登录')
                    return
                else:
                    log.error(f'😳 {id}: {response}')

                if i + 1 != retry:
                    log.info(f'将在 {sec} 秒后重试...')
                else:
                    log.error(f'🚫 {id}: 失败次数达到上限, 放弃领取该兑换码')

        log.info('兑换码获取完毕')
        return

    def get_box_code(self):
        log.info('准备获取「个人中心」的兑换码...')
        id_list = []
        code_list = []
        self.header['Referer'] = f'https://ka.sina.com.cn/html5/'
        self.header['Cookie'] = self.ka_cookie
        try:
            response = req.request('get',
                CONFIG.BOX_URL, headers=self.header, allow_redirects=False)
        except Exception as e:
            log.error(e)
        else:
            if response.status_code == 200:
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                # print(soup.prettify())
                boxs = soup.find_all(class_ = 'giftbag')
                for box in boxs:
                    item = {
                        'id': box.find(class_ = 'deleBtn').get('data-itemid'),
                        'title': box.find(class_ = 'title itemTitle').text,
                        'code': box.find('span').parent.contents[1]
                    }
                    log.info(f'└─☁️{item["title"]}')
                    id_list.append(item['id'])
                    code_list.append(item)
                code_list.insert(0, id_list)
            elif response.status_code == 302:
                log.error('😳 ka.sina: 登录可能失效, 尝试重新登录')
            else:
                log.error('😳 ka.sina: 兑换码获取失败')

        # 打印兑换码
        # print(req.to_json(code_list))

        log.info('「个人中心」的兑换码获取完毕')
        return code_list


if __name__ == '__main__':
    log.info(f'🌀微博超话签到小助手 v{CONFIG.WBH_VERSION}')
    """Sina COOKIE
    :param WB_COOKIE: 新浪微博的COOKIE.前往  https://m.weibo.cn 获取.
    :param KA_COOKIE: 新浪新手卡的COOKIE.前往 https://ka.sina.com.cn 获取.
    """
    # Github Actions用户请到Repo的Settings->Secrets里设置变量,变量名字必须与上述参数变量名字完全一致,否则无效!!!
    # Name=<变量名字>,Value=<获取的值>
    WB_COOKIE = ''
    KA_COOKIE = ''

    if os.environ.get('WB_COOKIE', '') != '':
        WB_COOKIE = os.environ['WB_COOKIE']
    if os.environ.get('KA_COOKIE', '') != '':
        KA_COOKIE = os.environ['KA_COOKIE']

    if WB_COOKIE:
        Weibo(WB_COOKIE).super_sign()
    if KA_COOKIE:
        events = RedeemCode(KA_COOKIE).get_id()
        codes = RedeemCode(KA_COOKIE).get_box_code() if events else ''
        if events and codes:
            ids = [i for i in events if i not in codes[0]]
            if not ids:
                log.info('兑换码已全部领取')
            else:
                log.info(f'检测到有 {len(ids)} 个未领取的兑换码')
                for id in ids:
                    code = RedeemCode(KA_COOKIE).get_code(id)
                    status = '原神兑换码' if code else '原神微博活动提醒'
                    msg = code if code else f'🎁 您有未领取的礼包'
                    Notify().send(status=status, msg=msg, hide=True)

        else:
            log.info('取消领取签到礼包')

