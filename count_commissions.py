from settings import payouts, paying_taxes, paying_delegators
from val import get_all_payed_delegators

total_txs = 0

total_txs += len(payouts['founders'])

if paying_taxes:
    total_txs += len(payouts['taxes'])

if paying_delegators:
    all_payed_delegators = get_all_payed_delegators()
    total_txs += len(all_payed_delegators)

print(total_txs)