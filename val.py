"""
Скрипт который вытаскивает всех делегаторов, которым должна идти выплата по токену GORBUNOV
"""
from pprint import pprint

import requests
from mintersdk.minterapi import MinterAPI
from mintersdk import MinterConvertor

import settings

api = MinterAPI(settings.NODE_API_URL)


# ------------------------------------------------------------------------------
# Формируем словарь с теми, кому полагается выплата
# ------------------------------------------------------------------------------

# Получаем список активных валидаторов
# def get_vals_list():
#     get_status = api.get_status()
#     block_height = get_status['result']['tm_status']['sync_info']['latest_block_height']
#     block = api.get_block(block_height)
#
#     vals_list = []
#     for validator in block['result']['validators']:
#         vals_list.append(validator['pub_key'])
#
#     return vals_list

# # Получаем список активных валидаторов
# def get_vals_list():
#     validators_data = api.get_validators(limit=256)['result']
#     return [key['pub_key'] for key in validators_data]
#
#
# def get_gelegators_list_by_node(node_key):
#     pprint(api.get_candidates(include_stakes=True))
#
#
#


def get_delegators_from_validator(validator, delegators):
    """
    Сканирует делегаторов в выбранном валидаторе и считает делегированный стейк
    Возвращает словарь {wallet: pip} по всем делегатором одного конкретного валидатора
    :param validator: dict
    :param delegators: dict
    :return: dict: {wallet: pip}
    """
    for delegator in validator['stakes']:
        if delegator['coin'] == settings.DELEGATED_TOKEN \
                and delegator['owner'] not in settings.STOP_LIST \
                and delegator['value'] >= settings.MIN_COINS_DELEGATED:
            if delegator['owner'] not in delegators.keys():
                delegators[delegator['owner']] = delegator['value']
            else:
                delegators[delegator['owner']] += delegator['value']
    return delegators


# Получаем всех делегаторов
def get_delegators_dict(total_pip):
    """
    Получаем всех делегаторов и количество токенов на кошельке
    :return: dict: {wallet: value}
    """

    validators = api.get_candidates(include_stakes=True)['result']
    delegators = {}

    # Получаем словарь всех делегаторов и количество их делегированных токенов
    for validator in validators:
        try:
            get_delegators_from_validator(validator, delegators)
        except KeyError:
            continue

    # Получаем сумму выплаты в BIP для каждого делегатора
    tokens_sum = sum(delegators.values())  # 100% токенов, участвующих в распределении
    for key in delegators:
        delegators[key] = total_pip * delegators[key] / tokens_sum

    return delegators


# print(len(delegators))
#
# for key in delegators:
#     print(key, delegators[key])
#
# print(sum(delegators.values()))  # 100% токенов, участвующих в распределении


# delegators = [address: stake for delegator_slot in validators['stakes']]
# pprint(validators[0])


# def get_gelegators_list_by_node(node_key):
#     """
#     Получаем список всех делегаторов в ноде
#     """
#     url = f'{settings.EXPLORER_API_URL}api/v1/validators/{node_key}'
#     r = requests.get(url)
#     delegators_data = r.json()['data']['delegator_list']
#
#     delegators = {}
#     for delegator in delegators_data:
#         if delegator['coin'] == 'GORBUNOV':
#             delegators[delegator['address']] = float(delegator['value'])
#
#     return delegators


# def get_all_delegators():
#     """
#     Получаем общий словарь со всеми делегаторами монеты
#     Если монета делегирована в несколько нод, то суммирует значения
#     """
#     print('* Получаем всех делегаторов монеты')
#
#     vals_list = get_vals_list()  # Получили всех делегаторов
#     all_delegators = {}
#
#     for val in vals_list:
#         delegators = get_gelegators_list_by_node(val)
#         if all_delegators:
#             for delegator in delegators:
#                 if delegator in all_delegators.keys():
#                     all_delegators[delegator] = delegators[delegator] + all_delegators[delegator]
#                 else:
#                     all_delegators[delegator] = delegators[delegator]
#         else:
#             all_delegators = delegators
#
#     print('+ Все делегаторы монеты получены')
#     return all_delegators
#
#
# def get_all_payed_delegators():
#     """
#     Словарь с теми делегаторами, которым полагается выплата
#     """
#     print('* Определяю тех, кому полагается выплата')
#
#     all_delegators = get_all_delegators()
#     all_payed_delegators = {}
#
#     for delegator in all_delegators:
#         coins = all_delegators[delegator]
#         if coins >= settings.MIN_COINS_DELEGATED and delegator not in settings.STOP_LIST:
#             all_payed_delegators[delegator] = all_delegators[delegator]
#
#     print('+ Все, кому полагается выплата успешно определены')
#     return all_payed_delegators
#
#
# # ------------------------------------------------------------------------------
# # Вычисляем количество делегированных монет, которые участвуют в распределении прибыли
# # ------------------------------------------------------------------------------
# def get_total_delegated_coins(payed_delegators_list):
#     """
#     Возвращает количество монет, участвующее в распределении выплаты
#     """
#     total_delegated_coins = 0
#     for d in payed_delegators_list:
#         total_delegated_coins += payed_delegators_list[d]
#
#     return total_delegated_coins
#
#
# # ------------------------------------------------------------------------------
# # Получаем сумму выплаты
# # ------------------------------------------------------------------------------
# def get_wallet_balances(wallet_address):
#     """
#     Возвращает балансы всех монет на кошельке
#     """
#     address = requests.get(f'{settings.EXPLORER_API_ADDRESS}{wallet_address}').json()
#     balances = address['data']['balances']
#     return balances
#
#
# def get_bip_balance(wallet_address):
#     """
#     Возвращает баланс BIP на кошельке
#     """
#     balances = get_wallet_balances(wallet_address)
#     for i in balances:
#         if i['coin'] == 'BIP':
#             return i['amount']
#
#
# # ------------------------------------------------------------------------------
# # Генерируем список для мультисенда
# # ------------------------------------------------------------------------------
#
# # Список для мультисенда: list[dict{coin, to, value}]
# def create_multisend_list(total_delegated_coins, payed_delegators_list, to_be_payed, pay_coin_name):
#     """
#     Создаем готовый список для Mutisend транзакции
#     list[dict{coin, to, value}]
#
#     total_delegated_coins – Всего монет в делегировании
#     payed_delegators_list — Список кошельков, кому полагается выплата
#     to_be_payed — Денег на выплату
#     pay_coin_name — Монета, в которой производится выплата
#     """
#     multisend_list = []
#     for Mx in payed_delegators_list:
#         percent = payed_delegators_list[Mx] * 100 / total_delegated_coins
#         value = to_be_payed * percent * 0.01
#         multisend_list.append({'coin': pay_coin_name,
#                                'to': Mx,
#                                'value': value})
#     return multisend_list
#
#
# def easy_create_multisend_list(to_be_payed):
#     # Все, кому полагается выплата
#     payed_delegators_list = get_all_payed_delegators()
#
#     # Количество монет, которое участвует в распределении выплаты
#     total_delegated_coins = get_total_delegated_coins(payed_delegators_list)
#
#     multisend_list = create_multisend_list(total_delegated_coins, payed_delegators_list, to_be_payed, 'BIP')
#
#     return multisend_list

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
