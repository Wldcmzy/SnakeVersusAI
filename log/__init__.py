from pathlib import Path
import logging
import datetime

LOG_FORDER = 'logs'

def create_logger():
    name = 'start at ' + str(datetime.datetime.now()).replace(':', '-').split('.')[0] + '.log'
    path = Path(__file__).parent / LOG_FORDER / name

    formatter = logging.Formatter('%(asctime)s <%(levelname)s>: %(message)s')

    handlerF = logging.FileHandler(path)
    handlerF.setLevel(logging.DEBUG)
    handlerF.setFormatter(formatter)

    handlerC = logging.StreamHandler()
    handlerC.setLevel(logging.INFO)
    handlerC.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handlerF)
    logger.addHandler(handlerC)

    return logger

logger = create_logger()