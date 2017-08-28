# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By as BY
import ipdb, json, time, requests, os, StringIO, random, re, traceback
from dotenv import load_dotenv, find_dotenv
from useragent import user_agent_list as USER_AGENTS
load_dotenv(find_dotenv())
# 默认等待时间，单位秒
DEFAULT_WAIT_TIME = 60
# 是否显示图片，1为显示，2为不显示
IS_SHOW_IMG = 2

class Base_class(object):
    """基础程序类"""
    def __init__(self):
        # cookie保存文件
        self.cookie_file = 'website_cookie.json'
        self.friends_file = 'qqfriends.json'
        self.base_url = u'https://qzone.qq.com/'
        self.user_url = u'https://user.qzone.qq.com/'
        self.login_url = u'i.qq.com'
        # 照片根目录
        self.driver = None
        self.user_dir = None
        self.g_tk = None
        self.friends_json = None
        self.cookies = {}
        self.sub_frame = None
        self.friends_url = ('https://h5.qzone.qq.com/proxy/domain/'
                            'r.qzone.qq.com/cgi-bin/tfriend/'
                            'friend_show_qqfriends.cgi?'
                            'uin={qq_num}&g_tk={g_tk}')
        self.one_page_len = '500'
        self.userqq = os.environ.get('num')
        self.userpwd = os.environ.get('num_p')
        self.chrome_path = os.environ.get('chrome_path')
        self.screen_blow_by_js = """
            var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
            if(Math.abs(document.documentElement.scrollHeight - document.documentElement.clientHeight - scrollTop) < 10){
                document.getElementsByTagName('body')[0].setAttribute('haha', 'blow');
            }
        """
        self.screen_origin_by_js = "window.scrollTo(0,0);document.getElementsByTagName('body')[0].setAttribute('haha', 'origin');"
        self.next_scroll_by_js = "window.scrollBy(0,{})"
        self.dom_remove_by_js = """
            var btn = document.getElementById("welcomeflash");
            btn.click();
        """
        self.by_map = {
            'id': BY.ID,
            'xpath': BY.XPATH,
            'name': BY.NAME,
            'tag': BY.TAG_NAME,
            'class': BY.CLASS_NAME,
            'css': BY.CSS_SELECTOR
        }

    def driver_init(self):
        """初始化浏览器操作句柄"""
        chromeOptions = webdriver.ChromeOptions()
        # 值为2时不加载图片
        prefs = {"profile.managed_default_content_settings.images": IS_SHOW_IMG}
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.add_argument('--allow-running-insecure-content')
        chromeOptions.add_argument('--disable-web-security')
        chromeOptions.add_argument('--disk-cache-dir={}'.format(
            os.path.join(os.getcwd() + 'selenium-chrome-cache')))
        chromeOptions.add_argument('--no-referrers')
        #chromeOptions.add_argument('--proxy-server=localhost:8118')
        chromeOptions.add_argument('lang=zh_CN.UTF-8')
        chromeOptions.add_argument(random.choice(USER_AGENTS))
        self.driver = webdriver.Chrome(
            executable_path=self.chrome_path,
            chrome_options=chromeOptions)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(DEFAULT_WAIT_TIME)
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
        # 方法一通过重新读取二维码并显示用手机扫描，失败
        #qr_url = self.driver.find_element_by_id('qrlogin_img').get_attribute('src')
        #qr_data = requests.get(qr_url).content
        #im = Image.open(StringIO.StringIO(qr_data))
        #im.show()
        # 方法二输入帐号及密码，登录多次后会有验证
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').send_keys(os.environ.get('num'))
        self.driver.find_element_by_id('p').send_keys(os.environ.get('num_p'))
        self.driver.find_element_by_id('login_button').send_keys(Keys.ENTER)
        # end
        while self.driver.current_url == self.base_url \
                or self.driver.current_url.find(self.login_url) > -1:
            time.sleep(1)
        # begin save cookie
        cookie_str = json.dumps(self.driver.get_cookies())
        open(self.cookie_file, 'wb').write(cookie_str)
        print "cookies已经保存到本地"
        # end

    def get_g_tk(self):
        """获取g_tk"""
        p_skey = self.driver.get_cookie('p_skey')['value']
        h = 5381
        for i in p_skey:
            h += (h<<5) + ord(i)
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

    def get_ele(self, etype, elestr, ismany=1, wait_time=DEFAULT_WAIT_TIME):
        """返回元素"""
        if ismany:
            return WebDriverWait(self.driver, wait_time).until(
                lambda x: x.find_elements(self.by_map[etype], elestr))
        else:
            return WebDriverWait(self.driver, wait_time).until(
                lambda x: x.find_element(self.by_map[etype], elestr))

    def cookies_to_dict(self):
        for item in self.driver.get_cookies():
            self.cookies[item['name']] = item['value']

    def quit(self):
        self.driver.quit()

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

    def default_click(self):
        welcomeflash = self.driver.find_elements(self.by_map['id'], 'welcomeflash')
        if welcomeflash:
            self.driver.execute_script(self.dom_remove_by_js)
        btn_sure =  self.driver.find_elements(self.by_map['class'], 'btn-fs-sure')
        if btn_sure:
            btn_sure[0].click()

