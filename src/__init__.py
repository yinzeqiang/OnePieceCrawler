import requests
from bs4 import BeautifulSoup
import threading
from PIL import Image
from io import BytesIO
import os
import traceback

"""
 从快看漫画网上爬取海贼王漫画
"""
DOMAIN = "http://www.kuaikanmanhua.com"
URL = "/web/topic/1338/"
# 漫画存储地址，记得修改。目录会自动创建
FILE_PATH = "F:/onePiece2/"
my_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Accept-Encoding': 'gzip',
    'Connection': 'keep-alive'}

# 如果需要走网络代理，则配代理地址。我用的是sock5代理，（使用sock5代理需要模块支持，安装命令 pip install requests[socks]）
# proxies_config = {
#     'http': 'socks5://127.0.0.1:9998',
#     'https': 'socks5://127.0.0.1:9998'
# }

# 不用代理直接 proxies_config = None
proxies_config = None

# 5个任务并行跑漫画内容，如果网速够快，不怕IP被封，可以变多个
thread_max_num = threading.Semaphore(5)


def fun():
    responsess = requests.get(DOMAIN + URL, headers=my_headers, timeout=300, proxies=proxies_config)
    if responsess.status_code == requests.codes.ok and responsess.content:
        htmll = responsess.content
        soup = BeautifulSoup(htmll, features="html.parser")
        table = soup.select("table.table")[0]
        a = table.select("a.article-img")
        for a_link in a:
            href = DOMAIN + a_link.get("href")
            title = a_link.get("title")
            t = MyThread(get_save_image, (href, title), name="onePiece-thread#" + title)
            t.start()


def get_save_image(args: tuple):
    href = args[0]
    title = args[1]
    print(threading.current_thread().name)
    page1 = requests.get(href, headers=my_headers, timeout=300, proxies=proxies_config)
    if page1.status_code == requests.codes.ok and page1.content:
        soup = BeautifulSoup(page1.content, features="html.parser")
        imgs = soup.select("div.comic-imgs")[0].select("img.kklazy")
        count = 1
        for img in imgs:
            img_src = img.get("data-kksrc")
            try:
                page2 = requests.get(img_src, headers=my_headers, timeout=300, allow_redirects=False,
                                     proxies=proxies_config)
                if page2.status_code == requests.codes.ok and page2.content:
                    imagee = Image.open(BytesIO(page2.content))
                    pathh = FILE_PATH + title.strip().replace(":", "-").replace("/", "")
                    if not os.path.isdir(pathh):
                        os.makedirs(pathh)
                    imagee.save(pathh + "/" + str(count) + ".jpg")
                    count = count + 1
                else:
                    print("<---------------------------------------------------------------------->")
                    print(page2.content)
                    print("<======================================================================>")
            except BaseException as e1:
                print("<**********************************************************************>")
                traceback.print_exc()
                print("<......................................................................>")
    else:
        print("<=================================================================>")
        print(page1.content)
        print("<#################################################################>")


class MyThread(threading.Thread):
    def __init__(self, funn, argss: tuple, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  args=args, kwargs=kwargs, daemon=daemon)
        self.funn = funn
        self.args = argss

    def run(self):
        with thread_max_num:
            self.funn(self.args)


if __name__ == "__main__":
    fun()
