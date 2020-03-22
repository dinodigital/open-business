import time
from decimal import Decimal

from mintersdk import MinterConvertor
from mintersdk.sdk.transactions import MinterSellAllCoinTx, MinterMultiSendCoinTx

from script.settings import PAYING_TAXES, PAYING_DELEGATORS, ADDRESS, PAYLOAD, PRIVATE_KEY, PAYING_FOUNDERS
from script.settings import TAXES, FOUNDERS, DELEGATORS_PERCENT
from script.settings import API
from script.val import get_delegators_dict


def only_symbol(balances, symbol):
    """True, Если на кошельке только токен symbol"""

    if len(balances) > 1:
        return False
    else:
        if symbol in balances:
            return True


def wait_for_nonce(address, old_nonce):
    while True:
        nonce = API.get_nonce(address)
        if nonce != old_nonce:
            break

        time.sleep(1)


def convert_all_wallet_coins_to(symbol, balances):
    if only_symbol(balances, symbol):
        return

    if symbol in balances.keys():
        del (balances[symbol])

    for i, coin in enumerate(balances, 1):
        if coin == symbol:
            continue

        nonce = API.get_nonce(ADDRESS)
        tx = MinterSellAllCoinTx(
            coin_to_sell=coin, coin_to_buy=symbol, min_value_to_buy=0, nonce=nonce, gas_coin=coin)
        tx.sign(private_key=PRIVATE_KEY)
        r = API.send_transaction(tx.signed_tx)
        print(f'\n{coin} успешно сконвертирован в {symbol}.\n\nSend TX response:\n{r}')

        if i != len(balances):
            print('Waiting for nonce')
            wait_for_nonce(ADDRESS, nonce)


# Генерация и отправка Multisend транзакции
def multisend(txs, pip_total, gas_coin='BIP'):
    nonce = API.get_nonce(ADDRESS)

    # Считаем комиссию
    tx = MinterMultiSendCoinTx(txs, nonce=nonce, gas_coin=gas_coin, payload=PAYLOAD)
    commission = tx.get_fee()

    # Пересчитываем выплаты
    new_pip_total = pip_total - commission

    for i in txs:
        i['value'] = to_bip(Decimal(str(new_pip_total)) * Decimal(str(i['value'])) / Decimal(str(pip_total)))

    # Подписываем транзакцию
    tx.sign(private_key=PRIVATE_KEY)

    # Отправляем транзакцию
    return API.send_transaction(tx.signed_tx)


# Считаем кому сколько платить
def count_money(pip_total):

    taxes_value = 0
    delegators_value = 0
    founders_value = 0

    # Налоги
    if PAYING_TAXES:
        taxes_value = Decimal(str(pip_total)) * Decimal(str(TAXES['percent']))
    after_taxes = pip_total - taxes_value

    # Делегаторам
    if PAYING_DELEGATORS:
        delegators_value = Decimal(str(after_taxes)) * Decimal(str(DELEGATORS_PERCENT))

    # Фаундерам
    if PAYING_FOUNDERS:
        founders_value = after_taxes - delegators_value

    return {
        'taxes': taxes_value,
        'delegators': delegators_value,
        'founders': founders_value
    }


def to_bip(value):
    return MinterConvertor.convert_value(value, 'bip')


def to_pip(value):
    return MinterConvertor.convert_value(value, 'pip')


# ---------------------------------------------------------------------------------------------
# Генерация multisend списка для оправки
# ---------------------------------------------------------------------------------------------
def make_tx_list_from_dict(d):
    """Делает из словаря список из словарей, где каждое ключ-значение начального словаря это отдельный словарь"""

    out_list = []

    for i in d:
        out_list.append(
            {
                'coin': 'BIP',
                'to': i,
                'value': d[i]
            })

    return out_list


def make_multisend_txs_list(payouts):

    taxes_data = []
    delegators_data = []
    founders_data = []

    if PAYING_TAXES:
        taxes_data = {TAXES['wallet']: payouts['taxes']}
        taxes_data = make_tx_list_from_dict(taxes_data)

    if PAYING_DELEGATORS:
        delegators_data = get_delegators_dict(payouts['delegators'])
        delegators_data = make_tx_list_from_dict(delegators_data)

    if PAYING_FOUNDERS:
        founders_data = {founder['wallet']: Decimal(str(founder['percent'])) * payouts['founders'] for founder in FOUNDERS.values()}
        founders_data = make_tx_list_from_dict(founders_data)

    return taxes_data + founders_data + delegators_data
