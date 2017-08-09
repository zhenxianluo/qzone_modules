#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import ipdb, json, time, requests, os
#from friends import friends
#from bs4 import BeautifulSoup as BS
cap = DesiredCapabilities.CHROME
cap["phantomjs.page.settings.resourceTimeout"] = 120
cap["phantomjs.page.settings.loadImages"] = False
driver = webdriver.Chrome(executable_path=r'/usr/local/bin/chromedriver', desired_capabilities=cap)
driver.maximize_window()
driver.get('https://qzone.qq.com/')
root_dir = 'friend_photo'
if not os.path.exists(root_dir):
    os.mkdir(root_dir)
user = '16415*9969'
url = 'https://user.qzone.qq.com/'
ipdb.set_trace()

screen_blow = """
var scrollTop = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
if(document.documentElement.scrollHeight == document.documentElement.clientHeight + scrollTop){
    document.getElementsByTagName('body')[0].setAttribute('haha', 'blow')
}
"""
driver.get(url + user)
user_dir = root_dir+os.sep+'rxx'
if not os.path.exists(user_dir):
    os.mkdir(user_dir)
btn_sure = driver.find_elements_by_class_name('btn-fs-sure')
if len(btn_sure) > 0: btn_sure[0].click()
driver.find_elements_by_class_name('menu_item_4')[1].click() #点击进入好友相册
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
    driver.switch_to_frame(sub_frame)
    imgs = driver.find_elements_by_class_name('j-pl-photoitem-img')
    for i, img in enumerate(imgs):
        try:
            r = requests.get(img.get_attribute('src').replace('/m/', '/b/'))
        except Exception, e:
            print i, 'error'
            continue
        if r.status_code == 200:
            open(user_dir+os.sep+str(i)+'.jpg', 'wb').write(r.content)
            i = i + 1
            print "you are download the %d photo, and also %d" % (i, len(imgs)-i)
    driver.switch_to_default_content()
    driver.execute_script("window.scrollTo(0,0)")
    driver.switch_to_frame(sub_frame)
    driver.find_elements_by_class_name('js-select')[0].click() #点击进入好友相册
driver.quit()
