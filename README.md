## Minter Business SDK
Автоматизируйте переводы, распределяйте доходы, платите делегаторам и конвертируйте токены, не забивая голову механизмами работы блокчейна. Оно просто работает.

## Установка
1. Склонируйте репозиторий `git clone https://github.com/dinodigital/Open_business.git` в папку проекта
2. (необязательно) Укажите url api-ноды в `sdk/settings.py` и headers, если нода приватная

## Пример использования
```python
from minterbiz.sdk import Wallet

# Инициализируем кошелек
my_wallet = Wallet(seed="12 слов вашей seed фразы")

# Кому сколько платим
payouts = {
    'Mx5cef09065d68561ad9f61a905c7d0aa230117733': 100,  # сюда 100 монет
    'Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5': 150   # сюда 150 монет
}

# Переводим BIP
my_wallet.pay(payouts)

# Переводим кастомные монеты с комментарием
my_wallet.pay(payouts, coin='MYTOKEN', payload='Автоматическая выплата тем, кто в меня верит')
```

## Использование
#### Перевод на 1 или несколько кошельков
```python
wallet.pay(payouts, coin="BIP", payload='', include_commission=True)

# payouts (dict) - словарь вида `{'Mx...1': 100, 'Mx...2': 150, ...}` с указанием кому сколько монет переводить. Может быть любой длинны, начиная с 1.
# coin (str) - токен, в котором будет производится выплата
# payload (str) - комментарий к транзакции
# include_commission (bool) - Если True, то комиссия за транзакцию включается в общую сумму выплаты. При этом суммы каждого получателя будут пересчитаны с учетом комиссии.
```

#### Перевод суммы в соответствии с долями
```python
wallet.pay_by_shares(shares, to_be_payed, coin="BIP", payload='', include_commission=True)

# shares (dict) - словарь вида `{'Mx...1': 0.1, 'Mx...2': 0.5, ...}`, где 0.1, 0.5 это проценты от общей суммы (10%, 50% соответственно)
# to_be_payed (int/float) - обшая сумма выплаты
# coin (str) - токен, в котором будет производится выплата
# payload (str) - комментарий к транзакции
# include_commission (bool) - Если True, то комиссия за транзакцию включается в общую сумму выплаты. При этом суммы каждого получателя будут пересчитаны с учетом комиссии.
```

#### Перевод суммы делегаторам конкретного токена
```python
wallet.pay_token_delegators(delegated_token, to_be_payed, by_node='', min_delegated=0, stop_list=None, coin='BIP', payload='', include_commission=True)

# delegated_token (str 'SYMBOL') - делегаторы данного токена получат выплату
# to_be_payed (int/float) - обшая сумма выплаты
# by_node (str 'Mp...') - если заполнить, то выплату получат делегаторы токена (delegated_token) в конкретной ноде
# min_delegated (int/float) - столько должно быть суммарно делегировано у кошелька, чтобы полчить выплату. Если равно 0, то выплату получат все делегаторы токена.
# stop_list (list ['Mx...1', ...] - эти кошельки не получат выплату по токену
# coin (str) - токен, в котором будет производится выплата
# payload (str) - комментарий к транзакции
# include_commission (bool) - Если True, то комиссия за транзакцию включается в общую сумму выплаты. При этом суммы каждого получателя будут пересчитаны с учетом комиссии.
```

#### Конвертировать одну монету в другую
```python
wallet.convert(value, from_symbol, to_symbol)

# value (int/float) - столько монет (from_symbol) будет сконвертировано
# from_symbol (str 'SYMBOL') - монета, которую продаем
# to_symbol (str 'SYMBOL') - монета, которую покупаем
```

#### Конвертировать весь баланс кошелька в определенную монету
```python
wallet.convert_all_coins_to(symbol)

# symbol (str 'SYMBOL') - монета, в которую конвертируем все остальные
```

#### Получить балансы всех монет на кошельке
```python
wallet.get_balance()

# Возвращает json с балансами
# Получить баланс конкретной монеты > wallet.get_balance()['SYMBOL']
```

#### Получить баланс BIP на кошельке
```python
wallet.get_bip_balance()

# Возвращает количество BIP на кошельке
```

## Примеры

### Работа с другой нодой
```python
from minterbiz.sdk import Wallet

# Основные параметры ноды
node = {
    'url': 'http://адрес ноды',
    'headers': {'Project-Id': '...', 'Project-Secret': '...'},
    'timeouts': {'read_timeout': 6, 'connect_timeout': 7}
}

# Инициализация кошелька с другой нодой
wallet = Wallet(seed='12 слов seed фразы', node=node)
```