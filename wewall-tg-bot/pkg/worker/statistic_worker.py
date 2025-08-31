import asyncio

from internal import interface, model

from datetime import time, date, datetime, timedelta

from aiogram import Bot


class StatisticWorker(interface.IStatisticWorker):
    def __init__(
            self,
            tel: interface.ITelemetry,
            user_service: interface.IUserService,
            statistic_tg_chat_ids: list[int],
            statistic_tg_chat_thread_ids: list[int],
            tg_bot_token: str
    ):
        self.logger = tel.logger()
        self.user_service = user_service

        self.bot = Bot(tg_bot_token)
        self.collection_time = time(7, 0)

        self.statistic_tg_chat_ids = statistic_tg_chat_ids
        self.statistic_tg_chat_thread_ids = statistic_tg_chat_thread_ids


    async def collect_daily_stats(self):
        while True:
            try:
                self.logger.debug("Цикл воркера статистики запущен")
                sleep_duration = self._calculate_daily_sleep_duration()
                print(f"sleep_duration = {sleep_duration}", flush=True)
                await asyncio.sleep(sleep_duration)

                await self._collect_and_process_daily_stats()
            except Exception as e:
                self.logger.error(f"Ошибка в воркере статистики: {e}")
                await asyncio.sleep(60)

    async def collect_monthly_stats(self):
        while True:
            try:
                self.logger.debug("Цикл воркера статистики запущен")
                sleep_duration = self._calculate_monthly_sleep_duration()
                print(f"sleep_duration = {sleep_duration}", flush=True)
                await asyncio.sleep(sleep_duration)

                await self._collect_and_process_monthly_stats()
            except Exception as e:
                self.logger.error(f"Ошибка в воркере статистики: {e}")
                await asyncio.sleep(60)

    def _calculate_monthly_sleep_duration(self) -> float:
        now = datetime.now()

        target_first_of_month = datetime.combine(date(now.year, now.month, 1), self.collection_time)

        if now >= target_first_of_month:
            if now.month == 12:
                target_next = datetime.combine(date(now.year + 1, 1, 1), self.collection_time)
            else:
                target_next = datetime.combine(date(now.year, now.month + 1, 1), self.collection_time)
        else:
            target_next = target_first_of_month

        return (target_next - now).total_seconds()

    def _calculate_daily_sleep_duration(self) -> float:
        now = datetime.now()
        print(f"now = {now}", flush=True)

        target_today = datetime.combine(now.date(), self.collection_time)

        if now >= target_today:
            target_next = target_today + timedelta(days=1)
        else:
            target_next = target_today

        return (target_next - now).total_seconds()

    async def _collect_and_process_daily_stats(self):
        try:
            print("Сбор дневной статистики", flush=True)

            target_day = date.today() - timedelta(days=1)
            users = await self.user_service.all_user()

            blocked_users = [
                user for user in users
                if user.is_bot_blocked
            ]

            users_today = [
                user for user in users
                if user.created_at.date() == target_day
            ]

            direct_link_users = [
                user for user in users_today
                if user.source_type == model.SourceType.DIRECT_LINK
            ]

            post_link_users = [
                user for user in users_today
                if user.source_type == model.SourceType.POST_LINK
            ]

            stat_text = f"""
<b>Статистика за {target_day.strftime("%d.%m.%Y")}</b>

Пользователи:
• Всего: <b>{len(users)}</b>
• Заблокировали бота: <b>{len(blocked_users)}</b>
• Новых: <b>{len(users_today)}</b>
  — прямая ссылка: <b>{len(direct_link_users)}</b>
  — пост: <b>{len(post_link_users)}</b>
"""
            for idx, statistic_tg_chat_id in enumerate(self.statistic_tg_chat_ids):
                try:
                    await self.bot.send_message(
                        statistic_tg_chat_id,
                        stat_text,
                        parse_mode="HTML",
                        message_thread_id=self.statistic_tg_chat_thread_ids[idx]
                    )
                    self.logger.info("Отправили статистику")

                except Exception as e:
                    self.logger.error(f"Ошибка отправки в чат {statistic_tg_chat_id}: {e}")

        except Exception as e:
            self.logger.error(f"Ошибка сбора статистики: {e}")


    async def _collect_and_process_monthly_stats(self):
        try:
            print("Сбор месячной статистики", flush=True)
            today = date.today()
            if today.month == 1:
                target_month_start = date(today.year - 1, 12, 1)
            else:
                target_month_start = date(today.year, today.month - 1, 1)

            # Последний день прошлого месяца
            target_month_end = date(today.year, today.month, 1) - timedelta(days=1)

            users = await self.user_service.all_user()

            blocked_users = [
                user for user in users
                if user.is_bot_blocked
            ]

            users_this_month = [
                user for user in users
                if target_month_start <= user.created_at.date() <= target_month_end
            ]

            direct_link_users = [
                user for user in users_this_month
                if user.source_type == model.SourceType.DIRECT_LINK
            ]

            post_link_users = [
                user for user in users_this_month
                if user.source_type == model.SourceType.POST_LINK
            ]

            months_ru = {
                1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
                5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
                9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
            }
            month_name_ru = f"{months_ru[target_month_start.month]} {target_month_start.year}"

            stat_text = f"""
<b>Статистика за {month_name_ru}</b>

Пользователи:
• Всего: <b>{len(users)}</b>
• Заблокировали бота: <b>{len(blocked_users)}</b>
• Новых за месяц: <b>{len(users_this_month)}</b>
  — прямая ссылка: <b>{len(direct_link_users)}</b>
  — пост: <b>{len(post_link_users)}</b>
"""

            for idx, statistic_tg_chat_id in enumerate(self.statistic_tg_chat_ids):
                try:
                    await self.bot.send_message(
                        statistic_tg_chat_id,
                        stat_text,
                        parse_mode="HTML",
                        message_thread_id=self.statistic_tg_chat_thread_ids[idx]
                    )
                    self.logger.info(f"Отправили месячную статистику за {month_name_ru}")

                except Exception as e:
                    self.logger.error(f"Ошибка отправки в чат {statistic_tg_chat_id}: {e}")

        except Exception as e:
            self.logger.error(f"Ошибка сбора месячной статистики: {e}")