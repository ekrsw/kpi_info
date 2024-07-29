import datetime
import os

from .abs_excel import BaseExcelHandler
import settings


today = datetime.date.today()

class SupportCase(BaseExcelHandler):
    def __init__(self, from_date, to_date, filename=os.path.join(settings.FILE_PATH, settings.SUPPORT_FILE)):
        super().__init__(filename)
        df = self.dataframe.copy()
        df = df.fillna('') # これを入れないとdf['かんたん！保守区分'] == ''が上手く判定されない

        # from_dateからto_dateの範囲のデータを抽出
        df = self.filtered_by_date_range(df, from_date, to_date)

        # 直受けの検索条件
        df = df[(df['受付タイプ'] == '直受け') | (df['受付タイプ'] == 'HHD入電（直受け）')]
        df = df[(df['顛末コード'] != '折返し不要・ｷｬﾝｾﾙ')]
        df = df[(df['顛末コード'] != 'ﾒｰﾙ・FAX回答（送信）')]
        df = df[(df['顛末コード'] != 'SRB投稿（要望）')]
        df = df[(df['顛末コード'] != 'ﾒｰﾙ・FAX文書（受信）')]
        df = df[(df['かんたん！保守区分'] == '会員') | (df['かんたん！保守区分'] == '')]
        df = df[(df['回答タイプ'] != '2次T転送')]

        # グループ別に分割
        self.df_direct_ss = df[df['サポート区分'] == 'SS']
        self.df_direct_tvs = df[df['サポート区分'] == 'TVS']
        self.df_direct_kmn = df[df['サポート区分'] == '顧問先']
        self.df_direct_hhd = df[df['サポート区分'] == 'HHD']

        # 留守電の検索条件
        df = self.dataframe.copy()
        df = df.fillna('') # これを入れないとdf['かんたん！保守区分'] == ''が上手く判定されない
        # from_dateからto_dateの範囲のデータを抽出
        df = self.filtered_by_date_range(df, from_date, to_date)
        df = df[df['受付タイプ'] == '留守電']
        df = df[(df['顛末コード'] != '折返し不要・ｷｬﾝｾﾙ')]
        df = df[(df['顛末コード'] != 'ﾒｰﾙ・FAX回答（送信）')]
        df = df[(df['顛末コード'] != 'SRB投稿（要望）')]
        df = df[(df['顛末コード'] != 'ﾒｰﾙ・FAX文書（受信）')]

        # グループ別に分割
        self.df_ivr_ss = df[df['サポート区分'] == 'SS']
        self.df_ivr_tvs = df[df['サポート区分'] == 'TVS']
        self.df_ivr_kmn = df[df['サポート区分'] == '顧問先']
        self.df_ivr_hhd = df[df['サポート区分'] == 'HHD']
    
    def filtered_by_date_range(self, df, from_date, to_date):
        # from_dateからto_dateの範囲のデータを抽出
        from_date_serial = self.datetime_to_serial(from_date)
        
        to_date_serial = self.datetime_to_serial(to_date + datetime.timedelta(days=1))
        
        df = df[(df['登録日時'] >= from_date_serial) & (df['登録日時'] < to_date_serial)]
        df = df.reset_index(drop=True)
        return df
