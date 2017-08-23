# dom-map
编号 | 作用 | 网址 | 元素类型 | 元素名
:-: | :-: | :-: | :-: | :-:
1 | 进入好友相册 | `https://user.qzone.qq.com/123456` | class | btn-fs-sure
 | ～ | ～ | id | QM_Profile_Photo_A

# api-map
domain | path | apt-name | api-function | data-type | request-type
:-: | :-: | :-: | :-: | :-: | :-:
https://h5.qzone.qq.com | /proxy/domain/photo.qzone.qq.com/fcgi-bin/ | cgi_list_photo | 返回照片列表 | jsonp | GET
https://h5.qzone.qq.com | /proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/ | friend_show_qqfriends.cgi | 获取qq好友列表 | jsonp | GET


# 接口参数说明
## cgi_list_photo
1. g_tk：g_tk值
2. topicId：相册唯一id
3. mode：返回模式，0表示返回全部
4. pageNum：指定照片数量
5. sortOrder：排序方式，可省略
6. hostUin：目标qq号
7. uin：本机qq号
8. inCharset：指定编码格式，gbk
9. outCharset：指定编码格式，gbk

## friend_show_qqfriends.cgi
1. uin：本机qq号
2. g_tk：g_tk值