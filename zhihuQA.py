# -*- coding:utf-8 -*-

# ID: zhihuQA.py
# By: github.com/Shaw-lib
# At: 2017/7/10

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

import json
import time
import http.cookiejar
import requests, html2text
from itertools import chain

from login import Logging
from login import isLogin

# 用以取消requests认证警告
requests.packages.urllib3.disable_warnings()


class zhihuQA(object):
    """
    问题(问题链接)
    作者(链接) 赞数
    内容
    创建时间(原文链接)
    """
    def __init__(self):
        self.Q_id = int(input("请输入问题编号\n>>"))
        self.A_num = int(input("请输入要获得的答案个数\n>>"))


    def get_data(self):
        try:
            requests = requests.Session()
        except:
            import requests
            requests = requests.Session()

        requests.cookies = http.cookiejar.LWPCookieJar('cookies')
        try:
            requests.cookies.load(ignore_discard=True)
        except:
            raise Exception("cookies载入失败，请检查login")

        if isLogin() != True:
            Logging.error(u"你的身份信息已经失效，请重新生成身份信息( `python LoginZH.py` )。")
            raise Exception("无权限(403)")

        print("已经登录，成功载入cookies!\n")

        print("开始抓取答案")


        # 请求头，直接复制Chrome的。
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            'Host': "www.zhihu.com",
            'Connection': "keep-alive",
            'Upgrade - Insecure - Requests': "1",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Accept - Encoding': "gzip, deflate, br",
            'Accept - Language': "zh - CN, zh;q=0.8"
            }

        Q_id = self.Q_id
        A_num = self.A_num
        # 伪页数变量
        start_num = int(A_num / 20)

        # 制作一个空生成器
        answers_data = []
        answers_data = (x for x in answers_data)

        for page_now in range(start_num + 1):
            # 通过chrome开发者工具找到的json数据接口，简化保留需要的数据。
            QA_url = "https://www.zhihu.com/api/v4/questions/{}/\
answers?&sort_by=default&include=data[*]\
.content,voteup_count,created_time&offset={}&limit=20".format(Q_id, page_now * 20)

            res = requests.get(QA_url, headers=headers, verify=False)
            data = json.loads(res.text)

            # 先看看需要的答案是不是超过总回答数。
            totals = data['paging']['totals']
            if A_num > totals:
                print("该问题下一共有{}个回答，你要的超过这个数字啦！".format(totals))
                break

            # answers_data is a list
            # 将20个dict元素转化为生成器。
            new_answers_data = (y for y in data['data'])
            # 合并生成器
            answers_data = chain(answers_data, new_answers_data) # answers_data这时是一个包含我们需要的所有答案的生成器。

        return answers_data


    def get_md(self):
        A_num = self.A_num
        # 计数器
        n = 0
        # 逐个输出答案并保存。
        for data in self.get_data():
            title        = data['question']['title']
            question_url = "http://www.zhihu.com/question/{}".format(data['question']['id'])
            author       = data['author']['name']
            author_url   = "http://www.zhihu.com/people/{}".format(data['author']['url_token'])
            upvote       = str(data['voteup_count'])+"个赞"
            content      = '\n\n' + html2text.html2text(data['content'])  # this is html
            answer_url   = '\n\n原文链接：'+question_url+'/{}'.format(data['id'])
            answer_time  = '\n\n发布于'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['updated_time']))

            question     = "[{}]({})".format(title, question_url)
            author_info  ="作者：[{}]({})".format(author, author_url)

            try:
                with open("/mark/{}--前{}个回答.md".format(title,A_num), 'a') as f:
                    print(question,
                          '\n----------\n',
                          author_info, upvote,
                          content,
                          answer_time,
                          answer_url,
                          '\n\n',
                          file=f)
                f.close()
            except UnicodeEncodeError:
                content = html2text.html2text(data['content']).encode('gbk', errors="replace").decode('gbk')
                with open("/mark/{}--前{}个回答.md".format(title,A_num), 'a') as f:
                    print(content,
                          answer_time,
                          answer_url,
                          '\n\n',
                          file=f)
            n += 1
            if n >= A_num:
                break
            else:
                continue


if __name__ == "__main__":
    # Q_id:31740233
    # A_num:43
    start = time.time()
    QA = zhihuQA()
    QA.get_md()
    end = time.time()
    cost = round(end - start)
    print('抓取了{}个答案，共计{}秒。'.format(A_num,cost))