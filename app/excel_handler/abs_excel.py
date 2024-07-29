import datetime
import time

import pandas as pd
import win32com.client as win32

import settings


class BaseExcelHandler:
    def __init__(self, filename):
        self.filename = filename
        self.excel = None
        self.dataframe = self.load_excel().iloc[:, 3:]

    def load_excel(self):
        self.refresh_save()
        return pd.read_excel(self.filename)
    
    def refresh_save(self):
        ctn = 0
        while True:
            try:
                if self.excel is None:
                    self.excel = win32.gencache.EnsureDispatch('Excel.Application')
                wb = self.excel.Workbooks.Open(self.filename)
                print(f'{self.filename}の外部接続を更新しています。')
                wb.RefreshAll()
                time.sleep(settings.REFRESH_WAIT_TIME)
                print('ファイルを保存しています。')
                wb.Save()
                wb.Close()
                self.excel.Quit()
                time.sleep(settings.SAVE_WAIT_TIME)
                # COMオブジェクトの解放
                if 'wb' in locals():
                    del wb
                if 'excel' in locals():
                    del self.excel
                break

            except Exception as exc:
                self.error = exc
                print(exc)
                # COMオブジェクトの解放
                if 'wb' in locals():
                    del wb
                if 'excel' in locals():
                    del self.excel
                ctn += 1
                print(f'ファイルの更新に失敗しました: {ctn}回目の再試行を行います。')
                if ctn >= settings.RETRY_COUNT:
                    print(f'{settings.RETRY_COUNT}回試行しましたが、失敗しました。')
                    time.sleep(3)
                    break
                continue
    
    def update_dataframe(self):
        self.dataframe = self.load_excel()
    
    def datetime_to_serial(self, dt, base_date=datetime.datetime(1899, 12, 30)):
        """
        datetimeオブジェクトをシリアル値に変換する。

        :param dt: 変換するdatetimeオブジェクト
        :param base_date: シリアル値の基準日（デフォルトは1899年12月30日）
        :return: シリアル値
        """
        dt = datetime.datetime(dt.year, dt.month, dt.day)
        return (dt - base_date).total_seconds() / (24 * 60 * 60)
    
    def serial_to_datetime(self, serial, base_date=datetime.datetime(1899, 12, 30)):
        """
        シリアル値をdatetimeオブジェクトに変換する。

        :param serial: 変換するシリアル値
        :param base_date: シリアル値の基準日（デフォルトは1899年12月30日）
        :return: datetimeオブジェクト
        """
        dt = datetime.datetime(dt.year, dt.month, dt.day)
        return base_date + dt.timedelta(days=serial)
    
    def current_time_to_serial(self, base_date=datetime.datetime(1899, 12, 30)):
        """
        現在日時をシリアル値に変換する。

        :return: シリアル値
        """
        current_time = datetime.datetime.now()
        serial_value = (current_time - base_date).total_seconds() / (24 * 60 * 60)
        return serial_value