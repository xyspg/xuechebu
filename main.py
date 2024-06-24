import requests
import time
import hashlib
import urllib3
from alive_progress import alive_bar
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



config = {
    "username": "你的手机号",
    "password": "你的密码",
    "subject": "km=4"  # km=1 为科目一，km=4 为科目四
}

base_url = "https://xuexiapi.xuechebu.com"
headers = {
  'Host': 'xuexiapi.xuechebu.com',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Connection': 'keep-alive',
  'Accept': '*/*',
  'User-Agent': 'iOS_XueCheBu;v11.4.4; (iPhone; iOS_XueCheBu 17.3.1; Scale/3.00; build/2208242;)',
  'Accept-Language': 'en-US;q=1, zh-Hans-US;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br'
}


def get_chapter_info(session):
    unfinished = []

    payload = config['subject']

    url = base_url + "/videoApiNew/SpPlay/GetChapterInfo"
    try:
        response = session.post(url, headers=headers, data=payload)
        if response.json()['data'] is None:
            raise RuntimeError("[ERROR] 用户未登录")
    except Exception as e:
        print(e)
    chapter_list = response.json()["data"]["ChapterList"]

    for chapter in chapter_list:
        if chapter["ID"] == "0":
            continue

        finished = chapter["SFJS"] == "1"

        if not finished:
            unfinished.append(chapter)

    return unfinished


def watch_video(session, video):
    try:
        session.get(f"{base_url}/videoApiNew/SpPlay/SetPlayProgress?Id={video['ID']}&Type=4&beforeWatchTime=0&thisWatchLocation=0&thisWatchTime=0")
    except Exception as e:
        print(f'Failed to watch {video["KSMC"]} {video["ZJMC"]}')
        print(e)


def main():
    print("python，启动！")
    print(f"当前科目：{'科目一' if config['subject'] == 'km=1' else '科目四'}")
    if config["username"] and config["password"]:
        username = config["username"]
        password = config["password"]
    else:
        username = str(input("请输入手机号: "))
        password = str(input("请输入密码: "))
    with requests.session() as s:
        s.verify = False
        success = login(s, username, password)
        s.headers.update(headers)
        if not success:
            print("登录失败")
            exit(1)

        unfinished = get_chapter_info(s)
        print(f"{len(unfinished)}个待学视频：", unfinished)
        if len(unfinished) == 0:
            print("没有未完成的视频")
            return

        with alive_bar(len(unfinished), force_tty=True) as bar:  # set force_tty to make this work in Pycharm
            for video in unfinished:
                print(f'Watching {video["KSMC"]} {video["ZJMC"]}')
                watch_video(s, video)
                bar()
                time.sleep(0.5)


def login(session, username, password):
    url = f"https://api.xuechebu.com/usercenter/userinfo/login?username={username}&passwordmd5={to_md5(password)}&callback=jQuery1910061955733684618375_1709975355621&ISJSONP=true&os=pc"

    payload = {}
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.xuechebu.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = session.request("GET", url, headers=headers, data=payload)

    if response.status_code != 200:
        return False

    return True


def to_md5(s):
    return hashlib.md5(s.encode()).hexdigest()


if __name__ == '__main__':
    main()
