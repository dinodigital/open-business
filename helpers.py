import time
from decimal import Decimal

from mintersdk import MinterConvertor
from mintersdk.sdk.transactions import MinterSellAllCoinTx, MinterMultiSendCoinTx

from secret.private_key import private_key
from settings import paying_taxes, paying_delegators, wallet, payload
from settings import taxes, founders, delegators_percent
from settings import api
from val import get_delegators_dict


def only_symbol(balances, symbol):
    """True, Если на кошельке только токен symbol"""

    if len(balances) > 1:
        return False
    else:
        if symbol in balances:
            return True


def wait_for_nonce(address, old_nonce):
    while True:
        nonce = api.get_nonce(address)
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

        nonce = api.get_nonce(wallet)
        tx = MinterSellAllCoinTx(
            coin_to_sell=coin, coin_to_buy=symbol, min_value_to_buy=0, nonce=nonce, gas_coin=coin)
        tx.sign(private_key=private_key)
        r = api.send_transaction(tx.signed_tx)
        print(f'\n{coin} успешно сконвертирован в {symbol}.\n\nSend TX response:\n{r}')

        if i != len(balances):
            print('Waiting for nonce')
            wait_for_nonce(wallet, nonce)


# Генерация и отправка Multisend транзакции
def multisend(txs, pip_total, gas_coin='BIP'):
    nonce = api.get_nonce(wallet)

    # Считаем комиссию
    tx = MinterMultiSendCoinTx(txs, nonce=nonce, gas_coin=gas_coin, payload=payload)
    commission = tx.get_fee()

    s = 0
    for i in txs:
        s += i['value']
    print(s)

    # Пересчитываем выплаты
    new_pip_total = pip_total - commission

    for i in txs:
        i['value'] = to_bip(Decimal(str(new_pip_total)) * Decimal(str(i['value'])) / Decimal(str(pip_total)))

    s = 0
    for i in txs:
        s += i['value']
    print(to_bip(s))

    # Подписываем транзакцию
    tx.sign(private_key=private_key)

    # Отправляем транзакцию
    return api.send_transaction(tx.signed_tx)


# Считаем кому сколько платить
def count_money(pip_total):

    taxes_value = 0
    delegators_value = 0

    # Налоги
    if paying_taxes:
        taxes_value = Decimal(str(pip_total)) * Decimal(str(taxes['percent']))
    after_taxes = pip_total - taxes_value

    # Делегаторам
    if paying_delegators:
        delegators_value = Decimal(str(after_taxes)) * Decimal(str(delegators_percent))

    # Фаундерам
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

    if paying_taxes:
        taxes_data = {taxes['wallet']: payouts['taxes']}
        taxes_data = make_tx_list_from_dict(taxes_data)

    if paying_delegators:
        delegators_data = get_delegators_dict(payouts['delegators'])
        delegators_data = make_tx_list_from_dict(delegators_data)

    founders_data = {founder['wallet']: Decimal(str(founder['percent'])) * payouts['founders'] for founder in founders.values()}
    founders_data = make_tx_list_from_dict(founders_data)

    return taxes_data + founders_data + delegators_data
