import time
from settings import MAX_ETH_GAS_PRICE
from eth_account import Account
from eth_account.signers.local import LocalAccount
from zksync2.manage_contracts.erc20_contract import get_erc20_abi
from zksync2.module.module_builder import ZkSyncBuilder
from zksync2.transaction.transaction_builders import TxFunctionCall
from zksync2.core.types import ZkBlockParams, EthBlockParams
import logging.config
from logger_configs import LOGGING_CONFIG
from web3 import Web3

TOKENS = {
    'LUSD': ['0x503234F203fC7Eb888EEC8513210612a43Cf6115', 6],
    'USDC': ['0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', 6],
    'USDT': ['0x493257fD37EDB34451f62EDf8D2a0C418852bA4C', 6],
    'USD+': ['0x8E86e46278518EFc1C5CEd245cBA2C7e3ef11557', 6],
    'iZi':  ['0x16a9494e257703797d747540f01683952547ee5b', 18],
    'SPACE':  ['0x47260090ce5e83454d5f05a0abbb2c953835f777', 18],
    'MAV':  ['0x787c09494ec8bcb24dcaf8659e7d5d69979ee508', 18],
}

RPC = 'https://mainnet.era.zksync.io'
logging.config.dictConfig(LOGGING_CONFIG)
error_logger = logging.getLogger('error_logger')

def get_now_token_balance(open_key, token):
    while True:
        try:
            zk_web3 = ZkSyncBuilder.build(RPC)
            account2_address = zk_web3.to_checksum_address(open_key)
            token_contact = zk_web3.zksync.contract(zk_web3.to_checksum_address(TOKENS[token][0]), abi=get_erc20_abi())
            balance = token_contact.functions.balanceOf(account2_address).call()
        except Exception:
            print('Ошибка блокчейна')
            time.sleep(10)
        else:
            break
    try:
        balance = float(str(balance / 10 ** TOKENS[token][1])[:6])
    except Exception:
        balance = 0
    return balance


def get_now_eth_balance(mnemonic):
    while True:
        try:
            Account.enable_unaudited_hdwallet_features()
            account = Account.from_mnemonic(mnemonic)
            zksync_web3 = ZkSyncBuilder.build(RPC)
            zk_balance = zksync_web3.zksync.get_balance(account.address, EthBlockParams.LATEST.value)
        except Exception:
            print('Ошибка блокчейна')
            time.sleep(10)
        else:
            break
    return zk_balance / 10**18


def get_tx_max_price(count):
    w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    while True:
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        if gas_price_gwei >= MAX_ETH_GAS_PRICE:
            print('Цена на газ слишком высока, ожидаю снижения цен')
            time.sleep(100)
        else:
            break
    coef = gas_price_gwei / 13
    price = 0.0003 * float(coef) * count + 0.0015
    return price


def transfer_all_arbitrum_eth(to_address, mnemonic, sender_address):
    Account.enable_unaudited_hdwallet_features()
    provider_url = "https://rpc.ankr.com/arbitrum"
    while True:
        try:
            web3 = Web3(Web3.HTTPProvider(provider_url))
            account: LocalAccount = web3.eth.account.from_mnemonic(mnemonic)
            private_key = account._private_key
            balance_in_wei = web3.eth.get_balance(sender_address)
        except Exception:
            print('Ошибка в получения данных из блокчейна, повторяю')
            time.sleep(10)
        else:
            break
    balance_in_wei -= web3.to_wei('0.1', 'gwei') * 800000
    if balance_in_wei <= 0:
        return False
    transaction = {
        'to': web3.to_checksum_address(to_address),
        'value': balance_in_wei,
        'gas': 800000,
        'gasPrice': web3.to_wei('0.1', 'gwei'),  # Замените на желаемую цену газа
        'nonce': web3.eth.get_transaction_count(sender_address),
    }
    while True:
        try:
            signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
            transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        except Exception:
            print('Ошибка в получения данных из блокчейна, повторяю')
            time.sleep(10)
        else:
            break
    return web3.to_hex(transaction_hash)

