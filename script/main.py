from script.helpers import convert_all_wallet_coins_to, make_multisend_txs_list, multisend
from script.settings import ADDRESS
from script.settings import API

# Получаем балансы кошелька
balances = API.get_balance(ADDRESS)['result']['balance']

# Конвертируем балансы в нужный нам ТОКЕН
coins_converted = convert_all_wallet_coins_to('BIP', balances)

# Если было конвертация, запрашиваем баланс BIP по новой
if coins_converted:
    balances = API.get_balance(ADDRESS)['result']['balance']

# Всего BIP на кошельке
pip_total = balances['BIP']

# Делаем список для multisend транзакции
txs = make_multisend_txs_list(pip_total)

# Отправляем выплату
print(multisend(txs, pip_total, gas_coin='BIP'))
