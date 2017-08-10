#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import ipdb, json, time, requests, os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
#from friends import friends
#from bs4 import BeautifulSoup as BS
chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
#driver = webdriver.Chrome(executable_path=r'/usr/local/bin/chromedriver',\
#                          chrome_options=chromeOptions)
driver = webdriver.Chrome(executable_path=os.environ.get('chrome_path'),\
                          chrome_options=chromeOptions)
driver.maximize_window()
cookie_file = 'website_cookie.json'
base_url = u'https://qzone.qq.com/'
driver.get(base_url)
if os.path.exists(cookie_file):
    with open(cookie_file, 'rb') as f:
        cookie_read = f.read()
        if cookie_read:
            driver.delete_all_cookies()
            for item in json.loads(cookie_read):
                driver.add_cookie(item)
            driver.refresh()
            time.sleep(5)
if driver.current_url == base_url:
    driver.delete_all_cookies()
    # begin login
    login_frame = driver.find_element_by_id("login_frame")
    driver.switch_to_frame(login_frame)
    driver.find_element_by_id('switcher_plogin').click()
    driver.find_element_by_id('u').send_keys(os.environ.get('num'))
    driver.find_element_by_id('p').send_keys(os.environ.get('num_p'))
    driver.find_element_by_id('login_button').send_keys(Keys.ENTER)
    # end
    while driver.current_url == base_url: time.sleep(1)
    # begin save cookie
    cookie_str = json.dumps(driver.get_cookies())
    open('website_cookie.json', 'ab').write(cookie_str)
    # end
root_dir = 'friend_photo'
if not os.path.exists(root_dir):
    os.mkdir(root_dir)
user = os.environ.get('num_f')
url = 'https://user.qzone.qq.com/'
screen_blow = """
var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
if(document.documentElement.scrollHeight == document.documentElement.clientHeight + scrollTop){
    document.getElementsByTagName('body')[0].setAttribute('haha', 'blow')
}
"""
screen_origin = "document.getElementsByTagName('body')[0].setAttribute('haha', 'origin')"
driver.get(url + user)
user_dir = root_dir + os.sep + driver.find_elements_by_class_name('textoverflow')[1].text
if not os.path.exists(user_dir):
    os.mkdir(user_dir)
btn_sure = driver.find_elements_by_class_name('btn-fs-sure')
if len(btn_sure) > 0: btn_sure[0].click()
el =  WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('menu_item_4'))
el[1].click()
#driver.find_elements_by_class_name('menu_item_4')[1].click() #点击进入好友相册
sub_frame = driver.find_element_by_id("tphoto")
driver.switch_to_frame(sub_frame)
select_ph = 0
while select_ph < len(driver.find_elements_by_class_name('js-album-cover')):
    ph = driver.find_elements_by_class_name('js-album-cover')[select_ph]
    select_ph += 1
    i=0
    ph.click() #点击进入独立相册
    driver.switch_to_default_content()
    while driver.find_element_by_tag_name('body').get_attribute('haha') != 'blow':
        driver.execute_script("window.scrollBy(0,500)")
        driver.execute_script(screen_blow)
        time.sleep(0.5)
    driver.execute_script(screen_origin)
    driver.execute_script("window.scrollTo(0,0)")
    driver.switch_to_frame(sub_frame)
    imgs = driver.find_elements_by_class_name('j-pl-photoitem-img')
    for i, img in enumerate(imgs):
        try:
            #r = requests.get(img.get_attribute('src').replace('/m/', '/b/'))
        except Exception, e:
            print i, 'error'
            continue
        if r.status_code == 200:
            #open(user_dir+os.sep+str(i)+'.jpg', 'wb').write(r.content)
            i = i + 1
            print "you are download the %d photo, and also %d" % (i, len(imgs)-i)
    driver.find_elements_by_class_name('js-select')[0].click() #点击进入好友相册
driver.quit()
