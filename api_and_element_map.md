# dom-map
编号 | 是否遗弃 | 作用 | 网址 | 元素类型 | 元素名
:-: | :-: | :-: | :-: | :-:
1 |  | 进入好友相册 | `https://user.qzone.qq.com/123456` | class | btn-fs-sure
2 | 已遗弃 | ～ | ～ | id | QM\_Profile\_Photo\_A

# 相册权限
属性字段：data-priv

值 | 说明
:-: | :-:
1 | 所有人可见
4 | qq好友可见
6 | 部分好友可见
8 | 部分好友可见（新）
3 | 仅自己可见
5 | 回答问题

# api-map
domain | path | apt-name | api-function | data-type | request-type
:-: | :-: | :-: | :-: | :-: | :-:
https://h5.qzone.qq.com | /proxy/domain/photo.qzone.qq.com/fcgi-bin/ | cgi_list_photo | 返回照片列表 | jsonp | GET
https://h5.qzone.qq.com | /proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/ | friend_show_qqfriends.cgi | 获取qq好友列表 | jsonp | GET


## 接口参数说明
### cgi_list_photo
1. g_tk：g_tk值
2. topicId：相册唯一id
3. mode：返回模式，0表示返回全部
4. pageNum：指定照片数量
5. sortOrder：排序方式，可省略
6. hostUin：目标qq号
7. uin：本机qq号
8. inCharset：指定编码格式，gbk
9. outCharset：指定编码格式，gbk

### friend_show_qqfriends.cgi
1. uin：本机qq号
2. g_tk：g_tk值
