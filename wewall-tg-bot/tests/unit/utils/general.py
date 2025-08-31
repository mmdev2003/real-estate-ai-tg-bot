from datetime import datetime

from unittest.mock import AsyncMock, MagicMock, call
from aiogram.types import Update, Message, CallbackQuery, User, Chat

from opentelemetry.trace import SpanKind, StatusCode

from internal import model

def create_message(text="Test message", user_id=123, chat_id=456, username="testuser"):
    message = AsyncMock(spec=Message)
    message.text = text
    message.message_id = 789
    message.answer = AsyncMock()
    message.answer_document = AsyncMock()
    message.answer_media_group = AsyncMock()

    # User
    user = AsyncMock(spec=User)
    user.id = user_id
    user.username = username
    user.first_name = "Test"
    user.last_name = "User"
    message.from_user = user

    # Chat
    chat = AsyncMock(spec=Chat)
    chat.id = chat_id
    message.chat = chat

    return message


def create_callback_query(data, message, user_id=123, username="testuser"):
    callback = MagicMock(spec=CallbackQuery)
    callback.data = data
    callback.message = create_message(message)
    callback.answer = AsyncMock()

    # User
    user = MagicMock(spec=User)
    user.id = user_id
    user.username = username
    user.first_name = "Test"
    user.last_name = "User"
    callback.from_user = user

    return callback


def create_update(message=None, callback_query=None):
    update = MagicMock(spec=Update)
    update.message = message
    update.callback_query = callback_query
    return update


def create_state(status: str, count_estate_calculator=0, count_estate_search=0):
    state = model.State(
        id=1,
        tg_chat_id=52,
        status=status,
        count_estate_search=count_estate_search,
        count_estate_calculator=count_estate_calculator,
        count_message=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return state

def assert_span(
        tracer,
        spans: list[dict]
):
    expected_calls = []
    for span in spans:
        kind = span.get("kind")
        if kind is None:
            kind = SpanKind.INTERNAL
        attributes = span.get("attributes")
        if attributes is None:
            expected_calls.append(call(span["name"], kind=kind))
        else:
            expected_calls.append(call(span["name"], kind=kind, attributes=attributes))

    actual_calls = tracer.start_as_current_span.call_args_list
    assert actual_calls == expected_calls

    span_mock = tracer.start_as_current_span.return_value.__enter__.return_value
    assert span_mock.set_status.call_count == len(spans)
    span_mock.set_status.assert_has_calls([
        call(StatusCode.OK)
        for _ in range(len(spans))
    ])


def assert_span_error(tracer, err: Exception, call_count: int):
    span_mock = tracer.start_as_current_span.return_value.__enter__.return_value
    assert span_mock.record_exception.call_count == call_count
    span_mock.record_exception.assert_has_calls([
        call(err)
        for _ in range(call_count)
    ])
    assert span_mock.set_status.call_count == call_count
    span_mock.set_status.assert_has_calls([
        call(StatusCode.ERROR, str(err))
        for _ in range(call_count)
    ])