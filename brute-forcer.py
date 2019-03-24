import queue
import threading
import urllib3
import urllib.parse as U
import urllib.error as E

threads = 5
target = 'http://testphp.vulnweb.com/'
filepath = 'words.txt'
ext = [".php"]
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"

def wordlist_build(filepath):
    is_resume = False
    words = queue.Queue()

    with open(filepath) as fp:
       raw = fp.readline()
       while raw:
           word = raw.strip()
           words.put(word)
           raw = fp.readline()

    fp.close()
    return words

def brut_dir(word_queue,extensions=None):

    while not word_queue.empty():
        try_this = word_queue.get()
        try_list = []

        if "." not in try_this:
            try_list.append("/{}/".format(try_this))
        else:
            try_list.append("/{}".format(try_this))

        if extensions:
            for extension in extensions:
                try_list.append("/{}{}".format(try_this,extension))

        for brute in try_list:
            url = "{}{}".format(target,U.quote(brute))

            try:
                http = urllib3.PoolManager()
                head = {}
                head["User-Agent"] = user_agent
                response = http.request("GET",headers=head,url=url)

                if len(response.data):
                    if response.status != 404:
                        print("[{}] ==> {}".format(response.status,url))

            except (E.URLError,E.HTTPError):
                if hasattr(E.HTTPError,'code') and E.HTTPError.code != 404:
                    print("!!!!! [{}] ==> {}".format(E.HTTPError.code,url))
                pass

d_queue = wordlist_build(filepath)

for i in range(threads):
    t = threading.Thread(target=brut_dir,args=(d_queue,ext,))
    t.start()
