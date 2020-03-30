from mintersdk.minterapi import MinterAPI

default_node = {
    'url': 'https://mnt.funfasy.dev/',
    'timeouts': {'read_timeout': 6, 'connect_timeout': 7},
    'headers': {}
}

default_API = MinterAPI(default_node['url'], headers=default_node['headers'], **default_node['timeouts'])
