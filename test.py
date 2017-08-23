#coding:utf8
import requests
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'b118.photo.store.qq.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
}
cookies = {
        #'pt2gguin':'o145120820',
        #'pgv_si':'s8748273664',
        #'ptisp':'ctc',
        #'uin':'o145120820',
        #'ptcz':'03bec135bf26d9e686a4785da7728e94867a22029f29b1bdb7de2f6ad47e999a',
        #'pgv_pvi':'74236707',
        #'pgv_pvid':'7099424190',
        #'skey':'@t6QluOZyi',
        #'RK':'X09XEl/+Si',
        #'pgv_info':'ssid=s8977350655',
        'rv2':'80108DE3C028D71BFAD6FB0483E2F7EA8EBC14BA476442B22D',
        'property20':'E9D0D2DCAFFD5BC0643129D39552325594A1FCF2478FA4C9E9400CE99D05584FCDDF15BE1208D803',
        'qq_photo_key':'4db8b73124a744908fce34ac08c24d51'
        }
url = 'http://b118.photo.store.qq.com/psbe?/V13E8m9v20Bxg7/idqmrN0ujPcOSsM5mPxCqssbEL4guVEwFnWn7Rk93ucRAB4kS4S4f1qoTXBc5QXE/b/dP0RXUaiBQAA&bo=gAJUAwAAAAABB*U!'
r = requests.get(url, cookies=cookies)
print r.content
open('haha.jpg', 'wb').write(r.content)
