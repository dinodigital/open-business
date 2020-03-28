## Open Business SDK
Автоматизируйте переводы, распределение доходов, выплаты делегаторам и конвертацию токенов.

## Установка
1. Склонируйте репозиторий `git clone https://github.com/dinodigital/Open_business.git` в папку проекта
2. (необязательно) Укажите url api-ноды в `sdk/settings.py` и headers, если нода приватная

## Инициализация
```python
from sdk.wallet import Wallet

wallet = Wallet(seed='income junk erase gesture announce brisk catch wolf helmet custom elder rug')  # Пример seed фразы
```

## Использование
#### Перевести монеты на 1 или несколько кошельков
```python
wallet.pay(payouts, coin="BIP", payload='', include_commission=True)

# payouts (dict) - словарь вида `{'Mx...1': 100, 'Mx...2': 150, ...}` с указанием кому сколько монет переводить. Может быть любой длинны, начиная с 1.
# coin (str) - токен, в котором будет производится выплата
# payload (str) - комментарий к транзакции
# include_commission (bool) - Если True, то комиссия за транзакцию включается в общую сумму выплаты. При этом суммы каждого получателя будут пересчитаны с учетом комиссии.
```

#### Перевести сумму в соответствии с долями
```python
wallet.pay_by_shares(shares, to_be_payed, coin="BIP", payload='', include_commission=True)

# shares (dict) - словарь вида `{'Mx...1': 0.1, 'Mx...2': 0.5, ...}`, где 0.1, 0.5 это проценты от общей суммы (10%, 50% соответственно)
# to_be_payed (int/float) - обшая сумма выплаты
# coin (str) - токен, в котором будет производится выплата
# payload (str) - комментарий к транзакции
# include_commission (bool) - Если True, то комиссия за транзакцию включается в общую сумму выплаты. При этом суммы каждого получателя будут пересчитаны с учетом комиссии.
```

- `wallet.pay_token_delegators()`
- `wallet.convert()`
- `wallet.convert_all_coins_to()`
- `wallet.get_balance()`
- `wallet.get_bip_balance()` 