import time

from mintersdk.minterapi import MinterAPI
from mintersdk.sdk.transactions import MinterSellAllCoinTx, MinterMultiSendCoinTx

from secret.private_key import private_key
from settings import NODE_API_URL, payouts, paying_taxes, paying_delegators, wallet, payload
from val import easy_create_multisend_list

api = MinterAPI(NODE_API_URL)


def only_symbol(human_balances, symbol):
    """True, Если на кошельке только BIP"""

    if len(human_balances) > 1:
        return False
    else:
        if symbol in human_balances:
            return True


def human_balances(wallet):
    """Возвращает нормальные балансы, а не строки с кучей нулей"""
    wallet_balance_data = api.get_balance(wallet)
    balances = wallet_balance_data['result']['balance']

    human_balances = {}

    for coin in balances:
        human_balances[coin] = int(balances[coin])/1000000000000000000

    return human_balances


def append_tx(txs, to, value):
    txs.append({
        'coin': 'BIP',
        'to': to,
        'value': value
    })


def wait_for_nonce(address, old_nonce):
    while True:
        nonce = api.get_nonce(address)
        if nonce != old_nonce:
            break

        time.sleep(1)


def convert_all_wallet_coins_to(symbol, wallet, private_key, balances):
    """
    Конвертируем все монеты в кошельке в монету symbol
    :param symbol: COINNAME (str)
    :param wallet:
    :param private_key:
    :param balances:
    :return:
    """
    if not only_symbol(balances, symbol):

        if symbol in balances.keys():
            del (balances[symbol])

        i = len(balances)
        for coin in balances:

            if coin != symbol:
                nonce = api.get_nonce(wallet)
                tx = MinterSellAllCoinTx(coin_to_sell=coin, coin_to_buy=symbol, min_value_to_buy=0, nonce=nonce,
                                         gas_coin=coin)
                tx.sign(private_key=private_key)
                r = api.send_transaction(tx.signed_tx)
                print(f'\n{coin} успешно сконвертирован в {symbol}.\n\nSend TX response:\n{r}')

                i -= 1
                if i > 0:
                    print('Waiting for nonce')
                    wait_for_nonce(wallet, nonce)


def write_taxes_and_return_remains(bip_total, payouts):
    """Вносим значение налогов в словарь и возвращаем остаток для дальнейшего распределения"""
    payouts['taxes']['value'] = bip_total * payouts['taxes']['percent']
    return bip_total - payouts['taxes']['value']


def write_founders_values(to_be_payed, payouts):
    """Вносим значения выплат для каждого основателя"""
    for _, f_dict in payouts['founders'].items():
        f_dict['value'] = to_be_payed * f_dict['percent']


# Генерация и отправка Multisend транзакции
def multisend(txs, bip_total, gas_coin='BIP'):
    nonce = api.get_nonce(wallet)

    # Считаем комиссию
    tx = MinterMultiSendCoinTx(txs, nonce=nonce, gas_coin=gas_coin, payload=payload)
    commission = tx.get_fee()/1000000000000000000

    print(commission)

    # Пересчитываем выплаты
    bip_total = bip_total - commission
    payouts = count_money(bip_total)
    txs = make_txs(payouts)
    tx.txs = txs

    tx.sign(private_key=private_key)
    r = api.send_transaction(tx.signed_tx)

    print(f'Multisend успешно отправлен.\n\nSend TX response:\n{r}')
    return tx


# Считаем кому сколько платить
def count_money(bip_total):
    after_taxes = write_taxes_and_return_remains(bip_total, payouts)  # Налоги
    payouts['delegators']['to_be_payed'] = after_taxes * payouts['delegators']['percent']  # Делегаторам
    founders_to_be_payed = after_taxes - payouts['delegators']['to_be_payed']  # Основателям
    write_founders_values(founders_to_be_payed, payouts)
    return payouts


# ---------------------------------------------------------------------------------------------
# Генерация multisend списка для оправки
# ---------------------------------------------------------------------------------------------

def make_txs(payouts):
    txs = []

    # Налоги
    if paying_taxes:
        append_tx(txs, payouts['taxes']['wallet'], payouts['taxes']['value'])

    # Основатели
    for _, f_dict in payouts['founders'].items():
        append_tx(txs, f_dict['wallet'], f_dict['value'])

    # Делегаторы
    if paying_delegators:
        delegators_multisend_list = easy_create_multisend_list(payouts['delegators']['to_be_payed'])
        txs = txs + delegators_multisend_list  # Формируем окончательный список

    return txs
