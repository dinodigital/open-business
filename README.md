## Open Business SDK
Автоматизируйте переводы, распределение доходов, выплаты делегаторам и конвертацию токенов.

### Установка
1. Склонируйте репозиторий `git clone https://github.com/dinodigital/Open_business.git` в папку проекта
2. (необязательно) Укажите url api-ноды в `sdk/settings.py` и headers, если нода приватная

### Использование
```python
from sdk.wallet import Wallet

wallet = Wallet(seed='income junk erase gesture announce brisk catch wolf helmet custom elder rug')  # Пример seed фразы
```

#### Методы
* `wallet.pay(payouts, coin="BIP", payload='', include_commission=True)` - Переводит монеты на кошелек/кошельки
  * `payouts` (dict) - словарь вида `{'Mx...1': 100, 'Mx...2': 150, ...}` с указанием кому сколько переводить. Может быть любой длинны (от 1 до тысяч значений)
  * `coin` (str) - токен, в котором будет производится выплата
  * `payload` (str) - комментарий к транзакции
  * `include_commission` (bool) - Если True, то комиссия за транзакцию включается в общую сумму выплаты. При этом суммы каждого получателя будут пересчитаны с учетом комиссии.

- `wallet.pay_by_shares(shares, to_be_payed, coin="BIP", payload='', include_commission=True)`
- `wallet.pay_token_delegators()`
- `wallet.convert()`
- `wallet.convert_all_coins_to()`
- `wallet.get_balance()`
- `wallet.get_bip_balance()` 