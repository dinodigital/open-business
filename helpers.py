import time

from mintersdk.sdk.transactions import MinterSellAllCoinTx, MinterMultiSendCoinTx


def only_symbol(human_balances, symbol):
    """True, Если на кошельке только BIP"""

    if len(human_balances) > 1:
        return False
    else:
        if symbol in human_balances:
            return True


def seed():
    with open('local/seed.txt', 'r') as f:
        return f.read()


def human_balances(api, wallet):
    """Возвращает нормальные балансы, а не строки с кучей нулей"""
    wallet_balance_data = api.get_balance(wallet)
    balances = wallet_balance_data['result']['balance']

    human_balances = {}

    for coin in balances:
        human_balances[coin] = int(balances[coin])/1000000000000000000

    return human_balances


def append_tx(txs, to, value):
    txs.append({
        'coin': 'BIP',
        'to': to,
        'value': value
    })


def count_commissions(num_of_recipients, payload):
    """
    Счиатет комиссии на multisend в сети Minter
    :param num_of_recipients: int
    :param payload: str
    :return: float
    """
    return (10+(num_of_recipients-1)*5)*0.001


def wait_for_nonce(api, address, old_nonce):
    while True:
        nonce = api.get_nonce(address)
        if nonce != old_nonce:
            break

        time.sleep(1)


def convert_all_wallet_coins_to(symbol, api, wallet, private_key, balances):
    """
    Конвертируем все монеты в кошельке в монету symbol
    :param symbol: COINNAME (str)
    :param api:
    :param wallet:
    :param private_key:
    :param balances:
    :return:
    """
    if not only_symbol(balances, symbol):

        if symbol in balances.keys():
            del (balances[symbol])

        i = len(balances)
        for coin in balances:

            if coin != symbol:
                nonce = api.get_nonce(wallet)
                tx = MinterSellAllCoinTx(coin_to_sell=coin, coin_to_buy=symbol, min_value_to_buy=0, nonce=nonce,
                                         gas_coin=coin)
                tx.sign(private_key=private_key)
                r = api.send_transaction(tx.signed_tx)
                print(f'\n{coin} успешно сконвертирован в {symbol}.\n\nSend TX response:\n{r}')

                i -= 1
                if i > 0:
                    print('Waiting for nonce')
                    wait_for_nonce(api, wallet, nonce)


def write_taxes_and_return_remains(bip_total, payouts):
    """Вносим значение налогов в словарь и возвращаем остаток для дальнейшего распределения"""
    payouts['taxes']['value'] = bip_total * payouts['taxes']['percent']
    return bip_total - payouts['taxes']['value']


def write_founders_values(to_be_payed, payouts):
    """Вносим значения выплат для каждого основателя"""
    for _, f_dict in payouts['founders'].items():
        f_dict['value'] = to_be_payed * f_dict['percent']


# Генерация и отправка Multisend транзакции
def multisend(api, private_key,  wallet, txs, gas_coin='BIP', payload=''):
    nonce = api.get_nonce(wallet)
    tx = MinterMultiSendCoinTx(txs, nonce=nonce, gas_coin=gas_coin, payload=payload)
    tx.sign(private_key=private_key)
    r = api.send_transaction(tx.signed_tx)

    print(f'Multisend успешно отправлен.\n\nSend TX response:\n{r}')
    return tx