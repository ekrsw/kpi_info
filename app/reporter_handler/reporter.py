import datetime
import time

from bs4 import BeautifulSoup

from .abs_reporter import BaseReporter
import settings


class Reporter(BaseReporter):
    def __init__(self, template, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = template
        self.df_incomming = None
        self.df_section = None

    @staticmethod
    def get_table_as_dataframe_incomming_and_section(template: list,
                                                     start_date: datetime.date,
                                                     end_date: datetime.date) -> None:
        """レポータ-対応状況集計表用テンプレートを表示して、着信分析とグループ分析のデータを取得する。

        Args:
            template (list): レポータ-対応状況集計表用テンプレート
            from_date(datetime): 集計期間のfrom
            to_date(datetime): 集計期間のto
        """

        cnt = 0
        while cnt <= settings.RETRY_COUNT:
            try:
                reporter = Reporter(template)
                
                reporter.call_template(template, start_date, end_date)

                html = reporter.driver.page_source.encode('utf-8')
                soup = BeautifulSoup(html, 'lxml')
                reporter.df_incomming = reporter.create_dataframe(soup, 'normal-list1-dummy-0')

                reporter.change_tabs(start_date, end_date)
                html = reporter.driver.page_source.encode('utf-8')
                soup = BeautifulSoup(html, 'lxml')

                reporter.df_section = reporter.create_dataframe(soup, 'normal-list2-dummy-1')
                reporter.close()
                return reporter

            except Exception as exc:
                print(exc)
                if cnt == settings.RETRY_COUNT:
                    print(f'{settings.RETRY_COUNT}回試行しましたが、失敗しました。')
                    reporter.close()
                    break
                cnt += 1
                time.sleep(settings.DELAY)
                reporter.close()
                continue


