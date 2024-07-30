import os
import pandas as pd
import time

# Webスクレイピング関係ライブラリ
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import settings


class BaseReporter(object):
    def __init__(self):
        self.url = settings.REPORTER_URL
        self.id = settings.REPORTER_ID

        options = Options()

        # ブラウザを表示させない。
        if settings.HEADLESS_MODE:
            options.add_argument('--headless')
        
        # コマンドプロンプトのログを表示させない。
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # headlessモードでもダウンロードできるようにする設定
        options.add_experimental_option('prefs', {'download.prompt_for_download': False})

        # headlessモードでもダウンロードできるようにする設定
        self.download_path = 'C:\\Users\\{}\\Downloads'.format(os.getlogin())
        self.driver = webdriver.Chrome(options=options)
        self.should_close = True

        self.driver.command_executor._commands["send_command"] = (
            'POST',
            '/session/$sessionId/chromium/send_command'
        )
        self.driver.execute(
            'send_command',
            params={
                'cmd': 'Page.setDownloadBehavior',
                'params': {'behavior': 'allow', 'downloadPath': self.download_path}
            }
        )

        self.driver.implicitly_wait(5)

    
    def login(self):
        """レポータに接続してログイン"""
        self.driver.get(self.url)
        self.driver.find_element(By.ID, 'logon-operator-id').send_keys(self.id)
        self.driver.find_element(By.ID, 'logon-btn').click()

    def call_template(self, template, from_date, to_date) -> None:
        """テンプレート呼び出し、指定の集計期間を表示"""

        self.login()

        # テンプレート呼び出し
        self.driver.find_element(By.ID, 'template-title-span').click()
        el1 = self.driver.find_element(By.ID, 'download-open-range-select')
        s1 = Select(el1)
        s1.select_by_visible_text(template[0])
        el2 = self.driver.find_element(By.ID, 'template-download-select')
        s2 = Select(el2)
        s2.select_by_value(template[1])
        self.driver.find_element(By.ID, 'template-creation-btn').click()

        # 集計期間のfromをクリアしてfrom_dateを送信
        self.driver.find_element(By.ID, 'panel-td-input-from-date-0').send_keys(Keys.CONTROL + 'a')
        self.driver.find_element(By.ID, 'panel-td-input-from-date-0').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'panel-td-input-from-date-0').send_keys(from_date.strftime('%Y/%m/%d'))

        # 集計期間のtoをクリアしてto_dateを送信
        self.driver.find_element(By.ID, 'panel-td-input-to-date-0').send_keys(Keys.CONTROL + 'a')
        self.driver.find_element(By.ID, 'panel-td-input-to-date-0').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'panel-td-input-to-date-0').send_keys(to_date.strftime('%Y/%m/%d'))

        # レポート作成
        self.driver.find_element(By.ID, 'panel-td-create-report-0').click()
        time.sleep(2)

    def change_tabs(self, from_date, to_date):
        self.driver.find_element(By.ID, 'normal-title2').click()
        # 集計期間のfromをクリアしてfrom_dateを送信
        self.driver.find_element(By.ID, 'panel-td-input-from-date-1').send_keys(Keys.CONTROL + 'a')
        self.driver.find_element(By.ID, 'panel-td-input-from-date-1').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'panel-td-input-from-date-1').send_keys(from_date.strftime('%Y/%m/%d'))

        # 集計期間のtoをクリアしてto_dateを送信
        self.driver.find_element(By.ID, 'panel-td-input-to-date-1').send_keys(Keys.CONTROL + 'a')
        self.driver.find_element(By.ID, 'panel-td-input-to-date-1').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'panel-td-input-to-date-1').send_keys(to_date.strftime('%Y/%m/%d'))
        
        # レポート作成
        self.driver.find_element(By.ID, 'panel-td-create-report-1').click()
        time.sleep(2)

    def create_dataframe(self, soup, list_name) -> pd.DataFrame:

        data_table = []

        # headerのリストを作成
        header_table = soup.find(id=f'{list_name}-table-head-table')
        xmp = header_table.thead.tr.find_all('xmp')
        header_list = [i.string for i in xmp]
        data_table.append(header_list)

        # bodyのリストを作成
        body_table = soup.find(id=f'{list_name}-table-body-table')
        tr = body_table.tbody.find_all('tr')
        for td in tr:
            xmp = td.find_all('xmp')
            row = [i.string for i in xmp]
            data_table.append(row)
        
        # テーブルをDataFrameに変換
        df = pd.DataFrame(data_table[1:], columns=data_table[0])
        df.set_index(df.columns[0], inplace=True)
        return df
    
    def close(self):
        if hasattr(self, 'driver'):
            self.driver.close()