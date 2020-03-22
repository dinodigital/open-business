На доходный кошелек поступает прибыль от проектов. Скрипт автоматически распределяет монеты между Основателями, Делегаторами, Налоговой или всеми вместе в зависимости от настроек `settings.py`

## Как пользоватьс скриптом
1. Создать в папке `secret` файл `seed.txt`, в котором 12 слов seed фразы кошелька
2. Настроить скрипт в `settings.py`
3. Запустить `main.py`


## Settings.py

#### Основные настройки скрипта
- `PAYLOAD = 'Текст транзакции'`
  Транзакция придет с этим текстом. Можно оставить пустым, тогда комиссия за транзакцию будет меньше. 1 символ описания ~ +0.1 BIP к комиссии.

- `PAYING_TAXES = False`
  Платим ли налоги. Если True, отправляет % от баланса кошелька на отдельный кошелек для налогов. (На будущее). В этом случае все остальные получают выплаты за вычетом налогов.

- `PAYING_DELEGATORS = True`
  Платим ли делегаторам токена. Если True, то пропорционально распределает делегаторам % от баланса кошелька (см. настройки выплат). В этом случае основатели получают выплаты за вычетом % делегаторов.

- `PAYING_FOUNDERS = True`
  Платим ли фаундерам проекта. Если True, то скрипт распределяет награды согласно пропорциям фаундеров (см. настройки выплат)


#### Настройки выплат
##### Налоги
```python
TAXES = {
    'wallet': 'Mx5cef09065d68561ad9f61a905c7d0aa230117733',
    'percent': 0.1
}
```
- `wallet` - кошелек для оплаты налогов
- `percent` - % налогов

##### Основатели
```python
FOUNDERS = {
        'gorbunov': {
            'wallet': 'Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5',
            'percent': 0.85},
        'isheldon': {
            'wallet': 'Mx1d2111ef33c0735ae6d97a8a7948a43cca3a4bd1',
            'percent': 0.15}
}
```
- `gorbunov` - название кошелька
- `wallet` - адрес кошелька
- `percent` - процент конкретного основателя (на всех основателей должно в сумме быть 1, то есть 100%)

##### Делегаторы
- `DELEGATORS_PERCENT = 0.1`
  Процент, который выплачивается делегаторам токена

- `DELEGATED_TOKEN = 'SYMBOL'`
  Токен, который нужно делегировать, чтобы получать процент, указанный выше

- `MIN_COINS_DELEGATED = 1`
  Столько минимум токенов должно быть делегировано, чтобы получить выплату. Если поставить 0, то выплаты будут приходить всем делегаторам без исключения

- `STOP_LIST = [addresses]`
  Стоп-лист. На эти кошельки выплаты приходить *не будут*. Принимает на вход список адресов. Можно оставить пустым  или дать список с 1 адресом.

