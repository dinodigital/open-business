from settings import payouts, PAYING_TAXES, PAYING_DELEGATORS
from val import get_all_payed_delegators

total_txs = 0

total_txs += len(payouts['founders'])

if PAYING_TAXES:
    total_txs += len(payouts['taxes'])

if PAYING_DELEGATORS:
    all_payed_delegators = get_all_payed_delegators()
    total_txs += len(all_payed_delegators)

print(total_txs)