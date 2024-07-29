import datetime
import logging
from sqlalchemy import and_, Column, Float, Integer, String

from common.models.db import BaseDatabase, database


class BaseKpiInfo(BaseDatabase):
    __abstract__ = True

    # データフィールド
    total_calls = Column('total_calls', Integer)  # 11_総着信数
    ivr_interruptions = Column('ivr_interruptions', Integer)  # 12_自動音声ガイダンス途中切断数
    abandoned_during_operator = Column('abandoned_during_operator', Integer)  # 14_オペレーター呼出途中放棄数
    abandoned_in_ivr = Column('abandoned_in_ivr', Integer)  # 15_留守電放棄件数
    abandoned_calls = Column('abandoned_calls', Integer)  # 13_放棄呼数
    voicemails = Column('voicemails', Integer)  # 16_留守電数
    responses = Column('responses', Integer)  # 17_応答件数
    response_rate = Column('response_rate', Float)  # 応答率
    phone_inquiries = Column('phone_inquiries', Integer)  # 18_電話問い合わせ件数
    direct_handling = Column('direct_handling', Integer)  # 21_直受け対応件数
    direct_handling_rate = Column('direct_handling_rate', Float)  # 直受け対応率
    # callbacks = Column('callbacks', Integer)  # 22_折返し対応件数
    callback_count_0_to_20_min = Column('callback_count_0_to_20_min', Integer)  # 23_お待たせ0分～20分対応件数
    cumulative_callback_under_20_min = Column('cumulative_callback_under_20_min', Integer)  # 24_お待たせ20分以内累計対応件数
    cumulative_callback_rate_under_20_min = Column('cumulative_callback_rate_under_20_min', Float)  # お待たせ20分以内累計対応率
    callback_count_20_to_30_min = Column('callback_count_20_to_30_min', Integer)  # 25_お待たせ20分～30分対応件数
    cumulative_callback_under_30_min = Column('cumulative_callback_under_30_min', Integer)  # 26_お待たせ30分以内累計対応件数
    cumulative_callback_rate_under_30_min = Column('cumulative_callback_rate_under_30_min', Float)  # お待たせ30分以内累計対応率
    callback_count_30_to_40_min = Column('callback_count_30_to_40_min', Integer)  # 27_お待たせ30分～40分対応件数
    cumulative_callback_under_40_min = Column('cumulative_callback_under_40_min', Integer)  # 28_お待たせ40分以内累計対応件数
    cumulative_callback_rate_under_40_min = Column('cumulative_callback_rate_under_40_min', Float)  # お待たせ40分以内累計対応率
    callback_count_40_to_60_min = Column('callback_count_40_to_60_min', Integer)  # 29_お待たせ40分～60分対応件数
    cumulative_callback_under_60_min = Column('cumulative_callback_under_60_min', Integer)  # 30_お待たせ60分以内累計対応件数
    cumulative_callback_rate_under_60_min = Column('cumulative_callback_rate_under_60_min', Float)  # お待たせ60分以内累計対応率
    callback_count_over_60_min = Column('callback_count_over_60_min', Integer)  # 31_お待たせ60分以上対応件数
    waiting_for_callback_over_20min = Column('waiting_for_callback_over_20min', Integer)  # 32_お待たせ20分以上対応件数
    waiting_for_callback_over_30min = Column('waiting_for_callback_over_30min', Integer)  # 33_お待たせ30分以上対応件数
    waiting_for_callback_over_40min = Column('waiting_for_callback_over_40min', Integer)  # 34_お待たせ40分以上対応件数
    waiting_for_callback_over_60min = Column('waiting_for_callback_over_60min', Integer)  # 34_お待たせ60分以上対応件数
    wfc_20min_list = Column('wfc_20min_list', String)  # お待たせ20分以上対応案件番号
    wfc_30min_list = Column('wfc_30min_list', String)  # お待たせ30分以上対応案件番号
    wfc_40min_list = Column('wfc_40min_list', String)  # お待たせ40分以上対応案件番号
    wfc_60min_list = Column('wfc_60min_list', String)  # お待たせ60分以上対応案件番号

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class KpiInfoSs(BaseKpiInfo):
    __tablename__ = 'kpi_info_ss'

    @staticmethod
    def add_record(data: dict):
        session = database.connect_db()

        record = KpiInfoSs()

        for key, value in data.items():
            setattr(record, key, value)

        session.add(record)
        session.commit()
        session.close()
    
    @staticmethod
    def get_latest_record():
        session = database.connect_db()
        record = session.query(KpiInfoSs).order_by(KpiInfoSs.id.desc()).first()
        session.close()
        return record


class KpiInfoTvs(BaseKpiInfo):
    __tablename__ = 'kpi_info_tvs'

    @staticmethod
    def add_record(data: dict):
        session = database.connect_db()

        record = KpiInfoTvs()

        for key, value in data.items():
            setattr(record, key, value)

        session.add(record)
        session.commit()
        session.close()
    
    @staticmethod
    def get_latest_record():
        session = database.connect_db()
        record = session.query(KpiInfoTvs).order_by(KpiInfoTvs.id.desc()).first()
        session.close()
        return record

    @staticmethod
    def get_records_at_date(datetime_obj: datetime.datetime):
        next_day = datetime_obj + datetime.timedelta(days=1)
        session = database.connect_db()
        records = session.query(KpiInfoTvs).filter(
            and_(
                KpiInfoTvs.created_at >= datetime_obj,
                KpiInfoTvs.created_at < next_day
                )
            ).all()
        session.close()
        return records
    
    @staticmethod
    def get_record_at_date_latest(datetime_obj: datetime.datetime):
        next_day = datetime_obj + datetime.timedelta(days=1)
        session = database.connect_db()
        record = session.query(KpiInfoTvs).filter(
            and_(
                KpiInfoTvs.created_at >= datetime_obj,
                KpiInfoTvs.created_at < next_day
                )
            ).order_by(KpiInfoTvs.id.desc()).first()
        session.close()
        return record
    
    @staticmethod
    def get_records_from_within_datetime_range(start_datetime: datetime.datetime, end_datetime: datetime.datetime):
        session = database.connect_db()
        records = session.query(KpiInfoTvs).filter(
            and_(
                KpiInfoTvs.created_at >= start_datetime,
                KpiInfoTvs.created_at < end_datetime,
                )
            ).all()
        session.close()
        return records


class KpiInfoKmn(BaseKpiInfo):
    __tablename__ = 'kpi_info_kmn'

    @staticmethod
    def add_record(data: dict):
        session = database.connect_db()

        record = KpiInfoKmn()

        for key, value in data.items():
            setattr(record, key, value)

        session.add(record)
        session.commit()
        session.close()
    
    @staticmethod
    def get_latest_record():
        session = database.connect_db()
        record = session.query(KpiInfoKmn).order_by(KpiInfoKmn.id.desc()).first()
        session.close()
        return record


class KpiInfoHhd(BaseKpiInfo):
    __tablename__ = 'kpi_info_hhd'
    
    @staticmethod
    def add_record(data: dict):
        session = database.connect_db()

        record = KpiInfoHhd()

        for key, value in data.items():
            setattr(record, key, value)

        session.add(record)
        session.commit()
        session.close()
    
    @staticmethod
    def get_latest_record():
        session = database.connect_db()
        record = session.query(KpiInfoHhd).order_by(KpiInfoHhd.id.desc()).first()
        session.close()
        return record
