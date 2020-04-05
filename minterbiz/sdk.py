import time
from decimal import Decimal
from pprint import pprint

from mintersdk.minterapi import MinterAPI
from mintersdk.sdk.transactions import MinterSellCoinTx, MinterSellAllCoinTx, MinterSendCoinTx, MinterMultiSendCoinTx
from mintersdk.sdk.wallet import MinterWallet
from mintersdk.shortcuts import to_bip

from minterbiz.settings import default_API


class Wallet:

    def __init__(self, seed, pk=None, node=None):
        self.seed = seed
        self.private_key = pk or MinterWallet.create(mnemonic=seed)['private_key']
        self.address = MinterWallet.create(mnemonic=seed)['address']
        self.node = node
        self.API = MinterAPI(node['url'], headers=node['headers'], **node['timeouts']) if node else default_API

    # ------------------------------------------
    # ОСНОВНЫЕ ФУНКЦИИ
    # ------------------------------------------

    def get_balance(self, in_bip=True):
        """
        Получаем баланс кошелька
        """
        return self.API.get_balance(self.address, pip2bip=in_bip)['result']['balance']

    def get_bip_balance(self):
        """
        Получаем баланс кошелька в BIP
        """
        return self.API.get_balance(self.address, pip2bip=True)['result']['balance']['BIP']

    def convert(self, value, from_symbol, to_symbol, gas_coin=None):
        """
        Конвертирует одну монету в другую
        :param gas_coin: str 'SYMBOL' - монета для оплаты комиссии
        :param value: int/float
        :param from_symbol: str (Тикер монеты)
        :param to_symbol: str (Тикер монеты)
        :return:
        """

        from_symbol = from_symbol.upper()
        to_symbol = to_symbol.upper()
        value = Decimal(str(value))
        if gas_coin is None:
            gas_coin = from_symbol

        balances = self.get_balance(in_bip=True)

        if balances[from_symbol] < value:
            print(f"На кошельке недостаточно {from_symbol}. Нужно {value}, а есть {balances[from_symbol]}")
            return

        # Генерируем транзакцию
        nonce = self.API.get_nonce(self.address)
        tx = MinterSellCoinTx(
            coin_to_sell=from_symbol,
            value_to_sell=value,
            coin_to_buy=to_symbol,
            min_value_to_buy=0,
            nonce=nonce,
            gas_coin=gas_coin
        )

        # Проверяем достаточно ли баланса на оплату комиссии
        commission = to_bip(tx.get_fee())
        if gas_coin == from_symbol and balances[from_symbol] < (value + commission):
            print(f"На кошельке недостаточно {from_symbol} для оплаты комиссии {commission}\n"
                  f"Баланс: {round(balances[from_symbol], 2)}\n"
                  f"Нужно:  {value + commission} (+{value + commission - round(balances[from_symbol], 2)})")
            return
        elif balances[gas_coin] < commission:
            print(f"На кошельке недостаточно {gas_coin} для оплаты комиссии {commission}\n"
                  f"Баланс: {round(balances[gas_coin], 2)}\n"
                  f"Нужно:  {commission}")
            return

        # Отправляем транзакицю
        tx.sign(private_key=self.private_key)
        r = self.API.send_transaction(tx.signed_tx)

        try:
            if r['result']['code'] == 0:
                print(f'{from_symbol} сконвертирован в {to_symbol}')
                self._wait_for_nonce(nonce)  # Ждем nonce, чтобы предотвратить отправку нескольких транзакций в блоке
        except Exception:
            print(f'Не удалось сконвертировать {from_symbol} в {to_symbol}\nServer response: {r}')

        return r

    def convert_all_coins_to(self, symbol, gas_coin=None):
        """
        Конвертирует все монеты на кошельке в symbol
        """
        symbol = symbol.upper()
        balances = self.get_balance()
        if gas_coin is None:
            gas_coin = symbol

        if self._only_symbol(balances, symbol):
            return

        for coin in balances:
            if coin == symbol:
                continue

            nonce = self.API.get_nonce(self.address)
            tx = MinterSellAllCoinTx(
                coin_to_sell=coin, coin_to_buy=symbol, min_value_to_buy=0, nonce=nonce, gas_coin=gas_coin
            )
            tx.sign(private_key=self.private_key)
            r = self.API.send_transaction(tx.signed_tx)

            try:
                if r['result']['code'] == 0:
                    print(f'{coin} сконвертирован в {symbol}')
                    self._wait_for_nonce(nonce)  # Ждем nonce, чтобы предотвратить отправку нескольких транзакций в блоке
            except Exception:
                print(f'Не удалось сконвертировать {coin} в {symbol}\nServer response: {r}')

            return r

    def pay(self, payouts, coin="BIP", payload='', include_commission=True):
        """
        Выплата на любое количество адресов
        :param payouts: dict > {'Mp...1: 100', 'Mp...2': 50, ...} - словарь кошелек: сумма
        :param coin: str > 'SYMBOL' - Монета, в которой будет производится выплата
        :param payload: str - комментарий к транзакции
        :param include_commission: bool - Если True, то комиссия за перевод включается в сумму выплаты и выплаты будут пересчитаны с учетом комиссии
        :return: json - ответ от ноды
        """
        return self.multisend(payouts, coin=coin, payload=payload, include_commission=include_commission)

    def pay_token_delegators(self, delegated_token, to_be_payed, by_node='', min_delegated=0, stop_list=None,
                             coin='BIP', payload='', include_commission=True):
        """
        Выплата делегаторам конкретного токена
        :param delegated_token: str > 'SYMBOL' - делгаторы этого токена получают выплату
        :param to_be_payed: int/float - сумма, которая будет выплачена всем делегаторам
        :param by_node: str > 'Mp....' - публичный адрес валидатора . Если заполнить, то выплата будет только делегатором конкретной ноды
        :param min_delegated: int/float - столько минимум должно быть делегировано, чтобы получить выплату
        :param stop_list: list > ['Mx...1', 'Mx...2', ...] кошельки, не участвующие в выплате
        :param coin: str > 'SYMBOL' - монета, в которой будет производится выплата
        :param payload: str - комментарий к транзакции
        :param include_commission: bool - Если True, то комиссия за перевод включается в сумму выплаты и выплаты будут пересчитаны с учетом комиссии
        :return:
        """
        delegators = Delegators(delegated_token, node=self.node)
        payouts = delegators.get_payouts(to_be_payed, by_node=by_node, min_delegated=min_delegated, stop_list=stop_list)
        return self.multisend(payouts, coin=coin, payload=payload, include_commission=include_commission)

    def pay_by_shares(self, shares, to_be_payed, coin="BIP", payload='', include_commission=True):
        """
        Выплаты по пропорциям
        :param shares: dict
        :param to_be_payed: int/float сумма выплаты
        :param coin: str 'SYMBOL'
        :param payload: str
        :param include_commission: bool
        :return: node response
        """
        payouts = self._convert_shares_to_payouts(shares, to_be_payed)
        return self.multisend(payouts, coin=coin, payload=payload, include_commission=include_commission)

    def send(self, to, value, coin="BIP", payload='', include_commission=True):
        value = Decimal(str(value))

        nonce = self.API.get_nonce(self.address)
        tx = MinterSendCoinTx(coin=coin, to=to, value=value, nonce=nonce, gas_coin=coin, payload=payload)

        if include_commission:
            if coin == 'BIP':
                commission = to_bip(tx.get_fee())
            else:
                tx.sign(self.private_key)
                commission = self.API.estimate_tx_commission(tx.signed_tx, pip2bip=True)['result']['commission']

            tx.value = value - commission

        # Проверяем на ошибки
        if tx.value <= 0:
            print(f'Ошибка: Комиссия ({to_bip(tx.get_fee())}) превышает сумму выплаты ({value})')
            return
        elif tx.value > self.get_balance(in_bip=True)[coin]:
            print(f'Ошибка: На кошельке недостаточно {coin}')
            return

        tx.sign(private_key=self.private_key)

        r = self.API.send_transaction(tx.signed_tx)

        try:
            if r['result']['code'] == 0:
                print(f'{value} {coin} успешно отпрвлены на адрес {to}')
                self._wait_for_nonce(nonce)  # Ждем nonce, чтобы предотвратить отправку нескольких транзакций в блоке
        except Exception:
            print(f'Не удалось отправить {coin}\nServer response: {r}')

        return r

    def multisend(self, to_dict, coin="BIP", payload='', include_commission=True):
        """
        Multisend на любое количество адресов

        :param to_dict: dict {address: value, ...}
        :param coin: str 'SYMBOL'
        :param payload: str 'Комментарий к транзакции'
        :param include_commission: bool Платит с учетом комиссии
        :return:
        """

        # Генерация общего списка транзакций и расчет общей суммы выплаты
        all_txs = []
        total_value = 0
        for d_address, d_value in to_dict.items():
            d_value = Decimal(str(d_value))
            all_txs.append({'coin': coin, 'to': d_address, 'value': d_value})
            total_value += d_value

        # Проверяем хватит ли баланса для совершения транзакции
        balance = self.get_balance(in_bip=True)[coin]
        if total_value > balance:
            print(f'Ошибка: На кошельке недостаточно {coin}. Нужно {total_value}, а у нас {balance}')
            return

        # Разбивка на списки по 100 транзакций
        all_txs = self._split_txs(all_txs)

        # Генерируем шаблоны транзакций
        tx_templates = [MinterMultiSendCoinTx(txs, nonce=1, gas_coin=coin, payload=payload) for txs in all_txs]

        # Считаем общую комиссию за все транзакции
        if coin == 'BIP':
            total_commission = to_bip(sum(tx.get_fee() for tx in tx_templates))
        else:
            [tx.sign(self.private_key) for tx in tx_templates]
            total_commission = sum(
                self.API.estimate_tx_commission(tx.signed_tx, pip2bip=True)['result']['commission'] for tx in
                tx_templates)

        # Если перевод с учетом комиссии, то пересчитываем выплаты
        if include_commission:
            new_total_value = total_value - total_commission
            if new_total_value <= 0:
                print(f'Ошибка: Комиссия ({total_commission}) превышает сумму выплаты ({total_value})')
                return

            for tx in tx_templates:
                for tx_dict in tx.txs:
                    tx_dict['value'] = new_total_value * Decimal(str(tx_dict['value'])) / Decimal(str(total_value))
        else:
            total_value -= total_commission
            if total_value <= 0:
                print(f'Ошибка: Комиссия ({total_commission}) превышает сумму выплаты ({total_value})')
                return

        r_out = []
        # Делаем multisend
        for tx in tx_templates:
            tx.nonce = self.API.get_nonce(self.address)
            tx.sign(self.private_key)
            r = self.API.send_transaction(tx.signed_tx)

            try:
                if r['result']['code'] == 0:
                    print(f'Multisend для {len(tx.txs)} получателей успешно отправлен')
                    self._wait_for_nonce(tx.nonce)  # Ждем nonce, чтобы предотвратить отправку нескольких транзакций в блоке

            except Exception:
                print(f'Не удалось отправить multisend\nServer response: {r}')

            r_out.append(r)

        return r_out

    # ------------------------------------------
    # СЛУЖЕБНЫЕ ФУНКЦИИ
    # ------------------------------------------

    @staticmethod
    def _convert_shares_to_payouts(shares, to_be_payed):

        for key in shares:
            shares[key] = Decimal(str(shares[key])) * Decimal(str(to_be_payed))

        return shares

    @staticmethod
    def _split_txs(txs, length=100):
        """
        Делает несколько multisend списков по length транзакций на список
        """
        if length > 100:
            print('[!] Ошибка в Wallet._split_txs: Максимум 100 адресов на 1 multisend транзакцию')
            return

        txs_list = []

        while len(txs) > length:
            txs_list.append(txs[:length])
            txs = txs[length:]
        else:
            txs_list.append(txs)

        return txs_list

    def _wait_for_nonce(self, old_nonce):
        """
        Прерывается, если новый nonce != старый nonce
        """
        while True:
            nonce = self.API.get_nonce(self.address)
            if nonce != old_nonce:
                break

            time.sleep(1)

    @staticmethod
    def _only_symbol(balances, symbol):
        """
        True, если на балансе кошелька только symbol
        """
        if len(balances) > 1:
            return False
        elif symbol in balances:
            return True


class Delegators:

    def __init__(self, token=None, min_delegated=0, stop_list=None, node=None):
        self.token = token
        self.min_delegated = min_delegated
        self.stop_list = stop_list or []
        self.API = MinterAPI(node['url'], headers=node['headers'], **node['timeouts']) if node else default_API

    def get_delegations(self, by_node='', min_delegated=0, stop_list=None):
        """
        Получаем всех делегаторов монеты self.token
        :param stop_list: list ['Mx...1', 'Mx...2', ...]
        :param by_node: str 'Mp....'
        :param min_delegated: float/int Минимальное количество делегированных токенов
        :return: dict {address: delegated_tokens, ...}
        """

        stop_list = stop_list or [] or self.stop_list
        min_delegated = min_delegated or self.min_delegated

        # Получаем стейки
        stakes = []

        # По отдельной ноде
        if by_node:
            stakes = self.API.get_candidate(by_node)['result']['stakes']
        # По всем нодам
        else:
            validators = self.API.get_validators(limit=256)['result']
            pub_keys = [v['pub_key'] for v in validators]
            print(f"Получаем стейки валидаторов")
            for i, pub_key in enumerate(pub_keys, 1):
                print(f"{i} / {len(validators)}")
                stakes += self.API.get_candidate(pub_key)['result']['stakes']

        # Получаем словарь со всеми делегаторами и суммарное количество заделегированных токенов
        delegators = {}
        for stake in stakes:
            if (stake['coin'] == self.token or self.token is None) and stake['owner'] not in stop_list:
                if stake['owner'] not in delegators.keys():
                    delegators[stake['owner']] = to_bip(stake['value'])
                else:
                    delegators[stake['owner']] += to_bip(stake['value'])

        # Фильтруем делегаторов по минимальной сумме
        if min_delegated > 0:
            delegators = {k: v for k, v in delegators.items() if v >= min_delegated}

        return delegators

    def get_payouts(self, bip_total, by_node="", min_delegated=0, stop_list=None):
        """
        Создает словарь адрес - выплата
        :param stop_list: list ['Mx...1', 'Mx...2', ...]
        :param bip_total: float/int
        :param by_node: str 'Mp....'
        :param min_delegated: float/int Минимальное количество делегированных токенов
        :return: dict {address: bip_value, ...}
        """
        stop_list = stop_list or [] or self.stop_list
        min_delegated = min_delegated or self.min_delegated

        delegators = self.get_delegations(by_node=by_node, min_delegated=min_delegated, stop_list=stop_list)

        # Получаем сумму выплаты в BIP для каждого делегатора
        tokens_sum = Decimal(str(sum(delegators.values())))
        for key in delegators:
            delegators[key] = round(Decimal(str(bip_total)) * Decimal(str(delegators[key])) / Decimal(str(tokens_sum)), 18)

        return delegators
