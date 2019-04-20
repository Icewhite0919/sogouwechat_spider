import logging
import os
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.chdir('/mnt/selenium')
columns = ['ID', 'type', 'title', 'intro', 'img', 'href', 'timestramp',
         'account', 'account_link', 'html', 'ori_href']

file_list = os.listdir(os.getcwd()+'/pageCsv')
try:
    file_list.remove('pages.csv')
    file_list.remove('db_pages.csv')
except Exception as e:
    logging.warning(e)
    logging.warning('找不到原文件...')
for file_name in file_list:
    pf_main = pd.DataFrame
    try:
        pf_main = pd.read_csv(os.getcwd() + '/pageCsv/pages.csv', encoding='utf-8')
    except Exception as e:
        logging.warning('创建新集合CSV文件...')
        pf_main = pd.DataFrame(columns=columns, index=None)
    pf_add = pd.read_csv(os.getcwd() + '/pageCsv/' + file_name, encoding='utf-8')
    pf_db_add = pd.DataFrame
    try:
        pf_db_add = pd.read_csv(os.getcwd() + '/pageCsv/db_pages.csv', encoding='utf-8')
    except Exception as e:
        logging.warning(e)
        logging.warning('打开文件异常...或目标CSV为空...')
        pf_db_add = pd.DataFrame(columns=columns, index=None)
    main_index = pf_main['ID'].to_list()
    for item in [pf_add.loc[index] for index in range(len(pf_add))]:
        if item.ID not in main_index:
            pf_main = pf_main.append(item, ignore_index=True)
            pf_db_add = pf_db_add.append(item, ignore_index=True)
            main_index.append(item.ID)
    pf_main.to_csv(os.getcwd() + '/pageCsv/pages.csv', encoding='utf-8', index=None)
    pf_db_add.to_csv(os.getcwd() + '/pageCsv/db_pages.csv', encoding='utf-8', index=None)
    os.remove(os.getcwd() + '/pageCsv/' + file_name)
    logging.info('已合并文件：' + file_name)
logging.info('No.2阶段 合并索引CSV文件 done')
