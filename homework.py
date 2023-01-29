from dotenv import load_dotenv
import os 
from telegram.ext import StreamHandler
import logging 

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    ...


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено')
    except Exception as error:
        logging.error(f'Сообщение не было отправлено {error}')


def get_api_answer(timestamp):
    ...


def check_response(response):
    if not isinstance(response, dict):
        logger.error(f"homeworks не словарь")
        raise TypeError(f"homeworks не словарь")
    if "homeworks" not in response:
        logger.error("В ответе API нет ключа homeworks")   
        raise KeyError("В ответе API нет ключа homeworks")
    if not isinstance(response["homeworks"], list):
        logger.error(f"Ключ homeworks не список")   
        raise TypeError(f"Ключ homeworks не список")
    if not response["current_date"]:
        logger.error(f"Ключ current_date пустой")
        raise exceptions.KeywordEmpty(f"Ключ current_date пустой")   
    return response["homeworks"]      


def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...
        time.sleep(1)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
        ...


if __name__ == '__main__':
    main() 
