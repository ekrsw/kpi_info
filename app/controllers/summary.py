import datetime
import json
import pandas as pd
import requests

from app.excel_handler.activity import Activity
from app.excel_handler.support_case import SupportCase
from app.reporter_handler.reporter import Reporter
import settings


class Summary:
    def __init__(self, group_name: str):
        if group_name == 'SS':
            template = settings.TEMPLATE_SS
        elif group_name == 'TVS':
            template = settings.TEMPLATE_TVS
        elif group_name == '顧問先':
            template = settings.TEMPLATE_KMN
        elif group_name == 'HHD':
            template = settings.TEMPLATE_HHD
        else:
            raise ValueError('Invalid group_name. Please input SS, TVS, 顧問先, or HHD.')
        
        today = datetime.date.today()
        support_case = SupportCase(today, today)
        activity = Activity(today, today)
        activity.waiting_for_callback()
        reporter = Reporter.get_table_as_dataframe_incomming_and_section(template, today, today)

        # 各種指標をクラス変数に追加
        # 11_総着信数 (int): reporter_着信数
        self.total_calls = int(reporter.df_incomming['総着信数'].sum())
        # 12_自動音声ガイダンス途中切断数 (int): reporter_IVR応答前放棄呼数 + reporter_IVR切断数
        self.ivr_interruptions = int(reporter.df_incomming['IVR応答前放棄呼数'].sum()) + int(reporter.df_incomming['IVR切断数'].sum())
        # 14_オペレーター呼出途中放棄数 (int): reporter_ACD放棄呼数
        self.abandoned_during_operator = int(reporter.df_section['ACD放棄呼数'].sum())
        # 16_留守電数 (int): S_留守電
        self.voicemails = int(support_case.df_ivr_tvs.shape[0])
        # 15_留守電放棄件数 (int): reporter_タイムアウト数 - 16_留守電数
        self.abandoned_in_ivr = int(reporter.df_section['タイムアウト数'].sum()) - self.voicemails
        # 13_放棄呼数 (int): 14 + 15
        self.abandoned_calls = self.abandoned_during_operator + self.abandoned_in_ivr
        # 17_応答件数 (int): 11 - 12 - 13
        self.responses = self.total_calls - self.ivr_interruptions - self.abandoned_calls
        # 応答率
        self.response_rate = self.calc_rate(self.responses, self.total_calls)
        # 18_電話問い合わせ件数 (int): 16 + 17
        self.phone_inquiries = self.voicemails + self.responses
        # 21_直受け対応件数 (int): support_case_直受け
        self.direct_handling = support_case.df_direct_tvs.shape[0]
        # 直受率: 21 /18
        self.direct_handling_rate = self.calc_rate(self.direct_handling, self.phone_inquiries)
        # 23_お待たせ0分～20分対応件数 (int): 
        self.callback_count_0_to_20_min = int(activity.df_cb_0_20_tvs.shape[0])
        # 24_お待たせ20分以内累計対応件数 (int): 21 + 23
        self.cumulative_callback_under_20_min = self.direct_handling + self.callback_count_0_to_20_min
        # 25_お待たせ20分～30分対応件数 (int):
        self.callback_count_20_to_30_min = int(activity.df_cb_20_30_tvs.shape[0])
        # 26_お待たせ30分以内累計対応件数 (int): 24 + 25
        self.cumulative_callback_under_30_min = self.cumulative_callback_under_20_min + self.callback_count_20_to_30_min
        # 27_お待たせ30分～40分対応件数 (int):
        self.callback_count_30_to_40_min = int(activity.df_cb_30_40_tvs.shape[0])
        # 28_お待たせ40分以内累計対応件数 (int): 26 + 27
        self.cumulative_callback_under_40_min = self.cumulative_callback_under_30_min + self.callback_count_30_to_40_min
        # 29_お待たせ40分～60分対応件数 (int):
        self.callback_count_40_to_60_min = int(activity.df_cb_40_60_tvs.shape[0])
        # 30_お待たせ60分以内累計対応件数 (int): 28 + 29
        self.cumulative_callback_under_60_min = self.cumulative_callback_under_40_min + self.callback_count_40_to_60_min
        # 31_お待たせ60分以上対応件数 (int):
        self.callback_count_over_60_min = int(activity.df_cb_60over_tvs.shape[0])
        # お待たせ20分以上対応件数 (int):
        self.waiting_for_callback_over_20min = int(activity.df_wfc_over20_tvs.shape[0])
        # お待たせ30分以上対応件数 (int):
        self.waiting_for_callback_over_30min = int(activity.df_wfc_over30_tvs.shape[0])
        # お待たせ40分以上対応件数 (int):
        self.waiting_for_callback_over_40min = int(activity.df_wfc_over40_tvs.shape[0])
        # お待たせ60分以上対応件数 (int):
        self.waiting_for_callback_over_60min = int(activity.df_wfc_over60_tvs.shape[0])

        denominator = self.cumulative_callback_under_60_min + self.callback_count_over_60_min
        # 20分以内折返し率
        self.cumulative_callback_rate_under_20_min = self.calc_rate(self.cumulative_callback_under_20_min,
                                                                    denominator + self.waiting_for_callback_over_20min)
        # 30分以内折返し率
        self.cumulative_callback_rate_under_30_min = self.calc_rate(self.cumulative_callback_under_30_min,
                                                                    denominator + self.waiting_for_callback_over_30min)
        # 40分以内折返し率
        self.cumulative_callback_rate_under_40_min = self.calc_rate(self.cumulative_callback_under_40_min,
                                                                    denominator + self.waiting_for_callback_over_40min)
        # 60分以内折返し率
        self.cumulative_callback_rate_under_60_min = self.calc_rate(self.cumulative_callback_under_60_min,
                                                                    denominator + self.waiting_for_callback_over_60min)

        # wfc_20min_list
        self.wfc_20min_list = self.create_wfc_list(activity.df_wfc_over20_tvs)

        # wfc_30min_list
        self.wfc_30min_list = self.create_wfc_list(activity.df_wfc_over30_tvs)

        # wfc_40min_list
        self.wfc_40min_list = self.create_wfc_list(activity.df_wfc_over40_tvs)

        # wfc_60min_list
        self.wfc_60min_list = self.create_wfc_list(activity.df_wfc_over60_tvs)


    def add_kpi(self):
        context = {
                "total_calls": self.total_calls,
                "ivr_interruptions": self.ivr_interruptions,
                "abandoned_during_operator": self.abandoned_during_operator,
                "abandoned_in_ivr": self.abandoned_in_ivr,
                "abandoned_calls": self.abandoned_calls,
                "voicemails": self.voicemails,
                "responses": self.responses,
                "response_rate": self.response_rate,
                "phone_inquiries": self.phone_inquiries,
                "direct_handling": self.direct_handling,
                "direct_handling_rate": self.direct_handling_rate,
                "callback_count_0_to_20_min": self.callback_count_0_to_20_min,
                "cumulative_callback_under_20_min": self.cumulative_callback_under_20_min,
                "cumulative_callback_rate_under_20_min": self.cumulative_callback_rate_under_20_min,
                "callback_count_20_to_30_min": self.callback_count_20_to_30_min,
                "cumulative_callback_under_30_min": self.cumulative_callback_under_30_min,
                "cumulative_callback_rate_under_30_min": self.cumulative_callback_rate_under_30_min,
                "callback_count_30_to_40_min": self.callback_count_30_to_40_min,
                "cumulative_callback_under_40_min": self.cumulative_callback_under_40_min,
                "cumulative_callback_rate_under_40_min": self.cumulative_callback_rate_under_40_min,
                "callback_count_40_to_60_min": self.callback_count_40_to_60_min,
                "cumulative_callback_under_60_min": self.cumulative_callback_under_60_min,
                "cumulative_callback_rate_under_60_min": self.cumulative_callback_rate_under_60_min,
                "callback_count_over_60_min": self.callback_count_over_60_min,
                "waiting_for_callback_over_20min": self.waiting_for_callback_over_20min,
                "waiting_for_callback_over_30min": self.waiting_for_callback_over_30min,
                "waiting_for_callback_over_40min": self.waiting_for_callback_over_40min,
                "waiting_for_callback_over_60min": self.waiting_for_callback_over_60min,
                "wfc_20min_list": self.wfc_20min_list,
                "wfc_30min_list": self.wfc_30min_list,
                "wfc_40min_list": self.wfc_40min_list,
                "wfc_60min_list": self.wfc_60min_list
                }
        proxies = {'http': None, 'https': None}
        json_data = json.dumps(context)
        response = requests.post(
            settings.API_URL,
            data=json_data,
            headers={"Content-Type": "application/json"},
            proxies=proxies
        )
        print(response.status_code)
        print(response.text)
    
    def is_empty(self, dataframe: pd.DataFrame, row: int, col: int):
        if dataframe.empty:
            return 0
        else:
            return dataframe.iloc[row, col]
    
    def calc_rate(self, a, b, wfc=0):
        if (b + wfc) != 0:
            return a / (b + wfc)
        else:
            return 0.0
    
    def create_wfc_list(self, df) -> str:
        _ = list(df.loc[:, '案件番号 (関連) (サポート案件)'])
        l = map(lambda x: str(x), _)
        return ','.join(l)
    
    def export_summary(self):
        print('11_総着信数: ', self.total_calls)
        print('12_自動音声ガイダンス途中切断数: ', self.ivr_interruptions)
        print('14_オペレーター呼出途中放棄数: ', self.abandoned_during_operator)
        print('16_留守電数: ', self.voicemails)
        print('15_留守電放棄件数: ', self.abandoned_in_ivr)
        print('13_放棄呼数: ', self.abandoned_calls)
        print('17_応答件数: ', self.responses)
        print('応答率: ', self.response_rate)
        print('18_電話問い合わせ件数: ', self.phone_inquiries)
        print('21_直受け対応件数: ', self.direct_handling)
        print('直受率: ', self.direct_handling_rate)
        print('23_お待たせ0分～20分対応件数: ', self.callback_count_0_to_20_min)
        print('24_お待たせ20分以内累計対応件数: ', self.cumulative_callback_under_20_min)
        print('25_お待たせ20分～30分対応件数: ', self.callback_count_20_to_30_min)
        print('26_お待たせ30分以内累計対応件数: ', self.cumulative_callback_under_30_min)
        print('27_お待たせ30分～40分対応件数: ', self.callback_count_30_to_40_min)
        print('28_お待たせ40分以内累計対応件数: ', self.cumulative_callback_under_40_min)
        print('29_お待たせ40分～60分対応件数: ', self.callback_count_40_to_60_min)
        print('30_お待たせ60分以内累計対応件数: ', self.cumulative_callback_under_60_min)
        print('31_お待たせ60分以上対応件数: ', self.callback_count_over_60_min)
        print('20分以内折返し率: ', self.cumulative_callback_rate_under_20_min)
        print('30分以内折返し率: ', self.cumulative_callback_rate_under_30_min)
        print('40分以内折返し率: ', self.cumulative_callback_rate_under_40_min)
        print('60分以内折返し率: ', self.cumulative_callback_rate_under_60_min)
        print('折返し待ち20分以上: ', self.waiting_for_callback_over_20min)
        print('折返し待ち30分以上: ', self.waiting_for_callback_over_30min)
        print('折返し待ち40分以上: ', self.waiting_for_callback_over_40min)
        print('折返し待ち60分以上: ', self.waiting_for_callback_over_60min)
        print('折返し待ち20分以上案件: ', self.wfc_20min_list)
        print('折返し待ち30分以上案件: ', self.wfc_30min_list)
        print('折返し待ち40分以上案件: ', self.wfc_40min_list)
        print('折返し待ち60分以上案件: ', self.wfc_60min_list)

        