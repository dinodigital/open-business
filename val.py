'''
Скрипт который вытаскивает всех делегаторов, которым должна идти выплата по токену GORBUNOV
'''

import requests
import settings
from settings import wallet


# ------------------------------------------------------------------------------
# Формируем словарь с теми, кому полагается выплата
# ------------------------------------------------------------------------------
def get_vals_list():
    '''
    Получаем актуальный список публичных ключей всех валидаторов
    '''
    print('* Получаем список валидаторов')

    # Получаем последний блок
    net_status_url = f'{settings.NODE_API_URL}/status'
    last_block = requests.get(net_status_url).json()['result']['latest_block_height']

    # Получаем список валидаторов из последнего блока
    get_val_url = f'{settings.NODE_API_URL}/validators?height={last_block}'
    r_vals = requests.get(get_val_url).json()['result']

    vals_list = []
    for val in r_vals:
        vals_list.append(val['pub_key'])

    print('+ Список валидаторов получен')
    return vals_list


def get_gelegators_list_by_node(node_key):
    '''
    Получаем список всех делегаторов в ноде
    '''
    URL = f'{settings.EXPLORER_API_URL}api/v1/validators/{node_key}'
    r = requests.get(URL)
    delegators_data = r.json()['data']['delegator_list']

    delegators = {}
    for delegator in delegators_data:
        if delegator['coin'] == 'GORBUNOV':
            delegators[delegator['address']] = float(delegator['value'])

    return delegators


def get_all_delegators():
    '''
    Получаем общий словарь со всеми делегаторами монеты
    Если монета делегирована в несколько нод, то суммирует значения
    '''
    print('* Получаем всех делегаторов монеты')

    vals_list = get_vals_list()  # Получили всех делегаторов
    all_delegators = {}

    for val in vals_list:
        delegators = get_gelegators_list_by_node(val)
        if all_delegators:
            for delegator in delegators:
                if delegator in all_delegators.keys():
                    all_delegators[delegator] = delegators[delegator] + all_delegators[delegator]
                else:
                    all_delegators[delegator] = delegators[delegator]
        else:
            all_delegators = delegators

    print('+ Все делегаторы монеты получены')
    return all_delegators


def get_all_payed_delegators():
    '''
    Словарь с теми делегаторами, которым полагается выплата
    '''
    print('* Определяю тех, кому полагается выплата')

    all_delegators = get_all_delegators()
    all_payed_delegators = {}

    for delegator in all_delegators:
        coins = all_delegators[delegator]
        if coins >= settings.MIN_COINS_DELEGATED and delegator not in settings.STOP_LIST:
            all_payed_delegators[delegator] = all_delegators[delegator]

    print('+ Все, кому полагается выплата успешно определены')
    return all_payed_delegators


# ------------------------------------------------------------------------------
# Вычисляем количество делегированных монет, которые участвуют в распределении прибыли
# ------------------------------------------------------------------------------
def get_total_delegated_coins(payed_delegators_list):
    '''
    Возвращает количество монет, участвующее в распределении выплаты
    '''
    total_delegated_coins = 0
    for d in payed_delegators_list:
        total_delegated_coins += payed_delegators_list[d]

    return total_delegated_coins


# ------------------------------------------------------------------------------
# Получаем сумму выплаты
# ------------------------------------------------------------------------------
def get_wallet_balances(wallet_address):
    '''
    Возвращает балансы всех монет на кошельке
    '''
    address = requests.get(f'{settings.EXPLORER_API_ADDRESS}{wallet_address}').json()
    balances = address['data']['balances']
    return balances


def get_bip_balance(wallet_address):
    '''
    Возвращает баланс BIP на кошельке
    '''
    balances = get_wallet_balances(wallet_address)
    for i in balances:
        if i['coin'] == 'BIP':
            return i['amount']


# ------------------------------------------------------------------------------
# Генерируем список для мультисенда
# ------------------------------------------------------------------------------

# Список для мультисенда: list[dict{coin, to, value}]
def create_multisend_list(total_delegated_coins, payed_delegators_list, to_be_payed, pay_coin_name):
    '''
    Создаем готовый список для Mutisend транзакции
    list[dict{coin, to, value}]

    total_delegated_coins – Всего монет в делегировании
    payed_delegators_list — Список кошельков, кому полагается выплата
    to_be_payed — Денег на выплату
    pay_coin_name — Монета, в которой производится выплата
    '''
    multisend_list = []
    for Mx in payed_delegators_list:
        percent = payed_delegators_list[Mx] * 100 / total_delegated_coins
        value = to_be_payed * percent * 0.01
        multisend_list.append({'coin': pay_coin_name,
                               'to': Mx,
                               'value': value})
    return multisend_list


def easy_create_multisend_list(to_be_payed):
    # Все, кому полагается выплата
    payed_delegators_list = get_all_payed_delegators()

    # Количество монет, которое участвует в распределении выплаты
    total_delegated_coins = get_total_delegated_coins(payed_delegators_list)

    multisend_list = create_multisend_list(total_delegated_coins, payed_delegators_list, to_be_payed, 'BIP')

    return multisend_list


# # ------------------------------------------------------------------------------
# # Выводим инфу
# # ------------------------------------------------------------------------------
# def print_info():
#     for i in multisend_list:
#         for j in payed_delegators_list:
#             if j == i['to']:
#                 print(f"{i['to']}: {payed_delegators_list[j]} {settings.TOKEN} / {i['value']} {i['coin']}")
#
#     print(f'''
#     -------------------------------------------------
#     Баланс кошелька: {bip_balance} BIP
#     Будет выплачено: {to_be_payed} BIP
#
#     В выплате участвуют:
#     — {len(payed_delegators_list)} адресов
#     — {total_delegated_coins} GORBUNOV
#
#     1 {settings.TOKEN} – это:
#     ~ {1 * 100 / total_delegated_coins} % от общей суммы
#     ~ {(1 * 100 / total_delegated_coins) * to_be_payed * 0.01} BIP
#     --------------------------------------------------
#     ''')
#
#
# print_info()
