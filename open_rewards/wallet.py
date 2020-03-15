import settings
from mintersdk.sdk.wallet import MinterWallet

wallet_from = MinterWallet.create(mnemonic=settings.MNEMONIC)
