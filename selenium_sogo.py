import asyncio
import logging
import re
import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from User_Agents import User_Agent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.chdir('/mnt/selenium')

columns = ['ID', 'type', 'title', 'intro', 'img', 'href', 'timestramp',
         'account', 'account_link', 'html', 'ori_href']


def save_subscription(subscription_dict):
    try:
        logging.info('正在保存公众号CSV文件...')
        subscriptions = []
        for name, pngurl in subscription_dict.items():
            wd.get(pngurl)
            sub_soup = BeautifulSoup(wd.page_source, 'html.parser')
            num = ''
            try:
                num = sub_soup.find('p', class_='profile_account').text.strip().replace("微信号:", "").strip()
            except Exception as e:
                pass
            subscriptions.append([name, num])
        subpf = pd.DataFrame(subscriptions, columns=['account', 'profile'], index=None)
        subpf.to_csv(os.getcwd() + '/subscriptionCsv/' + str(time.time()) + '.csv', encoding='utf-8', index=None)
    except Exception as e:
        logging.warning(e)


def subpage_content(href):
    wd.get(href)
    res = wd.page_source
    subpage_soup = BeautifulSoup(res, "html.parser")
    contents = subpage_soup.find('div', class_='rich_media_content')
    add = subpage_soup.findAll('div', class_='rich_media_tool')
    dic = {}
    try:
        dic['add'] = add[-1].a['href']
    except Exception:
        dic['add'] = ''
    if contents:
        contents = str(contents).replace("data-before-oversubscription-url", "src")
        contents = contents.replace("data-src", "src")
        dic['contents'] = contents
    else:
        dic['contents'] = ''
    return dic


async def save_pagehtml(contents, id):
    with open(os.getcwd() + '/pageHtml/' + id + '.html', 'wb') as pagehtml:
        pagehtml.write(contents.encode('utf-8'))


async def save_page(news_box):
    try:
        global catch_num
        error_num = 0
        page = []
        subscription_dict = {}
        page_id_list = []
        try:
            page_id_list = pd.read_csv(os.getcwd() + '/pageCsv/pages.csv', encoding='utf-8')['ID'].to_list()
        except Exception as e:
            logging.warning('找不到总文章索引CSV文件...', e)
        for ele in news_box:
            uig = re.compile(r'pc_([0-9]+?)_').findall(ele['id'])[0]
            logging.info("正在获取标签<" + textdict[uig] + ">的新闻...")
            for item in ele.find_all("li"):
                page_id = item['d'].split("-")[-1]
                if page_id not in page_id_list:
                    dic = subpage_content(item.find("a")['href'])
                    contents = dic['contents']
                    if contents:
                        catch_num += 1
                        pagedict = {
                            'id': page_id,
                            'uig': uig,
                            'title': item.find("h3").text.strip().encode('utf-8').decode('utf-8'),
                            'info': item.find("p").text.strip().encode('utf-8').decode('utf-8'),
                            'imgurl': item.find("img")['src'],
                            'pageurl': item.find("a")['href'],
                            'time': item.find(class_="s2")['t'],
                            'account': item.find(class_="account").text.strip().encode('utf-8').decode('utf-8'),
                            'accounturl': item.find(class_="account")['href'],
                            'add': dic['add']}
                        if pagedict['account'] not in subscription_dict:
                            subscription_dict[pagedict['account']] = pagedict['accounturl']
                        page.append([pagedict['id'], textdict[pagedict['uig']],
                                     pagedict['title'], pagedict['info'],
                                     pagedict['imgurl'], pagedict['pageurl'],
                                     pagedict['time'], pagedict['account'],
                                     pagedict['accounturl'], item['d'].split("-")[-1] + '.html',
                                     pagedict['add']])
                        await save_pagehtml(contents=contents, id=item['d'].split("-")[-1])
                        page_id_list.append(page_id)
            logging.info("共获取类别<" + textdict[uig] + ">文章：" + str(len(page)) + "篇，正在保存索引为CSV文件...")
            if len(page) == 0:
                error_num += 1
            if error_num >= 3:
                raise Exception('连续三次没有爬到内容，终止本次爬取...')
            pagedf = pd.DataFrame(page, columns=columns, index=None)
            pagedf.to_csv(os.getcwd() + '/pageCsv/' + str(uig) + '_' + str(time.time()) + '.csv', encoding='utf-8',
                          index=None)
            page = []
        save_subscription(subscription_dict)
    except Exception as e:
        logging.warning(e)


try:
    rua = User_Agent()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("user-agent=" + rua.get_agent())
    wd = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getcwd()+'/chromedriver')
    wd.get("https://weixin.sogou.com/")
    content = wd.page_source
    ajaxtext = re.compile(r'uigs="type_pc_([0-9]+?)">(.+?)<span>').findall(content)
    ajaxtext.insert(0, ('0', '热门'))
    textdict = {}
    catch_num = 0
    for index, text in ajaxtext:
        logging.info("正在完成第"+index+"页AJAX加载...")
        textdict[index] = text
        acur = wd.find_element_by_id('pc_'+index)
        wd.execute_script("document.getElementById('hide_tab').style.display='block'")
        acur.click()
        wait = WebDriverWait(wd, 2)
        while(True):
            try:
                look_more = wait.until(expected_conditions.presence_of_element_located((By.ID, 'look-more')))
                look_more.click()
            except Exception:
                break
    content = wd.page_source
    news_box = BeautifulSoup(content, "html.parser").find_all('div', class_='news-box')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(save_page(news_box=news_box))
except Exception as e:
    logging.warning(e)
finally:
    wd.quit()
    loop.close()
    logging.info('No.1阶段 爬取数据 共爬取文章' + str(catch_num) + ' done')
