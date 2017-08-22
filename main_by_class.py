# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By as BY
from PIL import Image
import ipdb, json, time, requests, os, StringIO, random, re, traceback
from dotenv import load_dotenv, find_dotenv
from useragent import user_agent_list as USER_AGENTS
load_dotenv(find_dotenv())
# 开始相册
BEGIN_ALBUM = 0
# 设置允许爬取的分组
ALLOW_GROUPS = [8, 10, 13]

class Spider(object):
    """主要程序类"""
    def __init__(self):
        # cookie保存文件
        self.cookie_file = 'website_cookie.json'
        self.friends_file = 'qqfriends.json'
        self.base_url = u'https://qzone.qq.com/'
        self.user_url = u'https://user.qzone.qq.com/'
        self.login_url = u'i.qq.com'
        # 照片根目录
        self.root_dir = 'friend_photo'
        self.driver = None
        self.sub_frame = None
        self.user_dir = None
        self.g_tk = None
        self.friends_json = None
        self.friends_url = ('https://h5.qzone.qq.com/proxy/domain/'
                            'r.qzone.qq.com/cgi-bin/tfriend/'
                            'friend_show_qqfriends.cgi?'
                            'uin={qq_num}&g_tk={g_tk}')
        self.one_page_len = '500'
        self.userqq = os.environ.get('num')
        self.userpwd = os.environ.get('num_p')
        self.friendqq = os.environ.get('num_f')
        self.chrome_path = os.environ.get('chrome_path')
        # 值为2时不加载图片
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.screen_blow_by_js = """
            var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
            if(Math.abs(document.documentElement.scrollHeight - document.documentElement.clientHeight - scrollTop) < 10){
                document.getElementsByTagName('body')[0].setAttribute('haha', 'blow');
            }
        """
        self.screen_origin_by_js = "window.scrollTo(0,0);document.getElementsByTagName('body')[0].setAttribute('haha', 'origin');"
        self.next_scroll_by_js = "window.scrollBy(0,{})"
        self.dom_remove_by_js = """
            var wel=document.getElementById('welcomeflash');
            document.documentElement.style.overflow = "";
            wel && (wel.innerHTML = '');
            wel && document.body.removeChild(wel);
            window.QZONE && window.QZONE.Gift4Visitor && window.QZONE.Gift4Visitor.init();
            window.g_hasWelcomeflash = 0;
        """

    def path_handle(self, photo_file):
        """对路径字符串进行安全处理，并新建文件夹，返回处理后的字符串"""
        photo_file = re.sub(' ', '', photo_file)
        pf = os.path.split(photo_file)
        if not os.path.exists(pf[0]):
            os.makedirs(pf[0])
        return photo_file

    def driver_init(self):
        """初始化浏览器操作句柄"""
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("prefs", self.prefs)
        chromeOptions.add_argument('lang=zh_CN.UTF-8')
        chromeOptions.add_argument(random.choice(USER_AGENTS))
        self.driver = webdriver.Chrome(
            executable_path=self.chrome_path,
            chrome_options=chromeOptions)
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        self.login_by_cookie()
        self.get_friends()

    def login_by_cookie(self):
        """读取cookie并写入浏览器"""
        status = 0
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'rb') as f:
                cookie_read = f.read()
                if cookie_read.strip():
                    self.driver.delete_all_cookies()
                    try:
                        for item in json.loads(cookie_read):
                            self.driver.add_cookie(item)
                    except Exception, e:
                        print str(e)
                    self.driver.refresh()
                    time.sleep(1)
                    if self.driver.current_url.find(self.login_url) == -1 \
                            and self.driver.current_url != self.base_url:
                        print "cookie登录成功！"
                        status = 1
        if status == 0:
            print "cookie登录失败，尝试正常登录！"
            self.login()
        self.g_tk = self.get_g_tk()

    def login(self):
        """登录，成功后写入cookie到本地"""
        self.driver.delete_all_cookies()
        # begin login
        login_frame = self.driver.find_element_by_id("login_frame")
        self.driver.switch_to_frame(login_frame)
        #方法一通过重新读取二维码并显示用手机扫描，失败
        #qr_url = self.driver.find_element_by_id('qrlogin_img').get_attribute('src')
        #qr_data = requests.get(qr_url).content
        #im = Image.open(StringIO.StringIO(qr_data))
        #im.show()
        #方法二输入帐号及密码，登录多次后会有验证
        #self.driver.find_element_by_id('switcher_plogin').click()
        #self.driver.find_element_by_id('u').send_keys(os.environ.get('num'))
        #self.driver.find_element_by_id('p').send_keys(os.environ.get('num_p'))
        #self.driver.find_element_by_id('login_button').send_keys(Keys.ENTER)
        # end
        while self.driver.current_url == self.base_url:
            time.sleep(1)
        # begin save cookie
        cookie_str = json.dumps(self.driver.get_cookies())
        open(self.cookie_file, 'wb').write(cookie_str)
        print "cookies已经保存到本地"
        # end

    def goto_photos(self):
        """进入空间好友相册"""
        import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        if self.driver.find_elements(BY.ID, 'welcomeflash'):
            self.driver.execute_script(self.dom_remove_by_js)
        btn_sure = self.get_ele('id', 'QM_Profile_Photo_A')
        if len(btn_sure) > 0:
            btn_sure[0].click()
        el = self.get_ele('class', 'menu_item_4')
        el[1].click()
        print "进入空间好友相册"
        self.sub_frame = self.get_ele('id', "tphoto", 0)

    def quit(self):
        self.driver.quit()

    def get_ele(self, etype, elestr, ismany=1, wait_time=10):
        """返回元素"""
        by_map = {
            'id': BY.ID,
            'xpath': BY.XPATH,
            'name': BY.NAME,
            'tag': BY.TAG_NAME,
            'class': BY.CLASS_NAME,
            'css': BY.CSS_SELECTOR
        }
        if ismany:
            return WebDriverWait(self.driver, wait_time).until(
                lambda x: x.find_elements(by_map[etype], elestr))
        else:
            return WebDriverWait(self.driver, wait_time).until(
                lambda x: x.find_element(by_map[etype], elestr))

    def scroll_to_end(self):
        """将相册页滚动条移到最下面"""
        self.driver.switch_to_default_content()
        while self.get_ele('tag', 'body', 0).get_attribute('haha') != 'blow':
            self.driver.execute_script(self.next_scroll_by_js.format(self.one_page_len))
            self.driver.execute_script(self.screen_blow_by_js)
            time.sleep(1)
        print "滚动条已到最底部"
        self.driver.execute_script(self.screen_origin_by_js)
        self.driver.switch_to_frame(self.sub_frame)

    def get_g_tk(self):
        """获取g_tk"""
        p_skey = self.driver.get_cookie('p_skey')['value']
        h = 5381
        for i in p_skey:
            h += (h<<5) + ord(i)
        print 'g_tk', h&2147483647
        return h&2147483647

    def get_friends(self):
        friends_str_json = None
        if os.path.exists(self.friends_file):
            with open(self.friends_file, 'rb') as f:
                friends_str_json = f.read().strip()
        if not friends_str_json:
            self.driver.get(self.friends_url.format(qq_num=self.userqq,
                                                    g_tk=self.g_tk))
            xx = self.get_ele('tag', 'body', 0).text.encode('utf8')
            friends_str_json = xx.replace(':""', ':"""').replace('""', '"')[11:-2]
            open(self.friends_file, 'wb').write(friends_str_json)
        self.friends_json = json.loads(friends_str_json)


def run_execute(ct, qqnum):
    # 进入好友空间
    ct.friendqq = str(qqnum) if type(qqnum) == type(1) else qqnum
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


if __name__ == "__main__":
    try:
        ct = Spider()
        ct.driver_init()
        for item in ct.friends_json['items']:
            if item['groupid'] in ALLOW_GROUPS:
                run_execute(ct, item['uin'])
    except Exception, e:
        traceback.print_exc()
