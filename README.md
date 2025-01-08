# Spam Protection Bot 🐕

This bot helps to protect Telegram groups from spam by automatically deleting and banning users who send spam messages. It can also log spam messages to the admin and has additional features like command-based testing.
Created and generated with ChatGPT.

---

## Commands

### `/start`
- **English**: Activates the bot and sends a welcome message.
- **Russian**: Активирует бота и отправляет приветственное сообщение.

### `/toggle_logs`
- **English**: Toggles the spam log functionality on and off (only available to admins).
- **Russian**: Включает/выключает логирование спама (доступно только администраторам).

### `/getid`
- **English**: Returns the chat ID and sender's ID of the message.
- **Russian**: Возвращает ID чата и ID отправителя сообщения.

### `/test_delete_and_ban`
- **English**: Tests spam deletion and bans the user (does not block the user in test mode).
- **Russian**: Тестирует удаление сообщения и бан пользователя (не блокирует пользователя в тестовом режиме).

---

## How to Use

### 1. Deploy the Bot
To deploy the bot, you need to have Python and Docker installed. Follow these steps:

1. Clone the repository and navigate to the directory:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your `.env` file with the required environment variables:
    ```ini
    BOT_TOKEN=<your_bot_token>
    ALLOWED_CHATS=<comma_separated_list_of_allowed_chats>
    ADMINS=<comma_separated_list_of_admins>
    ```

4. Run the bot locally:
    ```bash
    python main.py
    ```

### 2. Using via Docker

1. Set up your `.env` file with the required environment variables:
    ```ini
    BOT_TOKEN=<your_bot_token>
    ALLOWED_CHATS=<comma_separated_list_of_allowed_chats>
    ADMINS=<comma_separated_list_of_admins>
    ```
2. Run the bot in a Docker container:
    ```bash
    docker run -d --env-file .env jnqa/puhdaskoira:v1
    ```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
