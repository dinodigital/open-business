from decimal import Decimal

from mintersdk.shortcuts import to_bip

from sdk.settings import API


class Delegators:

    def __init__(self, token=None, min_delegated=0, stop_list=None):
        self.token = token
        self.min_delegated = min_delegated
        self.stop_list = stop_list or []

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
            stakes = API.get_candidate(by_node)['result']['stakes']
        # По всем нодам
        else:
            validators = API.get_validators(limit=256)['result']
            pub_keys = [v['pub_key'] for v in validators]
            print(f"Получаем стейки валидаторов")
            for i, pub_key in enumerate(pub_keys, 1):
                print(f"{i} / {len(validators)}")
                stakes += API.get_candidate(pub_key)['result']['stakes']

        # Получаем словарь со всеми делегаторами и суммарное количество заделегированных токенов
        delegators = {}
        for stake in stakes:
            if (stake['coin'] == self.token or self.token == None) and stake['owner'] not in stop_list and stake['value'] >= min_delegated:
                if stake['owner'] not in delegators.keys():
                    delegators[stake['owner']] = to_bip(stake['value'])
                else:
                    delegators[stake['owner']] += to_bip(stake['value'])

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
        tokens_sum = sum(delegators.values())
        for key in delegators:
            delegators[key] = bip_total * Decimal(str(delegators[key])) / Decimal(str(tokens_sum))

        return delegators
