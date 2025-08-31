import io

import pdfkit
import os
from string import Template
from PyPDF2 import PdfMerger

from aiogram.types import BufferedInputFile

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface, common

from pkg.client.client import AsyncHTTPClient


class WewallEstateCalculatorClient(interface.IWewallEstateCalculatorClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int
    ):
        self.logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/estate-calculator",
            use_tracing=True,
            logger=self.logger,
        )
        self.tracer = tel.tracer()

    async def calc_finance_model_finished_office(
            self,
            square: float,
            price_per_meter: float,
            need_repairs: int,
            estate_category: str,
            metro_station_name: str,
            distance_to_metro: float,
            nds_rate: int,
    ) -> model.FinanceModelResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_finished_office",
                kind=SpanKind.CLIENT,
                attributes={
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "need_repairs": need_repairs,
                    "estate_category": estate_category,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "nds_rate": nds_rate,
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "need_repairs": need_repairs,
                    "metro_station_name": metro_station_name,
                    "estate_category": estate_category,
                    "distance_to_metro": distance_to_metro,
                    "nds_rate": nds_rate,
                }
                response = await self.client.post("/finished/office", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    if json_response.get("error_code") is not None:
                        match json_response["error_code"]:
                            case 4041:
                                err = common.MetroStationNotFound(json_response.get("error"))
                                span.record_exception(err)
                                span.set_status(Status(StatusCode.ERROR, str(err)))
                                raise err

                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return model.FinanceModelResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_finished_office_table(
            self,
            square: float,
            price_per_meter: float,
            need_repairs: int,
            estate_category: str,
            metro_station_name: str,
            distance_to_metro: float,
            nds_rate: int,
    ) -> BufferedInputFile:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_finished_office_table",
                kind=SpanKind.CLIENT,
                attributes={
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "need_repairs": need_repairs,
                    "estate_category": estate_category,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "nds_rate": nds_rate,
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "need_repairs": need_repairs,
                    "metro_station_name": metro_station_name,
                    "estate_category": estate_category,
                    "distance_to_metro": distance_to_metro,
                    "nds_rate": nds_rate,
                }
                response = await self.client.post("/finished/office/table", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    json_response = response.json()
                    if json_response.get("error_code") is not None:
                        match json_response["error_code"]:
                            case 4041:
                                err = common.MetroStationNotFound(json_response.get("error"))
                                span.record_exception(err)
                                span.set_status(Status(StatusCode.ERROR, str(err)))
                                raise err
                    raise Exception(f"Client error: {response.status_code}")

                calc_xlsx = response.content
                if isinstance(calc_xlsx, bytes):
                    input_file = BufferedInputFile(calc_xlsx, filename="Финансовая модель офиса.xlsx")

                    span.set_status(Status(StatusCode.OK))
                    return input_file
                else:
                    err = Exception("Ошибка: ожидались байтовые данные, но получили что-то другое.")
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    raise err

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_finished_retail(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
    ) -> model.FinanceModelResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_finished_retail",
                kind=SpanKind.CLIENT,
                attributes={
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                }
                response = await self.client.post("/finished/retail", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return model.FinanceModelResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_finished_retail_table(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
    ) -> BufferedInputFile:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_finished_retail_table",
                kind=SpanKind.CLIENT,
                attributes={
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                }
                response = await self.client.post("/finished/retail/table", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                calc_xlsx = response.content
                if isinstance(calc_xlsx, bytes):
                    input_file = BufferedInputFile(calc_xlsx, filename="Финансовая модель ритейла.xlsx")

                    span.set_status(Status(StatusCode.OK))
                    return input_file
                else:
                    err = Exception("Ошибка: ожидались байтовые данные, но получили что-то другое.")
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    raise err
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_building_office(
            self,
            project_readiness: str,
            square: float,
            metro_station_name: str,
            distance_to_metro: float,
            estate_category: str,
            price_per_meter: float,
            nds_rate: int,
            transaction_dict: dict,
    ) -> model.FinanceModelResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_building_office",
                kind=SpanKind.CLIENT,
                attributes={
                    "project_readiness": project_readiness,
                    "square": square,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "estate_category": estate_category,
                    "price_per_meter": price_per_meter,
                    "nds_rate": nds_rate,
                    "transaction_dict": transaction_dict
                }
        ) as span:
            try:
                body = {
                    "project_readiness": project_readiness,
                    "square": square,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "estate_category": estate_category,
                    "price_per_meter": price_per_meter,
                    "nds_rate": nds_rate,
                    "transaction_dict": transaction_dict,
                }
                response = await self.client.post("/building/office", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if json_response.get("error") is not None:
                    match json_response["error_code"]:
                        case 4001:
                            err = common.TransactionDictSumNotEqual100(json_response["error"])
                            span.record_exception(err)
                            span.set_status(Status(StatusCode.ERROR, str(err)))
                            raise err

                        case 4041:
                            err = common.MetroStationNotFound(json_response.get("error"))
                            span.record_exception(err)
                            span.set_status(Status(StatusCode.ERROR, str(err)))
                            raise err

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return model.FinanceModelResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_building_office_table(
            self,
            project_readiness: str,
            square: float,
            metro_station_name: str,
            distance_to_metro: float,
            estate_category: str,
            price_per_meter: float,
            nds_rate: int,
            transaction_dict: dict,
    ) -> BufferedInputFile:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_building_office_table",
                kind=SpanKind.CLIENT,
                attributes={
                    "project_readiness": project_readiness,
                    "square": square,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "estate_category": estate_category,
                    "price_per_meter": price_per_meter,
                    "nds_rate": nds_rate,
                    "transaction_dict": transaction_dict
                }
        ) as span:
            try:
                body = {
                    "project_readiness": project_readiness,
                    "square": square,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "estate_category": estate_category,
                    "price_per_meter": price_per_meter,
                    "nds_rate": nds_rate,
                    "transaction_dict": transaction_dict,
                }
                response = await self.client.post("/building/office/table", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    json_response = response.json()
                    if json_response.get("error_code") is not None:
                        match json_response["error_code"]:
                            case 4041:
                                err = common.MetroStationNotFound(json_response.get("error"))
                                span.record_exception(err)
                                span.set_status(Status(StatusCode.ERROR, str(err)))
                                raise err
                    raise Exception(f"Client error: {response.status_code}")

                calc_xlsx = response.content

                if isinstance(calc_xlsx, bytes):
                    input_file = BufferedInputFile(calc_xlsx, filename="Финансовая модель офиса.xlsx")

                    span.set_status(Status(StatusCode.OK))
                    return input_file
                else:
                    err = Exception("Ошибка: ожидались байтовые данные, но получили что-то другое.")
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    raise err

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_building_retail(
            self,
            project_readiness: str,
            square: float,
            price_rva: float,
            m_a_p: float,
            price_per_meter: float,
            nds_rate: int,
            need_repairs: int,
            transaction_dict: dict,
    ) -> model.FinanceModelResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_building_retail",
                kind=SpanKind.CLIENT,
                attributes={
                    "project_readiness": project_readiness,
                    "square": square,
                    "price_rva": price_rva,
                    "m_a_p": m_a_p,
                    "price_per_meter": price_per_meter,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                    "transaction_dict": transaction_dict
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "transaction_dict": transaction_dict,
                    "price_rva": price_rva,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "project_readiness": project_readiness,
                    "need_repairs": need_repairs,
                }
                response = await self.client.post("/building/retail", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if json_response.get("error") is not None:
                    match json_response["error_code"]:
                        case 4001:
                            err = common.TransactionDictSumNotEqual100(json_response["error"])
                            span.record_exception(err)
                            span.set_status(Status(StatusCode.ERROR, str(err)))
                            raise err

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return model.FinanceModelResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_building_retail_table(
            self,
            project_readiness: str,
            square: float,
            price_rva: float,
            m_a_p: float,
            price_per_meter: float,
            nds_rate: int,
            need_repairs: int,
            transaction_dict: dict,
    ) -> BufferedInputFile:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_building_retail_table",
                kind=SpanKind.CLIENT,
                attributes={
                    "project_readiness": project_readiness,
                    "square": square,
                    "price_rva": price_rva,
                    "m_a_p": m_a_p,
                    "price_per_meter": price_per_meter,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                    "transaction_dict": transaction_dict
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "transaction_dict": transaction_dict,
                    "price_rva": price_rva,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "project_readiness": project_readiness,
                    "need_repairs": need_repairs,
                }

                response = await self.client.post("/building/retail/table", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                calc_xlsx = response.content

                if isinstance(calc_xlsx, bytes):
                    input_file = BufferedInputFile(calc_xlsx, filename="Финансовая модель ритейла.xlsx")

                    span.set_status(Status(StatusCode.OK))
                    return input_file
                else:
                    err = Exception("Ошибка: ожидались байтовые данные, но получили что-то другое.")
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    raise err

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def generate_pdf(
            self,
            estate_type: str,
            buying_property: float,
            sale_property: float,
            sale_tax: float,
            rent_tax: float,
            price_of_finishing: float,
            rent_flow: float,
            terminal_value: float,
            sale_income: float,
            rent_income: float,
            added_value: float,
            rent_irr: float,
            sale_irr: float,
    ) -> BufferedInputFile:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.generate_pdf",
                kind=SpanKind.CLIENT,
                attributes={
                    "estate_type": estate_type,
                    "buying_property": buying_property,
                    "sale_property": sale_property,
                    "sale_tax": sale_tax,
                    "rent_tax": rent_tax,
                    "price_of_finishing": price_of_finishing,
                    "rent_flow": rent_flow,
                    "terminal_value": terminal_value,
                    "sale_income": sale_income,
                    "rent_income": rent_income,
                    "added_value": added_value,
                    "rent_irr": rent_irr,
                    "sale_irr": sale_irr
                }
        ) as span:
            try:
                BASE_DIR = os.path.abspath(
                    "pkg/client/internal/wewall_estate_calculator/image_generator/html")

                IMG_DIR = os.path.abspath(
                    "pkg/client/internal/wewall_estate_calculator/image_generator/img/")

                sale_analyse_text = await self.__analyse_text_by_irr(sale_irr, estate_type)
                rent_analyse_text = await self.__analyse_text_by_irr(rent_irr, estate_type)

                with open(os.path.join(BASE_DIR, "wewall_rent_template.html"), "r", encoding="utf-8") as file:
                    wewall_rent_template = Template(file.read())
                with open(os.path.join(BASE_DIR, "wewall_purchase_template.html"), "r", encoding="utf-8") as file:
                    wewall_purchase_template = Template(file.read())
                with open(os.path.join(BASE_DIR, "wewall_landing.html"), "r", encoding="utf-8") as file:
                    wewall_landing_html = Template(file.read())

                wewall_landing_html = wewall_landing_html.substitute()
                wewall_purchase_html = wewall_purchase_template.substitute({
                    "sale_analyse_text": sale_analyse_text,
                    "irr": sale_irr,
                    "income": sale_income,
                    "purchase": buying_property,
                    "estate_tax": sale_tax,
                    "finish_price": sale_property,
                    "extra_price": added_value,
                })
                wewall_rent_html = wewall_rent_template.substitute({
                    "rent_analyse_text": rent_analyse_text,
                    "irr": rent_irr,
                    "income": rent_income,
                    "purchase": buying_property,
                    "estate_tax": rent_tax,
                    "design_price": price_of_finishing,
                    "rent_income": rent_flow,
                    "finishing_price": terminal_value,
                    "invest_cycle": "6 ЛЕТ",
                    "invest_cycle_text": "С ДАТЫ ПОКУПКИ" if "finished" in estate_type else "С ДАТЫ ВВОДА",
                })

                wewall_landing_html = wewall_landing_html.replace('src="../img/', f'src="file://{IMG_DIR}/')
                wewall_rent_html = wewall_rent_html.replace('src="../img/', f'src="file://{IMG_DIR}/')
                wewall_purchase_html = wewall_purchase_html.replace('src="../img/', f'src="file://{IMG_DIR}/')

                options = {
                    'margin-top': '0',
                    'margin-left': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'page-height': '12cm',
                    'page-width': '8cm',
                    'dpi': 300,
                    '--enable-local-file-access': '',
                    '--print-media-type': '',
                }
                if estate_type in (common.FinishStateCommand.estate_calculator_finished_retail,
                                   common.FinishStateCommand.estate_calculator_finished_office):
                    pdf_bytes_1 = pdfkit.from_string(wewall_landing_html, False, options=options)
                    pdf_bytes_2 = pdfkit.from_string(wewall_rent_html, False, options=options)

                    final_pdf_stream = io.BytesIO()

                    merger = PdfMerger()
                    merger.append(io.BytesIO(pdf_bytes_1))
                    merger.append(io.BytesIO(pdf_bytes_2))
                    merger.write(final_pdf_stream)
                    merger.close()

                else:
                    pdf_bytes_1 = pdfkit.from_string(wewall_landing_html, False, options=options)  # Первая страница
                    pdf_bytes_2 = pdfkit.from_string(wewall_rent_html, False, options=options)  # Вторая страница
                    pdf_bytes_3 = pdfkit.from_string(wewall_purchase_html, False, options=options)  # Третья страница

                    final_pdf_stream = io.BytesIO()

                    merger = PdfMerger()
                    merger.append(io.BytesIO(pdf_bytes_1))
                    merger.append(io.BytesIO(pdf_bytes_2))
                    merger.append(io.BytesIO(pdf_bytes_3))
                    merger.write(final_pdf_stream)
                    merger.close()

                wewall_landing_html = wewall_landing_html.replace(f'src="file://{IMG_DIR}/', f'src="../img/')
                wewall_rent_html = wewall_rent_html.replace(f'src="file://{IMG_DIR}/', f'src="../img/')
                wewall_purchase_html = wewall_purchase_html.replace(f'src="file://{IMG_DIR}/', f'src="../img/')

                final_pdf_stream.seek(0)

                pdf_file = BufferedInputFile(final_pdf_stream.read(), filename="Отчет оценки доходности.pdf")

                span.set_status(Status(StatusCode.OK))
                return pdf_file
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    @staticmethod
    async def __analyse_text_by_irr(irr: float, estate_type: str) -> str:

        if "building" in estate_type:
            if irr <= 6:
                analyse_text = """ОЧЕНЬ НИЗКАЯ НОРМА ДОХОДНОСТИ по данной стратегии для проектов на стадии строительства. 
Покупка этого объекта – это даже не сохранение своих денег. 
Если для вас экономика объекта имеет значение, то рекомендую рассмотреть альтернативные проекты.
Рекомендую обратиться за консультацией и подбором объектов к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""
            elif irr <= 9:
                analyse_text = """НОРМА ДОХОДНОСТИ НИЖЕ СРЕДНЕРЫНОЧНОЙ по данной стратегии для проектов на стадии строительства. 
Не составит труда найти альтернативные варианты с более высокими финансовыми показателями.  
Если для вас экономика объекта имеет значение, то рекомендую продолжать поиск. 
Рекомендую обратиться за консультацией и подбором объектов к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""

            elif irr <= 13:
                analyse_text = """СРЕДНЯЯ НОРМА ДОХОДНОСТИ по данной стратегии для объекта на стадии строительства. 
Рекомендую сделать сравнительный анализ с другими объектами-аналогами для принятия взвешенного решения. 
С этой задачей обратитесь к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий. 
"""

            else:
                analyse_text = """ВЫСОКАЯ НОРМА ДОХОДНОСТИ по данной стратегии для объекта на стадии строительства. 
Чтобы подтвердить оценку финансовых показателей по основным вводным для расчета, рекомендую обратиться за консультацией к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""

            return analyse_text

        #
        elif "finished" in estate_type:
            if irr <= 6:
                analyse_text = """ОЧЕНЬ НИЗКАЯ НОРМА ДОХОДНОСТИ по данной стратегии для этого объекта.
Покупка этого объекта – это даже не сохранение своих денег. 
Если для вас экономика объекта имеет значение, то рекомендую рассмотреть альтернативные проекты.
Рекомендую обратиться за консультацией и подбором объектов к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""
            elif irr <= 8:
                analyse_text = """НОРМА ДОХОДНОСТИ НИЖЕ СРЕДНЕРЫНОЧНОЙ по данной стратегии для этого объекта.
Не составит труда найти альтернативные варианты с более высокими финансовыми показателями.  
Если для вас экономика объекта имеет значение, то рекомендую продолжать поиск. 
Рекомендую обратиться за консультацией и подбором объектов к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""

            elif irr <= 10:
                analyse_text = """СРЕДНЯЯ НОРМА ДОХОДНОСТИ по данной стратегии для этого объекта. 
Рекомендую сделать сравнительный анализ с другими объектами-аналогами для принятия взвешенного решения. 
С этой задачей обратитесь к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""

            else:
                analyse_text = """ВЫСОКАЯ НОРМА ДОХОДНОСТИ по данной стратегии для этого объекта. 
Чтобы подтвердить оценку финансовых показателей по основным вводным для расчета, рекомендую обратиться за консультацией к лучшей на рынке недвижимости консалтинговой компании WEWALL. Работают без комиссий.
"""

            return analyse_text
        return ""
