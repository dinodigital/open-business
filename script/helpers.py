import time
from decimal import Decimal

from mintersdk import MinterConvertor
from mintersdk.sdk.transactions import MinterSellAllCoinTx, MinterMultiSendCoinTx
from mintersdk.sdk.wallet import MinterWallet

from script.settings import PAYING_TAXES, PAYING_DELEGATORS, ADDRESS, PAYLOAD, PRIVATE_KEY, PAYING_FOUNDERS
from script.settings import TAXES, FOUNDERS, DELEGATORS_PERCENT
from script.settings import API
from script.val import get_delegators_dict


def to_bip(value):
    """
    Короткая функция конвертации в BIP
    """
    return MinterConvertor.convert_value(value, 'bip')


def to_pip(value):
    """
    Короткая функция конвертации в PIP
    """
    return MinterConvertor.convert_value(value, 'pip')


def only_symbol(balances, symbol):
    """
    True, если на балансе кошелька только symbol
    """

    if len(balances) > 1:
        return False
    else:
        if symbol in balances:
            return True


def wait_for_nonce(old_nonce):
    """
    Прерывается, если новый nonce != старый nonce
    """
    while True:
        nonce = API.get_nonce(ADDRESS)
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
            wait_for_nonce(nonce)


def make_tx_list_from_dict(d):
    """
    Делает из словаря список из словарей, где каждое ключ-значение начального словаря это отдельный словарь
    """

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
    """
    Складывае 2 словаря, суммируя значения у повторяющихся ключей
    """
    for address in new_dict:
        if address in main_dict.keys():
            main_dict[address] += Decimal(str(new_dict[address]))
        else:
            main_dict[address] = Decimal(str(new_dict[address]))


def make_multisend_txs_list(pip_total):
    """
    Генерируем txs list для отправки в multisend транзакцию
    """

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


def recalculate_payouts_and_convert_to_bip(txs, commission, pip_total):
    """
    Формирует новый список txs с учетом multisend комиссии
    И конвертирует сумму каждой выплаты в BIP
    """
    new_pip_total = pip_total - commission

    for tx in txs:
        tx['value'] = to_bip(new_pip_total * Decimal(str(tx['value'])) / Decimal(str(pip_total)))

    return txs


def calc_commission(txs, gas_coin="BIP"):
    """
    Считает комиссию за транзакцию
    """
    return MinterMultiSendCoinTx(txs, nonce=1, gas_coin=gas_coin, payload=PAYLOAD).get_fee()


def multisend(txs, pip_total, gas_coin='BIP'):
    """
    Генерация и отправка Multisend транзакции с кошелька под 0 с учетом комиссии
    """

    # Пересчитываем выплаты с учетом комиссии и конвертируем в BIP
    commission = calc_commission(txs)
    txs = recalculate_payouts_and_convert_to_bip(txs, commission, pip_total)

    # Делаем multisend транзакцию
    nonce = API.get_nonce(ADDRESS)
    tx = MinterMultiSendCoinTx(txs, nonce=nonce, gas_coin=gas_coin, payload=PAYLOAD)
    tx.sign(private_key=PRIVATE_KEY)

    # Отправляем транзакцию
    print(API.send_transaction(tx.signed_tx))

    return nonce


def split_txs(txs):
    """
    Делает список из списков по 100 транзакций
    """
    txs_list = []

    x = 0
    temp_list = []

    for num, tx in enumerate(txs, 1):
        temp_list.append(tx)
        x += 1

        if x == 60 or num == len(txs):
            txs_list.append(temp_list)
            temp_list = []
            x = 0

    return txs_list


def calc_pip_total(txs):
    """
    Считает общую сумму pip всех получателей в этом списке
    """
    pip_total = 0

    for i in txs:
        pip_total += i['value']

    return pip_total


# test = []
# for i in range(102):
#     test.append({'coin': 'BIP', 'to': MinterWallet.create()['address'], 'value': Decimal(str(to_pip(0.001)))})


def smart_multisend(all_txs, gas_coin='BIP'):
    """
    Генерирует multisend на каждые 100 адресов в all_txs
    """

    # Проверяем не превышают ли комиссии сумму выплат
    commissions, pip_total = calc_commission(all_txs), calc_pip_total(all_txs)
    if commissions > pip_total:
        print('Ошибка: Комиссии превышают сумму выплаты')
        return

    # Делаем из общего списка транзакций списки по 100 адресов
    txs_list = split_txs(all_txs)

    # Делаем multisend
    for txs in txs_list:
        pip_total = calc_pip_total(txs)
        nonce = multisend(txs, pip_total, gas_coin=gas_coin)
        if len(txs_list) > 1:
            wait_for_nonce(nonce)

    return


# smart_multisend(test, gas_coin='BIP')
