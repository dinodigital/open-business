# ОСНОВНЫЕ НАСТРОЙКИ
# ------------------------------------------------------------
wallet = 'Mx20e826a362eb061306ccb0e23d7ab3f18503d344'
min_bip = 5
payload = 'Автоматическая выплата'
MNEMONIC = ''
STOP_LIST = ['']
MIN_COINS_DELEGATED = 1

paying_taxes = False
paying_delegators = False

payouts = {
    'delegators': {
        'percent': 0.1
    },
    'founders': {
        'gorbunov': {
            'wallet': 'Mx5cef09065d68561ad9f61a905c7d0aa230117733',
            'percent': 0.85
        },
        'isheldon': {
            'wallet': 'Mxd315211a50c65e036c14117f6949f2ac91bb6170',
            'percent': 0.15
        }
    },
    'taxes': {
        'wallet': 'Mx50d9e92706ce51341c5f8f0c57afe1950a3ea922',
        'percent': 0.1
    }
}

# API URLs
# ------------------------------------------------------------
NODE_API_URL = 'http://api.minter.one'
EXPLORER_API_URL = 'https://explorer-api.minter.network/'
EXPLORER_API_ADDRESS = 'https://explorer-api.minter.network/api/v1/addresses/'

# ПРОЧИЕ НАСТРОЙКИ
# ------------------------------------------------------------
TIMEOUTS = {'read_timeout': 6, 'connect_timeout': 7}

