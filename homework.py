import os
import logging
import telegram
import requests
import sys
import time
from dotenv import load_dotenv
from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверки доступности переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True


def send_message(bot, message):
    """Начата отправка сообщений в ТГ."""
    logging.debug('Сообщение отправлено')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as error:
        logging.error(f'Сообщение не было отправлено {error}', exc_info=True)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    logging.info('Начали запрос к API')
    current_timestamp = timestamp or int(time.time())
    payload = {'from_date': current_timestamp}
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
        raise TypeError("homeworks не словарь")
    if "homeworks" not in response:
        raise KeyError("В ответе API нет ключа homeworks")
    if not isinstance(response["homeworks"], list):
        raise TypeError("Ключ homeworks не список")
    if "current_date" not in response:
        raise KeyError("Ключ current_date пустой")
    return response["homeworks"]


def parse_status(homework):
    """Функция присвоения статуса домашней работе."""
    logging.info("Старт проверки статусов ДЗ")
    if "homework_name" not in homework:
        raise KeyError("В ответе отсутствует ключ homework_name")
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    if status is None:
        raise KeyError("В ответе отсутствует ключ status")
    if status not in (HOMEWORK_VERDICTS):
        raise ValueError(f"Неизвестный статус работы - {status}")
    verdict = HOMEWORK_VERDICTS[homework.get("status")]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    problem = "Проблемы с переменными окружения"
    logging.info('Бот начал работу')
    if not check_tokens():
        logging.critical(problem)
        raise sys.exit(problem)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            homeworks = get_api_answer(timestamp)
            check_response(homeworks)
            if homeworks != []:
                status = parse_status(homeworks.get("homeworks")[0])
                send_message(bot, status)
                logging.debug("Новый статус работы")
            else:
                logging.debug("Нет нового статуса работы")
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
