URLS = {
    'syncswap': 'https://syncswap.xyz/swap',
    'mute': 'https://app.mute.io/swap',
    'space': 'https://swap-zksync.spacefi.io/#/swap',
    'pancake': 'https://pancakeswap.finance/swap?chain=zkSync',
    'mav': 'https://app.mav.xyz/?chain=324',
    'syncswap_liquid': 'https://syncswap.xyz/pools',
    'mute_liquid': 'https://app.mute.io/pool',
    'zkbridge': 'https://portal.zksync.io/bridge/withdraw',
    'zkns': 'https://zns.is/',
    'orbiter': 'https://www.orbiter.finance/?source=zkSync%20Era&dest=Arbitrum',
    'eralend': 'https://app.eralend.com/',
    'zkswap': 'https://app.zk-swap.xyz/swap'
}

INFO = {
    'syncswap':
        {
            0: 56890,
            'now_selected_token': ['ETH', 'USDC'],
        },
    'mute': {
        0: 56891,
    },
    'space': {
        0: 56892,
        'now_selected_token': ['ETH', '']
    },
    'pancake': {
        0: 56893,
        'now_selected_token': ['ETH', 'CAKE']
    },
    'mav': {
        0: 56894,
    }
    }

TRADER_PORT = 57001
HOST = '127.0.0.1'
TEST = True

MUTE_CONFIGS = {
    'btn': ('//*[@id="app"]/main/div/div/div[2]/div[2]/div[1]/div[1]/button', '//*[@id="app"]/main/div/div/div[2]/div[2]/div[3]/div[1]/button'),  # тут Xpath кнопок с выбором монет
    'search': '/html/body/div[2]/div[2]/input',  # тута Xpath поиска
    'token_container': 'div.MuiModal-root.css-8ndowl div:nth-child(3)div.sc-dtDOqo.GCznx.sc-cLpAjG.ewkckn ul li',
    # Css selector элемента в котором все токены (до пробела)
    'token1_input': '//*[@id="app"]/main/div/div/div[2]/div[2]/div[1]/div[1]/div[1]/input',  # xpath для первого input
    'swap_btn': '//*[@id="app"]/main/div/div/div[2]/button',  # xpath кнопки свапа
    'approve_btn': '//*[@id="app"]/main/div/div/div[2]/button',  # тут выбор кнопки с approve
    'approve_starswith': 'Approve',  # текст начала апрува
    'min_price': '//*[@id="app"]/main/div/div/div[2]/ul/li[3]/p'
}

SYNCSWAP_CONFIGS = {
    'btn': ('//*[@id="swap-input"]/div[1]/button', '//*[@id="swap-box"]/div[1]/div/div/div[2]/div[3]/div[1]/button'),
    # тут Xpath кнопок с выбором монет
    'search': '//*[@id="toolbox"]/div/div[2]/div[1]/div/input',  # тута Xpath поиска
    'token_container': '.fade-in-mid.token-selector-currencies.col',
    # Css selector элемента в котором все токены (до пробела)
    'token1_input': '//*[@id="swap-input"]/div[1]/input',  # xpath для первого input
    'swap_btn': '//*[@id="swap-box"]/div[1]/div/button',  # xpath кнопки свапа
    'approve_btn': '//*[@id="swap-box"]/div[1]/div/div[3]/button',  # тут выбор кнопки с approve
    'approve_starswith': 'Unlock',  # текст начала апрува
    'min_price': '//*[@id="swap-box"]/div[1]/div/div[2]/div/div[1]/div/div[2]/div[1]/p',
    'min_price_open': '//*[@id="swap-box"]/div[1]/div/div[2]/button'
}

SPACEFI_CONFIGS = {
    'btn': ('//*[@id="swap-currency-input"]/div/div[2]/button[2]', '//*[@id="swap-currency-output"]/div/div[2]/button'),
    # тут Xpath кнопок с выбором монет
    'search': '//*[@id="token-search-input"]',  # тута Xpath поиска
    'token_container': '/html/body/reach-portal[1]/div[3]/div/div/div/div/div[3]/div[1]/div/div/div[1]',
    # Css selector элемента в котором все токены (до пробела)
    'token1_input': '//*[@id="swap-currency-input"]/div/div[2]/input',  # xpath для первого input
    'swap_btn': '//*[@id="swap-button"]',  # xpath кнопки свапа
    'approve_btn': '//*[@id="swap-page"]/div[2]/div[1]/button[1]',  # тут выбор кнопки с approve
    'min_price': '//*[@id="root"]/div/div[2]/div[4]/div/div[1]/div[1]/div[2]/div',
}

PANCAKE_CONFIGS = {
    'btn': ('//*[@id="swap-currency-input"]/div[1]/div[1]/button/div', '//*[@id="swap-currency-output"]/div[1]/div[1]/button/div'),
    # тут Xpath кнопок с выбором монет
    'search': '//*[@id="token-search-input"]',  # тута Xpath поиска
    'token_container': '//*[@id="portal-root"]/div/div/div[2]/div[2]/div[2]/div/div/div',
    # Css selector элемента в котором все токены (до пробела)
    'token1_input': '//*[@id="swap-currency-input"]/div[2]/label/div[1]/input',  # xpath для первого input
    'swap_btn': '//*[@id="swap-button"]',  # xpath кнопки свапа
    'approve_btn': '//*[@id="swap-page"]/div/div[5]/div[1]/button[1]',  # тут выбор кнопки с approve
    'min_price': '//*[@id="__next"]/div[1]/div[3]/div/div/div[1]/div/div/div/div/div/div[3]/div/div[1]/div[1]/div[2]/div',
}

MAV_CONFIGS = {
    'btn': ('/html/body/div/div/div/div/div/div[1]/div[2]/div/div/div[1]/div[1]/div[1]/button', '/html/body/div/div/div/div/div/div[1]/div[2]/div/div/div[3]/div/div/button'),
    # тут Xpath кнопок с выбором монет
    'search': '//*[@id="customized-hook-demo"]',  # тута Xpath поиска
    'token_container': '//*[@id="customized-hook-demo-listbox"]',
    # Css selector элемента в котором все токены (до пробела)
    'token1_input': '//*[@id="mui-2"]',  # xpath для первого input
    'swap_btn': '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button',  # xpath кнопки свапа
    'approve_btn': '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button',  # тут выбор кнопки с approve
    'min_price': '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/div[2]/p[2]',
}

ALLOW_NET = {
    'zksync': {
        'url': 'https://chainlist.org/?search=zksy',
        'xpath': '//*[@id="__next"]/div/div[2]/div[2]/div/button[1]'
    },
    'zkevm': {
        'url': 'https://chainlist.org/?search=zkevm',
        'xpath': '//*[@id="__next"]/div/div[2]/div[2]/div[1]/button[1]',
    },
    'linea': {
        'url': 'https://chainlist.org/?search=linea',
        'xpath': '//*[@id="__next"]/div/div[2]/div[2]/div/button[1]'
    }
}
