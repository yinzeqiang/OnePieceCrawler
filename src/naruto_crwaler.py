import requests
from bs4 import BeautifulSoup
import threading
from PIL import Image
from io import BytesIO
import os
import traceback

"""
    爬取火影忍者前350回的漫画（后面的章节要付费，爬不下来） 配置同onePiece的配置
"""
DOMAIN = "http://www.kuaikanmanhua.com"
URL = "/web/topic/1342/"
FILE_PATH = "F:/naruto1/"
my_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Accept-Encoding': 'gzip',
    'Connection': 'keep-alive'}
proxies_config = {
    'http': 'socks5://127.0.0.1:9998',
    'https': 'socks5://127.0.0.1:9998'
}
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
            t = MyThread(get_save_image, (href, title), name="naruto-thread#" + title)
            t.start()


def get_save_image(args:tuple):
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
                page2 = requests.get(img_src, headers=my_headers, timeout=300, allow_redirects=False, proxies=proxies_config)
                if page2.status_code == requests.codes.ok and page2.content:
                    imagee = Image.open(BytesIO(page2.content))
                    pathh = FILE_PATH + title.strip().replace(":","-").replace("/","")
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
    # print(type(get_save_image))
