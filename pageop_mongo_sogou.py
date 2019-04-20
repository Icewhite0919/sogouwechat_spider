import logging

from pymongo import MongoClient
import pandas as pd
import os
import asyncio

os.chdir('/mnt/selenium')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def get_html(d):
    with open(d, 'rb') as f:
        return f.read().decode('utf-8')


async def db_save(db, dic):
    logging.info('保存新文章：' + dic['_id'])
    db['weixin_page'].insert_one(dic)
    return None


async def page_save():
    try:
        client = MongoClient('mongodb://icewhite:8729305266YxL@120.79.177.232:20177')
        db = client.tzo
        pf_db_add = pd.read_csv(os.getcwd() + '/pageCsv/db_pages.csv', encoding='utf-8')
        insert_num = 0
    except Exception as e:
        logging.warning(e)
    try:
        for index in range(len(pf_db_add)):
            item = pf_db_add.loc[index].to_dict()
            item['_id'] = item.pop('ID')
            item['html'] = await get_html(os.getcwd() + '/pageHtml/' + item.pop('html'))
            item.pop('href')
            item.pop('account_link')
            item['timestramp'] = str(item['timestramp'])
            try:
                await db_save(db=db, dic=item)
                insert_num += 1
            except Exception as e:
                logging.warning(e)
            pf_db_add = pf_db_add.drop(index=index)
    except Exception as e:
        logging.warning(e)
    finally:
        pf_db_add.to_csv(os.getcwd() + '/pageCsv/db_pages.csv', encoding='utf-8')
        logging.info('本次共插入' + str(insert_num) + '篇文章...')


logging.info('No.3阶段：合并数据库 done')
loop = asyncio.get_event_loop()
loop.run_until_complete(page_save())
loop.close()
