from pprint import pprint

from helpers import convert_all_wallet_coins_to, count_money, make_multisend_txs_list, to_pip, multisend
from settings import ADDRESS
from settings import API

# Получаем балансы кошелька
balances = API.get_balance(ADDRESS)['result']['balance']

# Конвертируем балансы в нужный нам ТОКЕН
coins_converted = convert_all_wallet_coins_to('BIP', balances)

# Если было конвертация, запрашиваем баланс BIP по новой
if coins_converted:
    balances = API.get_balance(ADDRESS)['result']['balance']

# Всего BIP на кошельке
pip_total = balances['BIP']
print(f"Pip total (1) = {pip_total}")

# Считаем кому сколько денег переводить
payouts = count_money(pip_total)

# Делаем список для multisend транзакции
txs = make_multisend_txs_list(payouts)

# Отправляем выплату
print(multisend(txs, pip_total, gas_coin='BIP'))

# # Сообщаем об успешном выполнении скрипта
# if tx_response['result']['code'] == 0:
#     print(f'Multisend Транзакция успешно отправлена\nResponse: {tx_response["result"]}')
