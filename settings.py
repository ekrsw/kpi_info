import logging
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
WAIT_TIME = 30

# logger関係設定
LOG_FILE = 'appserver.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

# DataBase関係設定
DB_NAME = 'db.sqlite3'
REFRESH_WAIT_TIME = 6
SAVE_WAIT_TIME = 3
FILE_PATH = os.path.join(BASE_DIR, 'files')

# CTStageレポーター関係設定
REPORTER_URL = os.getenv('REPORTER_URL')
REPORTER_ID = os.getenv('REPORTER_ID')
HEADLESS_MODE = True
RETRY_COUNT = 3
DELAY = 3
TEMPLATE_SS = ['パブリック', '対応状況集計表用-SS']
TEMPLATE_TVS = ['パブリック', '対応状況集計表用-TVS']
TEMPLATE_KMN = ['パブリック', '対応状況集計表用-顧問先']
TEMPLATE_HHD = ['パブリック', '対応状況集計表用-HHD']

# Excelファイル関係設定
ACTIVITY_FILE = 'TS_todays_activity.xlsx'
CLOSE_FILE = 'TS_todays_close.xlsx'
SUPPORT_FILE = 'TS_todays_support.xlsx'

# API関係設定
API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')
