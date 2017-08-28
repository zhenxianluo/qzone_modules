# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By as BY
from PIL import Image
import ipdb, json, time, requests, os, StringIO, random, re, traceback
from dotenv import load_dotenv, find_dotenv
from useragent import user_agent_list as USER_AGENTS
from base_class import Base_class
load_dotenv(find_dotenv())
# 设置允许爬取的分组
ALLOW_GROUPS = [10, 13]

class Spider(Base_class):
    """主要程序类"""
    def __init__(self):
        Base_class.__init__(self)
        # 照片根目录
        self.root_dir = 'friend_photo'
        self.user_dir = None
        self.friendqq = os.environ.get('num_f')
        self.dom_show_by_js = """document.getElementById('tb_menu_panel').style.display = ''"""

    def path_handle(self, photo_file):
        """对路径字符串进行安全处理，并新建文件夹，返回处理后的字符串"""
        photo_file = re.sub(' ', '', photo_file)
        pf = os.path.split(photo_file)
        if not os.path.exists(pf[0]):
            os.makedirs(pf[0])
        return photo_file

    def goto_photos(self):
        """进入空间好友相册"""
        self.default_click()
        # 旧方法
        # el = self.get_ele('id', 'QM_Profile_Photo_A')
        self.driver.execute_script(self.dom_show_by_js)
        el = self.get_ele('class', 'menu_item_4')
        if el:
            el[0].click()
        else:
            raise "未找到好友空间左上角相册入口"
        #el = self.get_ele('class', 'menu_item_4')
        #el[1].click()
        print "进入空间好友相册"
        self.sub_frame = self.get_ele('id', "tphoto", 0)
        self.default_click()

    def download_file(self, downlist, ispriv):
        """函数功能：下载文件
        downlist格式：[(url, dfile), (url, dfile)]
        ispriv为False时为所有人可见"""
        if type(downlist) != type([]):
            downlist = [downlist]
        if ispriv is True:
            self.driver.get(downlist[0][0])
            self.cookies_to_dict()
        for item in downlist:
            trynum = max_try = 5
            while trynum:
                try:
                    if ispriv is True:
                        r = requests.get(item[0], cookies=self.cookies)
                    else:
                        r = requests.get(item[0])
                    file_type = r.headers['Content-Type'].split('/')[1]
                except Exception, e:
                    print str(max_try - trynum + 1), 'error--> url:', item[0], '--> file: ', item[1]
                    trynum -= 1
                if r and r.status_code == 200:
                    file_name = item[1] + '.' + file_type
                    print 'success--> file:', file_name
                    open(file_name, 'wb+').write(r.content)
                    trynum = 0


# 爬虫主程序，完全基于selenium的模拟操作
def run_execute(ct, qqnum=None):
    # 进入好友空间
    ct.friendqq = str(qqnum) if qqnum is not None and type(qqnum) == type(1) else qqnum or ct.friendqq
    ct.driver.get(ct.user_url + ct.friendqq)
    ct.goto_photos()
    # 尝试获取昵称
    names = ct.get_ele('class', 'textoverflow')
    user_dir = ct.root_dir + os.sep + \
        (names[1].text if len(names) > 1 else ct.friendqq)
    ct.driver.switch_to_frame(ct.sub_frame)
    select_ph = BEGIN_ALBUM
    albums = ct.get_ele('class', 'js-album-cover')
    while select_ph < len(albums):
        ph_parents = ct.get_ele('class', 'js-album-item')[select_ph]
        if ph_parents.get_attribute('data-question'):
            select_ph += 1
            continue
        ph = ct.get_ele('class', 'js-album-cover')[select_ph]
        select_ph += 1
        photo_i = 0
        # 点击进入独立相册
        ph.click()
        time.sleep(1)
        try:
            next_page = ct.get_ele('id', 'pager_next_1', 0, 1) or -1
        except Exception:
            next_page = -1
        while next_page or next_page == -1:
            try:
                photo_name = ct.get_ele('class', 'j-pl-albuminfo-title')[1].text
            except Exception, e:
                photo_name = ct.get_ele('css', '.profile .tit', 0).text
            print "进入独立子相册:", photo_name, "No.", str(select_ph)
            photo_dir = user_dir + os.sep + photo_name
            ct.scroll_to_end()
            imgs = ct.get_ele('class', 'j-pl-photoitem-img')
            if len(imgs) == 0:
                imgs = ct.get_ele('css', '.area-portrait-inner>a>img')
            titles = ct.get_ele('class', 'item-tit')
            for i, img in enumerate(imgs):
                try:
                    # s：小图，m：中图，b：大图
                    img_url = img.get_attribute('src').replace('/m/', '/b/')
                    r = requests.get(img_url)
                except Exception, e:
                    print i, 'error'
                    continue
                if r.status_code == 200:
                    photo_i += 1
                    photo_file = photo_dir + os.sep + '<' + str(photo_i) + '>' + \
                        (titles[i].text if len(titles) else '') + '.jpg'
                    photo_file = ct.path_handle(photo_file)
                    print "%s : %d -----> %d" % (photo_file, i, len(imgs)-i)
                    open(photo_file, 'wb+').write(r.content)
            if next_page != -1:
                next_page.click()
                try:
                    next_page = ct.get_ele('id', 'pager_next_1', 0)
                except Exception:
                    next_page = -1
            else:
                next_page = 0
        # 点击进入好友相册
        ct.get_ele('class', 'js-select')[0].click()
    ct.quit()

def parse_url(url, query_map):
    query_arr = []
    for key, value in query_map.items():
        if type(value) == type(u'type'):
            value = value.encode('utf8')
        query_arr.append(key + '=' + value)
    return url + '?' + '&'.join(query_arr)

# 爬虫主程序，主要基于接口处理，搭配selenium操作
def run_execute_for_api(ct, item):
    qqnum = item['uin']
    # 进入好友空间
    ct.friendqq = str(qqnum) if qqnum is not None and type(qqnum) == type(1) else qqnum or ct.friendqq
    ct.driver.get(ct.user_url + ct.friendqq)
    if len(ct.driver.find_elements_by_id('tb_menu_panel')) == 0:
        print '对用户：', item['remark'], '空间无访问权限'
        return
    ct.goto_photos()
    user_dir = os.path.join(ct.root_dir, item['remark'])
    ct.driver.switch_to_frame(ct.sub_frame)
    albums = ct.get_ele('class', 'js-album-item')
    path_url = []
    for select_ph, ph_parents in enumerate(albums):
        # 需要回答问题的相册跳过
        if ph_parents.get_attribute('data-priv') == '5':
            continue
        query_map = {
            'topicId': ph_parents.get_attribute('data-id'),
            'pageNum': ph_parents.get_attribute('data-total'),
            'g_tk': str(ct.g_tk),
            'mode': '0',
            'hostUin': ct.friendqq,
            'uin': ct.userqq,
            'inCharset': 'gbk',
            'outCharset': 'gbk'
        }
        url = ('https://h5.qzone.qq.com'
               '/proxy/domain/photo.qzone.qq.com/fcgi-bin/'
               'cgi_list_photo')
        url = parse_url(url, query_map)
        priv = ph_parents.get_attribute('data-priv')
        path_url.append([user_dir, url, priv])
    for index, item in enumerate(path_url):
        ct.driver.get(item[1])
        xx = ct.get_ele('tag', 'pre', 0).text.encode('utf8')[10:-2]
        data = json.loads(xx)
        if data['code'] == -4003:
            print data['message'], "或该相册无照片"
            continue
        photo_dir = os.path.join(item[0],
                                 data['data']['topic']['name']).replace(' ', '')
        print str(index), photo_dir
        if not os.path.exists(photo_dir):
            os.makedirs(photo_dir)
        ph_list = data['data']['photoList']
        print 'total have ', str(len(ph_list))
        ans = []
        ispriv = True if item[2] in ['4', '6', '8', '3'] else False
        for i, ph_item in enumerate(ph_list):
            filename = os.path.join(photo_dir, ''.join(
                ['<', str(i), '>', ph_item['name'].replace(' ', '')]))
            ans.append((ph_item['url'], filename, ))
        ct.download_file(ans, ispriv)



if __name__ == "__main__":
    try:
        ct = Spider()
        ct.driver_init()
        index = 0
        for item in ct.friends_json['items']:
            if item['groupid'] in ALLOW_GROUPS:
                index += 1
                if index <= 2: continue
                print item['uin'], '<----->', item['remark']
                run_execute_for_api(ct, item)
    except Exception, e:
        traceback.print_exc()
