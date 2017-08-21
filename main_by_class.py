#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import ipdb, json, time, requests, os, StringIO, random, re
from dotenv import load_dotenv, find_dotenv
from useragent import user_agent_list as USER_AGENTS
load_dotenv(find_dotenv())

class Spider(Object):
    def __init__(self):
        #cookie保存文件
        self.cookie_file = 'website_cookie.json'
        self.base_url = 'https://qzone.qq.com/'
        self.user_url = 'https://user.qzone.qq.com/'
        self.login_url = 'i.qq.com'
        self.driver = None
        #照片根目录
        self.root_dir = 'friend_photo'
        self.sub_frame = None
        self.screen_blow = """
            var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
            if(Math.abs(document.documentElement.scrollHeight - document.documentElement.clientHeight - scrollTop) < 10){
                document.getElementsByTagName('body')[0].setAttribute('haha', 'blow');
            }
        """
        self.screen_origin = "window.scrollTo(0,0);document.getElementsByTagName('body')[0].setAttribute('haha', 'origin');"

    def path_handle(self, photo_file):
        pass

    def driver_init(self)
        """初始化浏览器操作句柄"""
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images":2}
        chromeOptions.add_experimental_option("prefs",prefs)
        chromeOptions.add_argument('lang=zh_CN.UTF-8')
        chromeOptions.add_argument(random.choice(USER_AGENTS))
        self.driver = webdriver.Chrome(executable_path=os.environ.get('chrome_path'),\
                                chrome_options=chromeOptions)
        self.driver.maximize_window()

    def login_by_cookie(self):
        """读取cookie并写入浏览器"""
        if not os.path.exists(self.cookie_file):
            return 0
        with open(self.cookie_file, 'rb') as f:
            cookie_read = f.read()
            if cookie_read.strip():
                driver.delete_all_cookies()
                try:
                    for item in json.loads(cookie_read):
                        self.driver.add_cookie(item)
                except Exception, e:
                    print str(e)
                    return 0
                self.driver.refresh()
                time.sleep(1)
                if self.driver.current_url.find(self.login_url) > -1 or self.driver.current_url == self.base_url:
                    return 0
                return 1

    def login(self):
        """登录，成功后写入cookie到本地"""
        self.driver.delete_all_cookies()
        # begin login
        login_frame = driver.find_element_by_id("login_frame")
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
        while self.driver.current_url == self.base_url: time.sleep(1)
        # begin save cookie
        cookie_str = json.dumps(self.driver.get_cookies())
        open(self.cookie_file, 'wb').write(cookie_str)
        print "cookies已经保存到本地"
        # end

    def get_user(self, user, url=self.user_url):
        self.driver.get(url + user)

    def goto_photos(self):
        """进入空间好友相册"""
        btn_sure = driver.find_elements_by_class_name('btn-fs-sure')
        if len(btn_sure) > 0: btn_sure[0].click()
        el =  WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('menu_item_4'))
        print "进入空间好友相册"
        el[1].click()


if __name__ == "__main__":
    ct = Spider()
    ct.driver_init()
    if ct.login_by_cookie():
        print "cookie登录成功！"
    else:
        print "cookie登录失败，尝试正常登录！"
        ct.login()
    userqq = os.environ.get('num_f')
    ct.get_user(userqq)
    try:
        user_dir = ct.root_dir + os.sep + ct.driver.find_elements_by_class_name('textoverflow')[1].text
    except Exception:
        user_dir = ct.root_dir + os.sep + userqq
    ct.sub_frame = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id("tphoto"))
    ct.driver.switch_to_frame(ct.sub_frame)
    select_ph = 1 #控制第几个相册
