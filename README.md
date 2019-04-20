# 301工程小队_搜狗公众号文章

## 介绍
爬取搜狗微信公众号文章的体系，将实现爬取、部署、合并csv、更新数据库等操作
### 实际部署环境
1. ubuntu x64 18.04 服务器版本 + nohup & 不挂断运行任务指令 + crontab守护进程  
例如：0 */3 * * * nohup python selenium_sogou.py 2>>tzo_spider_error.log 1>>tzo_spider.log &  
表示每3小时后台不挂断运行一次爬虫程序，标准错误定向到tzo_spider_error.log文件，标准输入输出定向到tzo_spider.log文件  
详情请搜索crontab、nohup，就懂啦
2. ubuntu下使用无界google-chrome的方法  
参考链接：(https://blog.csdn.net/qq_29303759/article/details/83719285)  
然后对应到代码就可以啦，特别提醒，在本程序中以下四行代码可以解决很多问题：
```
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
```
### Python模块
1. selenium_sogou.py  
模块的爬取路线:从首页ajax模拟加载保存为csv文件==>文章详情页保存为html文件==>公众号微信号保存为csv文件。  
目前公众号微信号的爬取还有点问题，有可能是爬取速度太快导致被检测无法继续爬取。
2. merge_csv_sogou.py  
该模块用来对文章索引和基本信息（不包括文章内容）的csv文件进行整合，并找出没有更新到数据库的文章，便于pageop_mongo_sogou.py模块进行数据库的更新，整合后的索引csv文件pages.csv还可以给selenium_sogou.py模块优化速度和请求量，对已经爬取过的文章跳过打开文章详情页的过程，防止被反爬。
3. pageop_mongo_sogou.py  
该模块利用merge_csv_sogou.py模块整合的索引csv文件db_pages.csv对保存为html文件的文章读取并和基本信息写入mongodb数据库。
### 文件夹
1. pageCsv  
保存了每次爬取文章的索引和基本信息（不包括文章内容）csv文件，主要有三种形式：  
>>[pages.csv]保存了所有文章的索引  
>>[db_pages.csv]保存了未存入数据库的文章索引  
>>[u_xxxxxx.csv]保存了在时间戳为xxxxxx的第u个标签下的文章索引
2. pageHtml  
保存了每次爬取文章的内容，存为html文件，以爬取的文章ID命名
3. suscriptionCsv  
保存了每次进行爬取后所涉及到的公众号及微信号（该文件夹的体系目前有些问题，还未解决，以及需要编写合并程序和存数据库程序）
