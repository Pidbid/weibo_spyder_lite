# -*- encoding: utf-8 -*-
'''
@File    :   weibo.py
@Time    :   2020/11/05 16:20:07
@Author  :   Wicos 
@Version :   1.0
@Contact :   wicos@wicos.cn
@Blog    :   https://www.wicos.me
'''

# here put the import lib
import requests as rq
import datetime


class WEIBO(object):
    def __init__(self, user_id: str=None) -> None:
        self.user_id = user_id
        self.url_user_info = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=100505{}".format(
            self.user_id, self.user_id)
        self.url_weibo_origin = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}".format(
            self.user_id, self.user_id)
        self.url_weibo_info_all = "https://m.weibo.cn/api/container/getIndex?containerid=230283{}_-_INFO".format(
            self.user_id)
        self.url_login = "https://passport.weibo.cn/sso/login"
        self.session = rq.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Mobile Safari/537.36'
        }

    def __data_analyze__(self, data):
        """
        docstring
        """
        if data.status_code == 200 and data.json().get("ok") == 1:
            return True
        else:
            return False

    def __weibo_data__(self, data):
        weibo_data = []
        for i in data:
            if not i.get('mblog'):
                continue
            in_weibo_data = {
                "created_time": i['mblog']['created_at'],
                "text": i['mblog']['raw_text'],
                "source": i['mblog']['source'],
            }
            if i['mblog'].get("original_pic"):
                in_weibo_data['pic'] = i['mblog']['original_pic']
            if i['mblog'].get("pics"):
                pic_urls = ''
                for j in i['mblog'].get("pics"):
                    pic_urls += j['url'] + ";"
                in_weibo_data['pics'] = pic_urls
            weibo_data.append(in_weibo_data)
        return weibo_data

    def login(self, username, password):
        """
        docstring
        """
        login_headers = {
            "Host": "passport.weibo.cn",
            "Origin": "https://passport.weibo.cn",
            "Referer": "https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Mobile Safari/537.36"
        }
        login_data = {
            "username": username,
            "password": password,
            "savestate": 1,
            "r": "https://m.weibo.cn/",
            "ec": 1,
            "pagerefer": "https://m.weibo.cn/login?backURL=https%3A%2F%2Fm.weibo.cn%2F",
            "entry": "mweibo",
            "wentry": None,
            "loginfrom": None,
            "client_id": None,
            "code": None,
            "qq": None,
            "mainpageflag": 1,
            "hff": None,
            "hfp": None
        }
        get_login_data = rq.post(self.url_login, data=login_data,headers=login_headers)
        get_login_data_json = get_login_data.json()
        if get_login_data_json['retcode'] == 50011002:
            print("用户名或密码错误")
        elif get_login_data_json['retcode'] == 50050011:
            verify_url = get_login_data_json['data']['errurl']
            print("请完成验证",verify_url)

    def set_cookies(self, cookies):
        self.session.headers.update({
            "cookie": cookies
        })

    def user_info(self):
        get_data = self.session.get(url=self.url_user_info)
        if get_data.status_code == 200 and get_data.json().get("ok") == 1:
            origin_data = get_data.json()['data']
            total_data = self.session.get(self.url_weibo_origin)
            total = total_data.json(
            )["data"]["cardlistInfo"]["total"] if total_data.status_code == 200 else None
            user_info_data = {
                "user_id": origin_data['userInfo']['id'],
                "name": origin_data['userInfo']['screen_name'],
                "description": origin_data['userInfo']['description'],
                "fans": origin_data['userInfo']['followers_count'],
                "follows": origin_data['userInfo']['follow_count'],
                "pic": origin_data['userInfo']['avatar_hd'],
                "bg_pic": origin_data['userInfo']['cover_image_phone']
            }
            if total:
                user_info_data.update({"total": total})
            oth_data = self.session.get(self.url_weibo_info_all)
            if self.__data_analyze__(oth_data):
                oth_data_json = oth_data.json()
                all_cards_data = oth_data_json['data']['cards']
                for i in all_cards_data:
                    for j in i['card_group']:
                        if j.get("item_name") == "性别":
                            user_info_data.update(
                                {"gender": j.get('item_content')})
                        if j.get("item_name") == "生日":
                            user_info_data.update(
                                {"borthday": j.get('item_content')})
                        if j.get("item_name") == "大学":
                            user_info_data.update(
                                {"hignscrool": j.get('item_content')})
                        if j.get("item_name") == "所在地":
                            user_info_data.update(
                                {"location": j.get('item_content')})
                        if j.get("item_name") == "注册时间":
                            user_info_data.update(
                                {"register": j.get('item_content')})
            return user_info_data
        else:
            return {"ok": 0, "msg": "something wrong"}

    def weibo(self, num: int):
        """
        num 表示返回的微博数量
        num = 0 表示返回全部微博 建议微博在100条以下的使用
        num = -1 表示只获取第一页 大概10条 用于“增量更新”
        """
        if num == 0:
            get_data = self.session.get(url=self.url_weibo_origin)
            weibo_data = self.__weibo_data__(get_data.json()['data']['cards'])
            since_id = get_data.json()["data"]["cardlistInfo"].get('since_id')
            while since_id:
                get_data = self.session.get(
                    url=self.url_weibo_origin+"&since_id="+str(since_id))
                weibo_data += self.__weibo_data__(
                    get_data.json()['data']['cards'])
                since_id = get_data.json(
                )["data"]["cardlistInfo"].get("since_id")
            rt_weibo = []
            today = datetime.date.today()
            for i in weibo_data:
                if '昨天' in i['created_time']:
                    i['created_time'] = str(today - datetime.timedelta(days=1))
                if '前' in i['created_time']:
                    i['created_time'] = str(today)
                if len(i['created_time'].split('-')) == 2:
                    i['created_time'] = str(today).split('-')[0] + "-" + i['created_time']
                rt_weibo.append(i)
            return self.data_sort(rt_weibo)
        elif num == -1:
            get_data = self.session.get(url=self.url_weibo_origin)
            weibo_data = self.__weibo_data__(get_data.json()['data']['cards'])
            rt_weibo = []
            today = datetime.date.today()
            for i in weibo_data:
                if '昨天' in i['created_time']:
                    i['created_time'] = str(today - datetime.timedelta(days=1))
                if '前' in i['created_time']:
                    i['created_time'] = str(today)
                if len(str(i['created_time']).split('-')) == 2:
                    i['created_time'] = str(today).split('-')[0] + "-" + i['created_time']
                rt_weibo.append(i)
            return self.data_sort(rt_weibo)
        else:
            origin_loop = int(num/10) if num % 10 == 0 else int(num/10)+1
            # print(origin_loop)
            get_data = self.session.get(url=self.url_weibo_origin)
            if get_data.status_code == 200 and get_data.json().get("ok") == 1:
                origin_data = get_data.json()
                weibo_data = self.__weibo_data__(origin_data['data']['cards'])
                since_id = origin_data["data"]["cardlistInfo"]["since_id"]
                for i in range(origin_loop):
                    get_data = self.session.get(
                        url=self.url_weibo_origin+"&since_id="+str(since_id))
                    since_id = get_data.json(
                    )["data"]["cardlistInfo"].get("since_id")
                    if self.__data_analyze__(get_data):
                        weibo_data += self.__weibo_data__(
                            get_data.json()['data']['cards'])
                        if since_id == None:
                            break
                    else:
                        continue
                all_weibo = weibo_data[:num]
                rt_weibo = []
                today = datetime.date.today()
                for i in all_weibo:
                    if '昨天' in i['created_time']:
                        i['created_time'] = today - datetime.timedelta(days=1)
                    if '前' in i['created_time']:
                        i['created_time'] = str(today)
                    if len(i['created_time'].split('-')) == 2:
                        i['created_time'] = str(today).split('-')[0] + "-" + i['created_time']
                    rt_weibo.append(i)
                return self.data_sort(rt_weibo)
            else:
                return {"ok": 0, "msg": "something wrong"}

    def data_sort(self,data:list):
        nums = ''
        def sorts(i):
            return int(str().join(i['created_time'].split("-")))
        data.sort(reverse=True,key=sorts)
        return data
