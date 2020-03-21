from helpers import human_balances, append_tx, convert_all_wallet_coins_to, \
    write_taxes_and_return_remains, write_founders_values, multisend, count_money, make_txs

from secret.private_key import private_key
from settings import wallet, min_bip, paying_taxes, paying_delegators
from val import easy_create_multisend_list

# ---------------------------------------------------------------------------------------------
# Считаем кому сколько переводить
# ---------------------------------------------------------------------------------------------

# Получаем балансы кошелька
balances = human_balances(wallet)

# Конвертируем кастомки в BIP
convert_all_wallet_coins_to('BIP', wallet, private_key, balances)

# Всего BIP на кошельке
bip_total = balances['BIP']

# Считаем кому сколько денег переводить
payouts = count_money(bip_total)

# Делаем miltisend список
txs = make_txs(payouts)


# ---------------------------------------------------------------------------------------------
# Отправляем выплату
# ---------------------------------------------------------------------------------------------

multisend(txs, bip_total, gas_coin='BIP')


