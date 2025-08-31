from dataclasses import dataclass

PREFIX = "/api/tg-bot"

TRACE_ID_KEY = "trace_id"
SPAN_ID_KEY = "span_id"
REQUEST_ID_KEY = "request_id"
EXTRA_LOG_FIELDS_KEY = "extra"
FILE_KEY = "file"
ERROR_KEY = "error"

HTTP_METHOD_KEY = "http.request.method"
HTTP_STATUS_KEY = "http.response.status_code"
HTTP_ROUTE_KEY = "http.route"
HTTP_REQUEST_DURATION_KEY = "http.server.request.duration"

CRM_SYSTEM_NAME_KEY = "crm.system.name"

TELEGRAM_EVENT_TYPE_KEY = "telegram.event.type"
TELEGRAM_CHAT_ID_KEY = "telegram.chat.id"
TELEGRAM_USER_USERNAME_KEY = "telegram.user.username"
TELEGRAM_USER_MESSAGE_KEY = "telegram.user.message"
TELEGRAM_MESSAGE_ID_KEY = "telegram.message.id"
TELEGRAM_CALLBACK_QUERY_DATA_KEY = "telegram.callback_query.data"
TELEGRAM_MESSAGE_DURATION_KEY = "telegram.message.duration"
TELEGRAM_MESSAGE_DIRECTION_KEY = "telegram.message.direction"
TELEGRAM_CHAT_TYPE_KEY = "telegram.chat.type"

REQUEST_DURATION_METRIC = "http.server.request.duration"
ACTIVE_REQUESTS_METRIC = "http.server.active_requests"
REQUEST_BODY_SIZE_METRIC = "http.server.request.body.size"
RESPONSE_BODY_SIZE_METRIC = "http.server.response.body.size"
OK_REQUEST_TOTAL_METRIC = "http.server.ok.request.total"
ERROR_REQUEST_TOTAL_METRIC = "http.server.error.request.total"

OK_MESSAGE_TOTAL_METRIC = "telegram.server.ok.message.total"
ERROR_MESSAGE_TOTAL_METRIC = "telegram.server.error.message.total"
OK_JOIN_CHAT_TOTAL_METRIC = "telegram.server.ok.join_chat.total"
ERROR_JOIN_CHAT_TOTAL_METRIC = "telegram.server.error.join_chat.total"
MESSAGE_DURATION_METRIC = "telegram.server.message.duration"
ACTIVE_MESSAGES_METRIC = "telegram.server.active_messages"

TRACE_ID_HEADER = "X-Trace-ID"
SPAN_ID_HEADER = "X-Span-ID"


@dataclass
class StateSwitchCommand:
    to_estate_search_expert = "switch_to_estate_search_expert"
    to_estate_finance_model_expert = "switch_to_estate_finance_model_expert"
    to_estate_expert = "switch_to_estate_expert"
    to_wewall_expert = "switch_to_wewall_expert"
    to_manager = "switch_to_manager"
    to_contact_collector = "switch_to_contact_collector"


@dataclass
class FinishStateCommand:
    estate_calculator_finished_office = "finished_office"
    estate_calculator_finished_retail = "finished_retail"
    estate_calculator_building_office = "building_office"
    estate_calculator_building_retail = "building_retail"

    start_estate_search = "start_estate_search"
    next_offer_estate_search = "next_offer"

    estate_search_sale = "estate_search_sale"
    estate_search_rent = "estate_search_rent"


@dataclass
class StateStatuses:
    wewall_expert = "wewall_expert"
    estate_expert = "estate_expert"
    estate_search = "estate_search"
    estate_analysis = "estate_analysis"
    estate_finance_model = "estate_finance_model"
    contact_collector = "contact_collector"

    chat_with_amocrm_manager = "chat_with_amocrm_manager"


@dataclass
class EstateSearchKeyboardCallbackData:
    PREFIX = "estate_search:"
    like_offer = "estate_search:like_offer"
    next_offer = "estate_search:next_offer"
    next_estate = "estate_search:next_estate"


@dataclass
class WewallExpertKeyboardCallbackData:
    PREFIX = "wewall_expert:"
    to_estate_search = "wewall_expert:to_estate_search"
    to_estate_finance_model = "wewall_expert:to_estate_finance_model"
    to_estate_expert = "wewall_expert:to_estate_expert"
    to_manager = "wewall_expert:to_manager"
    check_subscribe = "wewall_expert:check_subscribe"
    start = "wewall_expert:start"


@dataclass
class AmocrmPipelineStatus:
    chat_with_bot = 68250762
    high_engagement = 77378374
    active_user = 77664126
    chat_with_manager = 65965614


no_offers_text = "Нет подходящих предложений под ваши параметры поиска."
no_more_offers = "Больше помещений под ваши параметры поиска нет"
compromise_no_offers_text = """
Клиент не смог найти предложений по свом параметрам поиска.
Напиши что-то вроде:
Даже небольшая корректировка может открыть подходящие варианты. Что вы готовы изменить в текущем поиске? Например:

-Расширить локацию
-Скорректировать бюджет
-Изменить площадь объекта

Или предложите свой вариант в свободной форме и я начну новый поиск!
"""
no_more_estates = """
Больше зданий под ваши параметры поиска нет
"""
manger_is_connecting_text = "Менеджер скоро подключится, бот будет работать дальше, пока не подключится менеджер"
not_subscribe_text = 'WEWALL AI доступен только для подписчиков основного telegram-канала консалтинговой компании WEWALL'
