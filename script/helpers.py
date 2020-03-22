import time
from decimal import Decimal

from mintersdk import MinterConvertor
from mintersdk.sdk.transactions import MinterSellAllCoinTx, MinterMultiSendCoinTx

from script.settings import PAYING_TAXES, PAYING_DELEGATORS, ADDRESS, PAYLOAD, PRIVATE_KEY, PAYING_FOUNDERS
from script.settings import TAXES, FOUNDERS, DELEGATORS_PERCENT
from script.settings import API
from script.val import get_delegators_dict


def only_symbol(balances, symbol):
    """
    True, если на балансе кошелька только symbol
    """

    if len(balances) > 1:
        return False
    else:
        if symbol in balances:
            return True


def wait_for_nonce(address, old_nonce):
    """
    Прерывается, если новый nonce != старый nonce
    """
    while True:
        nonce = API.get_nonce(address)
        if nonce != old_nonce:
            break

        time.sleep(1)


def convert_all_wallet_coins_to(symbol, balances):
    """
    Конвертирует все монеты на кошельке в symbol
    """
    if only_symbol(balances, symbol):
        return

    del (balances[symbol])
    for i, coin in enumerate(balances, 1):
        if coin == symbol:
            continue

        nonce = API.get_nonce(ADDRESS)
        tx = MinterSellAllCoinTx(coin_to_sell=coin, coin_to_buy=symbol, min_value_to_buy=0, nonce=nonce, gas_coin=coin)
        tx.sign(private_key=PRIVATE_KEY)
        API.send_transaction(tx.signed_tx)
        print(f'{coin} успешно сконвертирован в {symbol}')

        if i != len(balances):
            print('Waiting for nonce')
            wait_for_nonce(ADDRESS, nonce)


def multisend(txs, pip_total, gas_coin='BIP'):
    """
    Генерация и отправка Multisend транзакции с кошелька под 0 с учетом комиссии
    """

    # Получаем nonce
    nonce = API.get_nonce(ADDRESS)

    # Считаем комиссию
    tx = MinterMultiSendCoinTx(txs, nonce=nonce, gas_coin=gas_coin, payload=PAYLOAD)
    commission = tx.get_fee()

    # Пересчитываем выплаты с учетом комиссии и конвертируем в BIP
    new_pip_total = pip_total - commission
    for i in txs:
        i['value'] = to_bip(new_pip_total * Decimal(str(i['value'])) / Decimal(str(pip_total)))

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


def sum_2_dicts(new_dict, main_dict):
    for address in new_dict:
        if address in main_dict.keys():
            main_dict[address] += Decimal(str(new_dict[address]))
        else:
            main_dict[address] = Decimal(str(new_dict[address]))


def make_multisend_txs_list(pip_total):

    if not PAYING_FOUNDERS and not PAYING_DELEGATORS and not PAYING_TAXES:
        return

    total_dict = {}

    taxes_value = 0
    delegators_value = 0
    founders_value = 0

    if PAYING_TAXES:
        taxes_value = pip_total * Decimal(str(sum(TAXES.values())))
        taxes_data = {address: Decimal(str(percent)) * pip_total for address, percent in TAXES.items()}
        sum_2_dicts(taxes_data, total_dict)

    after_taxes = pip_total - taxes_value

    if PAYING_DELEGATORS:
        delegators_value = after_taxes * Decimal(str(DELEGATORS_PERCENT))
        delegators_data = get_delegators_dict(delegators_value)
        sum_2_dicts(delegators_data, total_dict)

    if PAYING_FOUNDERS:
        founders_value = after_taxes - delegators_value
        founders_data = {address: Decimal(str(percent)) * founders_value for address, percent in FOUNDERS.items()}
        sum_2_dicts(founders_data, total_dict)

    return make_tx_list_from_dict(total_dict)
