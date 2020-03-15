from mintersdk.minterapi import MinterAPI
from helpers import seed, human_balances, append_tx, convert_all_wallet_coins_to, \
    write_taxes_and_return_remains, write_founders_values, multisend
from mintersdk.sdk.wallet import MinterWallet

from settings import wallet, min_bip, NODE_API_URL
from val import easy_create_multisend_list

# wallet = "Mx20e826a362eb061306ccb0e23d7ab3f18503d344"

w = MinterWallet.create(mnemonic=seed())
private_key = w['private_key']

paying_taxes = False
paying_delegators = True

payouts = {
    'delegators': {
        'percent': 0.1
    },
    'founders': {
        'gorbunov': {
            'wallet': 'Mx5cef09065d68561ad9f61a905c7d0aa230117733',
            'percent': 0.85
        },
        'isheldon': {
            'wallet': 'Mxd315211a50c65e036c14117f6949f2ac91bb6170',
            'percent': 0.15
        }
    },
    'taxes': {
        'wallet': 'Mx50d9e92706ce51341c5f8f0c57afe1950a3ea922',
        'percent': 0.1
    }
}


api = MinterAPI(NODE_API_URL)
balances = human_balances(api, wallet)

# Конвертируем кастомки в BIP
convert_all_wallet_coins_to('BIP', api, wallet, private_key, balances)

# Всего BIP на кошельке
bip_total = balances['BIP'] - min_bip
print(f"Total BIP = {bip_total}")

# Считаем кому сколько
after_taxes = write_taxes_and_return_remains(bip_total, payouts)  # Налоги
delegators_to_be_payed = after_taxes * payouts['delegators']['percent']  # Делегаторам
founders_to_be_payed = after_taxes - delegators_to_be_payed  # Основателям
write_founders_values(founders_to_be_payed, payouts)


# ---------------------------------------------------------------------------------------------
# Генерация multisend списка для оправки
# ---------------------------------------------------------------------------------------------

txs = []

# Налоги
if paying_taxes:
    append_tx(txs, payouts['taxes']['wallet'], payouts['taxes']['value'])

# Основатели
for _, f_dict in payouts['founders'].items():
    append_tx(txs, f_dict['wallet'], f_dict['value'])

# Делегаторы
if paying_delegators:
    delegators_multisend_list = easy_create_multisend_list(delegators_to_be_payed)
    txs = txs + delegators_multisend_list  # Формируем окончательный список


multisend(api, private_key,  wallet, txs, gas_coin='BIP', payload='Stream test payout')


