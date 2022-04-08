import telegram
import logging
import os
import json


logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logFormat = "%(asctime)s %(name)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=logFormat)


def webhook(event, context):
    logger.info(f"Event: {event}")
    if event["requestContext"]["http"]["method"] == "POST" and event["body"]:
        try:
            bot = set_bot()
            update = telegram.Update.de_json(json.loads(event["body"]), bot)
            chat_id = update.message.chat.id
            text = update.message.text
            if text and text.startswith("/hello"):
                try:
                    body = json.loads(event["body"])
                    message = body["message"]
                    msg = f"""Hello {message["from"]["first_name"]} {message["from"]["last_name"]}! I am bot."""
                    bot.sendMessage(
                        chat_id=chat_id,
                        text=msg,
                        reply_to_message_id=message["message_id"],
                        disable_web_page_preview=True,
                    )
                    logger.info("Text sent successfully")
                except Exception:
                    logger.exception("Error sending text")
            logger.info("Event handled")
            return create_response(200, "Event handled")
        except Exception:
            logger.exception("Error handling event")
            return create_response(400, "Error handling event")

    logger.info("No event to handle")
    return create_response(400, "No event to handle")


def set_webhook(event, context):
    logger.info(f"Event: {event}")
    url = f"""https://{event["headers"]["host"]}"""
    bot = set_bot()
    webhook = bot.set_webhook(url)
    if webhook:
        logger.info("Webhook set")
        return create_response(200, "Webhook set")

    logger.error("Error setting webhook")
    return create_response(400, "Error setting webhook")


def set_bot():
    telegram_token = os.environ["TELEGRAM_TOKEN"]
    return telegram.Bot(telegram_token)


def create_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(message),
    }
