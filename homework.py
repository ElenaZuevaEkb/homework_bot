from dotenv import load_dotenv
import os
import logging
import telegram
import requests
import sys
import time
from http import HTTPStatus


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
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверки доступности переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logging.critical("Отсутствует PRACTICUM_TOKEN")
        raise Exception("Отсутствует PRACTICUM_TOKEN")
    if TELEGRAM_TOKEN is None:
        logging.critical("Отсутствует TELEGRAM_TOKEN")
        raise Exception("Отсутствует TELEGRAM_TOKEN")
    if TELEGRAM_CHAT_ID is None:
        logging.critical("Отсутствует TELEGRAM_CHAT_ID")
        raise Exception("Отсутствует TELEGRAM_CHAT_ID")
    return TELEGRAM_CHAT_ID and TELEGRAM_TOKEN and PRACTICUM_TOKEN


def send_message(bot, message):
    """Функция отправки сообщений в ТГ."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено')
    except Exception as error:
        logging.error(f'Сообщение не было отправлено {error}')
        raise Exception('Сообщение не было отправлено')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    logging.info('Начали запрос к API')
    CURRENT_TIMESTAMP = timestamp or int(time.time())
    payload = {'from_date': CURRENT_TIMESTAMP}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        raise KeyError(f'Сбой в работе программы: {error}')
    if response.status_code != HTTPStatus.OK:
        raise requests.HTTPError(response)
    return response.json()


def check_response(response):
    """Функция проверки ответа API на соответствие."""
    if not isinstance(response, dict):
        logger.error("homeworks не словарь")
        raise TypeError("homeworks не словарь")
    if "homeworks" not in response:
        logger.error("В ответе API нет ключа homeworks")
        raise KeyError("В ответе API нет ключа homeworks")
    if not isinstance(response["homeworks"], list):
        logger.error("Ключ homeworks не список")
        raise TypeError("Ключ homeworks не список")
    if not response["current_date"]:
        logger.error("Ключ current_date пустой")
        raise Exception.KeywordEmpty("Ключ current_date пустой")
    return response["homeworks"]


def parse_status(homework):
    """Функция присвоения статуса домашней работе."""
    logging.info("Старт проверки статусов ДЗ")
    if "homework_name" not in homework:
        raise KeyError("В ответе отсутствует ключ homework_name")
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    if status not in (HOMEWORK_VERDICTS):
        raise ValueError(f"Неизвестный статус работы - {status}")
    verdict = HOMEWORK_VERDICTS[homework.get("status")]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.info('Бот начал работу')
    if not check_tokens():
        logger.critical("Проблемы с переменными окружения")
        raise ValueError("Проблемы с переменными окружения")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            homeworks = get_api_answer(timestamp)
            check_response(homeworks)
            if homeworks != []:
                status = parse_status(homeworks.get("homeworks")[0])
                send_message(bot, status)
                logger.debug("Новый статус работы")
            else:
                logger.debug("Нет нового статуса работы")
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
