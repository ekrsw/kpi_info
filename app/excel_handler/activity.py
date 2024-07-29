import datetime
import os
import pandas as pd

from .abs_excel import BaseExcelHandler
import settings

today = datetime.date.today()

class Activity(BaseExcelHandler):
    def __init__(self, from_date, to_date, filename=os.path.join(settings.FILE_PATH, settings.ACTIVITY_FILE)):
        self.from_date = from_date
        self.to_date = to_date
        super().__init__(filename)
        df = self.dataframe.copy()
        # 件名に「【受付】」が含まれていないもののみ残す
        df['件名'] = df['件名'].astype(str)
        df = df[~df['件名'].str.contains('【受付】', na=False)]

        # from_dateからto_dateの範囲のデータを抽出
        df = self.filtered_by_date_range(df, self.from_date, self.to_date)

        # 案件番号でソートし、最も早い日時を残して重複を削除
        df = df.sort_values(by=['案件番号 (関連) (サポート案件)', '登録日時'])
        df = df.drop_duplicates(subset='案件番号 (関連) (サポート案件)', keep='first')

        # サポート案件の登録日時と、活動の登録日時をPandas Datetime型に変換して、差分を'時間差'カラムに格納
        df['時間差'] = (df['登録日時'] - df['登録日時 (関連) (サポート案件)'])
        df['時間差'] = df['時間差'].fillna(0.0)

        # 受付タイプが折返しor留守電のものを抽出
        _df_ss_tvs_kmn = df[(df['受付タイプ (関連) (サポート案件)'] == '折返し') | (df['受付タイプ (関連) (サポート案件)'] == '留守電')]
        _df_hhd = df[(df['受付タイプ (関連) (サポート案件)'] == 'HHD入電（折返し）') | (df['受付タイプ (関連) (サポート案件)'] == '留守電')]

        df_ss = _df_ss_tvs_kmn[(_df_ss_tvs_kmn['サポート区分 (関連) (サポート案件)'] == 'SS')]
        df_tvs = _df_ss_tvs_kmn[(_df_ss_tvs_kmn['サポート区分 (関連) (サポート案件)'] == 'TVS')]
        df_kmn = _df_ss_tvs_kmn[(_df_ss_tvs_kmn['サポート区分 (関連) (サポート案件)'] == '顧問先')]
        df_hhd = _df_hhd[(_df_hhd['サポート区分 (関連) (サポート案件)'] == 'HHD')]

        # グループ別に分割
        self.df_cb_0_20_ss, self.df_cb_20_30_ss, self.df_cb_30_40_ss, self.df_cb_40_60_ss, self.df_cb_60over_ss, self.df_cb_not_include_ss = self.callback_classification_by_group(df_ss)
        self.df_cb_0_20_tvs, self.df_cb_20_30_tvs, self.df_cb_30_40_tvs, self.df_cb_40_60_tvs, self.df_cb_60over_tvs, self.df_cb_not_include_tvs = self.callback_classification_by_group(df_tvs)
        self.df_cb_0_20_kmn, self.df_cb_20_30_kmn, self.df_cb_30_40_kmn, self.df_cb_40_60_kmn, self.df_cb_60over_kmn, self.df_cb_not_include_kmn = self.callback_classification_by_group(df_kmn)
        self.df_cb_0_20_hhd, self.df_cb_20_30_hhd, self.df_cb_30_40_hhd, self.df_cb_40_60_hhd, self.df_cb_60over_hhd, self.df_cb_not_include_hhd = self.callback_classification_by_group(df_hhd)

    def callback_classification_by_group(self, df):
        towenty_minutes = 0.0138888888888889
        thirty_minutes = 0.0208333333333333
        forty_minutes = 0.0277777777777778
        sixty_minutes = 0.0416666666666667

        df_cb_0_20 = df[(df['時間差'] <= towenty_minutes)]
        df_cb_20_30 = df[(df['時間差'] > towenty_minutes) & (df['時間差'] <= thirty_minutes)]
        df_cb_30_40 = df[(df['時間差'] > thirty_minutes) & (df['時間差'] <= forty_minutes)]
        df_cb_40_60 = df[(df['時間差'] > forty_minutes) & (df['時間差'] <= sixty_minutes) & (df['指標に含めない (関連) (サポート案件)'] == 'いいえ')]
        df_cb_60over = df[(df['時間差'] > sixty_minutes) & (df['指標に含めない (関連) (サポート案件)'] == 'いいえ')]
        df_cb_not_include =df[(df['時間差'] > sixty_minutes) & (df['指標に含めない (関連) (サポート案件)'] == 'はい')]

        return df_cb_0_20, df_cb_20_30, df_cb_30_40, df_cb_40_60, df_cb_60over, df_cb_not_include
    
    def filtered_by_date_range(self, df, from_date, to_date):
        # from_dateからto_dateの範囲のデータを抽出
        from_date_serial = self.datetime_to_serial(from_date)
        
        to_date_serial = self.datetime_to_serial(to_date + datetime.timedelta(days=1))
        
        df = df[(df['登録日時 (関連) (サポート案件)'] >= from_date_serial) & (df['登録日時 (関連) (サポート案件)'] < to_date_serial)]
        df = df.reset_index(drop=True)
        return df

    def convert_to_pending_num(self, df):
        towenty_minutes = 0.0138888888888889
        thirty_minutes = 0.0208333333333333
        forty_minutes = 0.0277777777777778
        sixty_minutes = 0.0416666666666667

        df_wfc_over_20 = df[df['お待たせ時間'] >= towenty_minutes]
        df_wfc_over30 = df[df['お待たせ時間'] >= thirty_minutes]
        df_wfc_over40 = df[df['お待たせ時間'] >= forty_minutes]
        df_wfc_over60 = df[df['お待たせ時間'] >= sixty_minutes]

        return df_wfc_over_20, df_wfc_over30, df_wfc_over40, df_wfc_over60

    def waiting_for_callback(self):
        df = self.dataframe.copy()
        # 受付けタイプ「直受け」「折返し」「留守電」のみ残す
        df = df[(df['受付タイプ (関連) (サポート案件)'] == '折返し') | (df['受付タイプ (関連) (サポート案件)'] == '留守電')]

        # 指標に含めないが「いいえ」のもののみ残す
        df = df[df['指標に含めない (関連) (サポート案件)'] == 'いいえ']

        df = df[(df['顛末コード (関連) (サポート案件)'] == '対応中') | (df['顛末コード (関連) (サポート案件)'] == '対応待ち')]

        # 件名に「【受付】」が含まれているもののみ残す。
        df['件名'] = df['件名'].astype(str) 
        contains_df = df[df['件名'] == '【受付】']
        uncontains_df = df[df['件名'] != '【受付】']

        only_contains_df = pd.merge(contains_df, uncontains_df, on='案件番号 (関連) (サポート案件)', how='outer', indicator=True)
        result = only_contains_df[only_contains_df['_merge'] == 'left_only']
        s = result['案件番号 (関連) (サポート案件)'].unique()
        df = df[df['案件番号 (関連) (サポート案件)'].isin(s)]

        # 案件番号、登録日時でソート
        df.sort_values(by=['案件番号 (関連) (サポート案件)', '登録日時'], inplace=True)

        # 同一案件番号の最初の活動のみ残して他は削除  
        df.drop_duplicates(subset='案件番号 (関連) (サポート案件)', keep='first', inplace=True)
        
        # サポート案件の登録日時と、活動の登録日時をPandas Datetime型に変換して、差分を'お待たせ時間'カラムに格納、NaNは０変換
        current_serial = self.current_time_to_serial()
        df['お待たせ時間'] = (current_serial - df['登録日時 (関連) (サポート案件)'])

        df = self.filtered_by_date_range(df, self.from_date, self.to_date)
        df = df.reset_index(drop=True)

        df_ss = df[(df['サポート区分 (関連) (サポート案件)'] == 'SS')]
        df_tvs = df[(df['サポート区分 (関連) (サポート案件)'] == 'TVS')]
        df_kmn = df[(df['サポート区分 (関連) (サポート案件)'] == '顧問先')]
        df_hhd = df[(df['サポート区分 (関連) (サポート案件)'] == 'HHD')]

        
        self.df_wfc_over20_ss, self.df_wfc_over30_ss, self.df_wfc_over40_ss, self.df_wfc_over60_ss = self.convert_to_pending_num(df_ss)
        self.df_wfc_over20_tvs, self.df_wfc_over30_tvs, self.df_wfc_over40_tvs, self.df_wfc_over60_tvs = self.convert_to_pending_num(df_tvs)
        self.df_wfc_over20_kmn, self.df_wfc_over30_kmn, self.df_wfc_over40_kmn, self.df_wfc_over60_kmn = self.convert_to_pending_num(df_kmn)
        self.df_wfc_over20_hhd, self.df_wfc_over30_hhd, self.df_wfc_over40_hhd, self.df_wfc_over60_hhd = self.convert_to_pending_num(df_hhd)

