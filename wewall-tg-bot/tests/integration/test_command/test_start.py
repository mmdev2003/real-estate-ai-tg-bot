

class TestCommandHandlers:
    async def test_start_command_creates_new_state(
            self,
            deps,
            mocks,
            async_client,
            telegram_request_body_factory
    ):
        webhook_data = telegram_request_body_factory["message"]("/start")
        state_service = deps["state_service"]

        mocks['estate_expert_client'].send_message_to_wewall_expert.return_value = "Добро пожаловать!"

        response = await async_client.post(
            "/update",
            json=webhook_data,
            headers={"X-Telegram-Bot-Api-Secret-Token": "secret"}
        )

        state = await state_service.state_by_id(1)
        print(f"{state[0]=}", flush=True)

        assert response.status_code == 200