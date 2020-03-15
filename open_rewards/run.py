import settings, wallet, val

import mintersdk
from mintersdk.minterapi import MinterAPI
from mintersdk.sdk.wallet import MinterWallet
from mintersdk.sdk.transactions import MinterTx, MinterSendCoinTx, MinterMultiSendCoinTx

print('Connecting Node...')
API = MinterAPI(settings.NODE_API_URL, **settings.TIMEOUTS)

print('Making wallet data...')
wallet_from = wallet.wallet_from

# Список для мультисенда (list[dict{coin, to, value}])
print('Generating multisend list...')
w_dict = val.multisend_list


def send(wallet_from, wallet_to, coin, value, gas_coin='BIP', payload=''):
    nonce = API.get_nonce(wallet_from['address'])
    send_tx = MinterSendCoinTx(coin, wallet_to, value, nonce=nonce, gas_coin=gas_coin, payload=payload)
    send_tx.sign(wallet_from['private_key'])
    r = API.send_transaction(send_tx.signed_tx)
    print(f'Send TX response:\n{r}')
    return send_tx


# Генерация и отправка Multisend транзакции
def multisend(wallet_from, w_dict, gas_coin='BIP', payload=''):
    nonce = API.get_nonce(wallet_from['address'])
    tx = MinterMultiSendCoinTx(w_dict, nonce=nonce, gas_coin=gas_coin, payload=payload)
    tx.sign(wallet_from['private_key'])
    r = API.send_transaction(tx.signed_tx)
    print(f'Send TX response:\n{r}')
    return tx


print('MultiSending...')
multisend(wallet_from, w_dict, payload='Тестовая выплата делегаторам GORBUNOV / @gorbunov_exe ')
