from decimal import Decimal

from mintersdk.sdk.wallet import MinterWallet


def generate_multisend_list(length, value, coin="BIP"):
    m_list = []
    for i in range(length):
        m_list.append({'coin': coin, 'to': MinterWallet.create()['address'], 'value': Decimal(str(value))})

    return m_list


def generate_multisend_dict(length, value):
    m_dict = {}
    for i in range(length):
        m_dict[MinterWallet.create()['address']] = Decimal(str(value))

    return m_dict

