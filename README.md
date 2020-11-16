# weibo_spyder_lite
一个简单的微博爬虫

## 使用方法
以我本人微博举例，我的ID是  2412924180  
>import weibo  
wb = weibo.WEIBO("2412924180")
user_info = wb.user_info()#用户信息
wb_data = wb.data(0) #0表示获取100条微博，最大获取为100 -1 表示获取10条微博，可用于增量更新
wb.set_cookies("你的cookies") #某些微博设置为登陆可见，所以抓取该类微博只能登录

## 即将完成
微博登录

## 作者介绍
Blog:[https:/www.wicos.me](歪克士)
Email:wicos@wicos.cn
