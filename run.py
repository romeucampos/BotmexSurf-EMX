import requests
import logging
import time
import json
from math import log
from emx.rest_api import RestApi


logging.basicConfig(
                    handlers=[
                        logging.FileHandler("log.log"),
                        logging.StreamHandler()
                    ],
                    format='%(asctime)s - %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)

logging.info('BotmexSurf-EMX')
logging.info('Ideia @MatheusGrijo')
logging.info('Algorítmo @romeucampos')
logging.info('Load config...')

try:
    config = json.loads(open('config.txt').read())
    client = RestApi(config["key"], config["secret"], config['url'])
    accounts = client.get_account()['accounts'][0]['trader_id']
    balance = client.get_balances(accounts)['token_balances']['btc']

except Exception as e:
    logging.info(e)
    

def profit():
    balance_last = client.get_balances(accounts)['token_balances']['btc']
    rsp = log(round(float(balance_last), 4)/round(float(balance), 4)) * 100
    return f'balance last: {balance_last} - profit: {rsp:.2f}%'


def trend():
    url = 'https://anubis.website/api/anubis/trend/'
    rsp = requests.get(url).json()['data']
    return rsp[0]


def first_order():
    sinal_first = trend()
    while True:
        try:
            signal = trend()
            logging.info(f'{signal} - {profit()}')

            if signal['trend'] != sinal_first['trend']:
                if signal['trend'] == 'LONG':
                    long = client.create_new_order(
                                                            contract_code='BTC-PERP',
                                                            order_type='market',
                                                            order_side='buy',
                                                            size=str(config["amount_btc"]))
                    
                    logging.info(long)
                    time.sleep(config["interval"])
                else:
                    short = client.create_new_order(
                                                            contract_code='BTC-PERP',
                                                            order_type='market',
                                                            order_side='sell',
                                                            size=str(config["amount_btc"]))
                    
                    logging.info(short)
                    time.sleep(config["interval"])
                break
            time.sleep(config["interval"])

        except Exception as e:
            logging.info(e)
            break


def simple_strategy():
    while True:
        try:
            signal = trend()
            if signal['trend'] == 'LONG':
                position = client.get_positions()[0]['quantity']
                if config["amount_btc"] > float(position):
                    long = client.create_new_order(
                                                            contract_code='BTC-PERP',
                                                            order_type='market',
                                                            order_side='buy',
                                                            size=str(config["amount_btc"]*2))
                    
                    logging.info(signal, long)

            if signal['trend'] == 'SHORT':
                position = client.get_positions()[0]['quantity']
                if - config["amount_btc"] < float(position):
                    short = client.create_new_order(
                                                            contract_code='BTC-PERP',
                                                            order_type='market',
                                                            order_side='sell',
                                                            size=str(config["amount_btc"]*2))
                    
                    logging.info(signal, short)

            logging.info(f'{signal} - {profit()}')
            time.sleep(config["interval"])

        except Exception as e:
            logging.info(e)
            break


def main():
    first_order()
    simple_strategy()

if __name__ == '__main__':
    main()
