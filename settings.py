
# Данны ключа
okx_proxy = "http://ps72077:Yn1dip2a6x@45.8.126.148:8000" # можно не менять и оставить такое
apikey = ""
secretkey = ""
okx_passphrase = ''


# TODO количество аккаунтов, работающих одновременно (рекомендуется не более 2)
COUNT_ACCOUNTS = 1

# TODO будет ли виден монитор (если вы ставите более одного аккаунта одновременно, лучше выключить)
SCREEN = True

#TODO везде в дальнейшем, следует писать цифры более 0.0001

ENTER_MONEY = False     #пополняем ETH с биржи
VOLUME = 0.045           # объем средств выводимый на один аккаут (будет автоматом немного рандомизирован в меньшую сторону) (в ETH)

syncswap = False        # будет ли делать syncswap
syncswap_swap = [4, 4]  # количество транзакция случайное четное число между этими двумя
SYNCSWAP_LIQUIDUTY = False # добавит по минимум ликвидность на Syncswap

mute = False                # будет ли делать mute (для успешных свапов на mute желателен баланс более 0.15 ETH)
MUTE_LIQUIDUTY = False # добавит ликвидность на syncswap в пару ETH-USDC
MUTE_ADD_LIQUIDUTY = 0.001 # сколько ликвидности добавить в MUTE в ETH
MUTE_REMOVE_LIQUIDUTY = False
mute_swap = [2, 2] # количество транзакция случайное четное число между этими двумя

space = False
space_swap = [2, 2] # количество транзакция случайное четное число между этими двумя

pancake = False
pancake_swap = [2, 2] # количество транзакция случайное четное число между этими двумя

mav = False
mav_swap = [2, 2] # количество транзакция случайное четное число между этими двумя

zkswap = False
zkswap_count_swap = [2, 2]

eralend_supply = False
eralend_supply_amount = 0.001 # количество в ETH
eralend_withdraw = False
eralend_withdraw_amount = 0.001 # количество в ETH
eralend_count_supply = [2, 2]

BRIDGE = False # вывод в один конец в сеть эфира через официальный мост
bridge_count = 0.0001 # сколько выводить

DOMEN = False # покупка домена на сайте zns

CAKE_TOKEN = False # Покупка токена cake на сумму около (17 центов)

ZZ_TOKEN = False
count_zz = 0.001

IZI_TOKEN = False
count_izi = 0.001 # на сколько ETH купить токенов iZi

DVF_TOKEN = False
count_dvf = 0.001

SPACE_TOKEN = False # ликвидность очень мала, обмен может не пройти
count_SPACE = 0.001 # на сколько ETH купить токенов PVP

MAV_TOKEN = False
count_MAV = 0.001 # на сколько ETH купить токенов MAV

MAX_ETH_GAS_PRICE = 60 # софт будет ожидать пока цена на газ спустится ниже данной отметки

WITHDRAW_MONEY = False #Выводить ли оставшийся ETH в OKX
percentage = 80 # Сколько процентов оставшигося эфира выводить в OKX (не учитывая комиссию)

NFT = True
NFT_count = [1, 1]
NFT_LINKS = ['https://zksync_collection.nfts2.me/', 'https://zksyncnosybil.nfts2.me/', 'https://zksynckpass.nfts2.me/', 'https://zkevm_dropsss.nfts2.me/', 'https://zksync_airdropaas.nfts2.me/',  'https://cats-warriors.nfts2.me/', 'https://cats-teachers.nfts2.me/', 'https://cats-are-athletes.nfts2.me/', 'https://cats-are-bankers.nfts2.me/']

WORK_ANTIDETECT_MODE = False
account_num = 1

