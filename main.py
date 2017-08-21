#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import ipdb, json, time, requests, os, StringIO, random
from dotenv import load_dotenv, find_dotenv
from useragent import user_agent_list as USER_AGENTS
load_dotenv(find_dotenv())
#from friends import friends
#from bs4 import BeautifulSoup as BS
def path_handle(photo_file):
    """
    对路径字符串进行安全处理，并新建文件夹，返回处理后的字符串
    """
    import re
    photo_file = re.sub(' ', '', photo_file)
    pf = os.path.split(photo_file)
    if not os.path.exists(pf[0]):
        os.makedirs(pf[0])
    return photo_file
def driver_init():
    """
    初始化浏览器并返回操作句柄
    """
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chromeOptions.add_experimental_option("prefs",prefs)
    chromeOptions.add_argument('lang=zh_CN.UTF-8')
    chromeOptions.add_argument(random.choice(USER_AGENTS))
    driver = webdriver.Chrome(executable_path=os.environ.get('chrome_path'),\
                            chrome_options=chromeOptions)
    driver.maximize_window()
    return driver
def write_cookie(cookie_file, driver):
    """
    读取cookie并写入浏览器
    """
    with open(cookie_file, 'rb') as f:
        cookie_read = f.read()
        if cookie_read.strip():
            driver.delete_all_cookies()
            try:
                for item in json.loads(cookie_read):
                    driver.add_cookie(item)
                driver.refresh()
            except Exception, e:
                print str(e)
def login(driver):
    """
    登录，成功后写入cookie到本地
    """
    driver.delete_all_cookies()
    # begin login
    login_frame = driver.find_element_by_id("login_frame")
    driver.switch_to_frame(login_frame)
    #方法一通过重新读取二维码并显示用手机扫描，失败
    #qr_url = driver.find_element_by_id('qrlogin_img').get_attribute('src')
    #qr_data = requests.get(qr_url).content
    #im = Image.open(StringIO.StringIO(qr_data))
    #im.show()
    #方法二输入帐号及密码，登录多次后会有验证
    #driver.find_element_by_id('switcher_plogin').click()
    #driver.find_element_by_id('u').send_keys(os.environ.get('num'))
    #driver.find_element_by_id('p').send_keys(os.environ.get('num_p'))
    #driver.find_element_by_id('login_button').send_keys(Keys.ENTER)
    # end
    while driver.current_url == base_url: time.sleep(1)
    # begin save cookie
    cookie_str = json.dumps(driver.get_cookies())
    open('website_cookie.json', 'wb').write(cookie_str)
    print "cookies已经保存到本地"
    # end
driver = driver_init()
cookie_file = 'website_cookie.json'
base_url = u'https://qzone.qq.com/'
driver.get(base_url)
print "检测并读取本地cookie"
if os.path.exists(cookie_file):
    write_cookie(cookie_file, driver)
if driver.current_url.find('i.qq.com') > -1 or driver.current_url == base_url:
    login(driver)
print '登录成功'
root_dir = 'friend_photo'
user = os.environ.get('num_f')
url = 'https://user.qzone.qq.com/'
screen_blow = """
var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
if(Math.abs(document.documentElement.scrollHeight - document.documentElement.clientHeight - scrollTop) < 10){
    document.getElementsByTagName('body')[0].setAttribute('haha', 'blow');
}
"""
screen_origin = "window.scrollTo(0,0);document.getElementsByTagName('body')[0].setAttribute('haha', 'origin');"
driver.get(url + user)
user_dir = root_dir + os.sep + driver.find_elements_by_class_name('textoverflow')[1].text
print "成功进入好友空间：", user, user_dir
btn_sure = driver.find_elements_by_class_name('btn-fs-sure')
if len(btn_sure) > 0: btn_sure[0].click()
el =  WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('menu_item_4'))
print "进入好友相册"
el[1].click()
time.sleep(1)
#driver.find_elements_by_class_name('menu_item_4')[1].click() #点击进入好友相册
sub_frame = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id("tphoto"))
driver.switch_to_frame(sub_frame)
select_ph = 0 #控制第几个相册
while select_ph < len(driver.find_elements_by_class_name('js-album-cover')):
    ph = driver.find_elements_by_class_name('js-album-cover')[select_ph]
    select_ph += 1
    photo_i = 0
    ph.click() #点击进入独立相册
    time.sleep(1)
    try:
        next_page = driver.find_element_by_id('pager_next_1') or -1
    except Exception:
        next_page = -1
    while next_page or next_page == -1:
        try:
            photo_name = driver.find_elements_by_class_name('j-pl-albuminfo-title')[1].text
        except Exception,e:
            photo_name = driver.find_element_by_css_selector('.profile .tit').text
        print "进入独立子相册:", photo_name
        photo_dir = user_dir + os.sep + photo_name
        driver.switch_to_default_content()
        while driver.find_element_by_tag_name('body').get_attribute('haha') != 'blow':
            driver.execute_script("window.scrollBy(0,500)")
            driver.execute_script(screen_blow)
            time.sleep(1)
        print "滚动条已到最底部"
        driver.execute_script(screen_origin)
        driver.switch_to_frame(sub_frame)
        imgs = driver.find_elements_by_class_name('j-pl-photoitem-img')
        if len(imgs) == 0:
            imgs = driver.find_elements_by_css_selector('.area-portrait-inner>a>img')
        imgs.reverse()
        titles = driver.find_elements_by_class_name('item-tit')
        titles.reverse()
        for i, img in enumerate(imgs):
            try:
                img_url = img.get_attribute('src').replace('/m/', '/b/') #s：小图，m：中图，b：大图
                r = requests.get(img_url)
            except Exception, e:
                print i, 'error'
                continue
            if r.status_code == 200:
                photo_i += 1
                photo_file = photo_dir + os.sep + '<' + str(photo_i) + '>' + (titles[i].text if len(titles) else '') + '.jpg'
                photo_file = path_handle(photo_file)
                print "%s : %d -----> %d" % (photo_file, i, len(imgs)-i)
                open(photo_file, 'wb+').write(r.content)
        if next_page != -1:
            next_page.click()
            try:
                next_page = driver.find_element_by_id('pager_next_1')
            except Exception:
                next_page = -1
        else:
            next_page = 0
    driver.find_elements_by_class_name('js-select')[0].click() #点击进入好友相册
driver.quit()
