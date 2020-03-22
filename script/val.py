"""
Скрипт который вытаскивает всех делегаторов, которым должна идти выплата по токену GORBUNOV
"""
from script import settings
from script.settings import API


def get_delegators_from_validator(validator, delegators):
    """
    Возвращает словарь {wallet: pip} по всем делегаторам ТОКЕНА одного конкретного валидатора
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


def get_delegators_dict(total_pip):
    """
    Получаем всех делегаторов и количество делегированных токенов на кошельке
    :return: dict: {wallet: value}
    """

    validators = API.get_candidates(include_stakes=True)['result']
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
