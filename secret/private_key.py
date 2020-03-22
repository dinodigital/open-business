"""
Вытаскиваем private key из seed фразы
"""

from mintersdk.sdk.wallet import MinterWallet


def seed():
    with open('secret/seed.txt', 'r') as f:
        return f.read()


w = MinterWallet.create(mnemonic=seed())
private_key = w['private_key']


def make_private_key(seed):
    return MinterWallet.create(mnemonic=seed)['private_key']
