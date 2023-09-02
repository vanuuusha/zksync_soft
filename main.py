import multiprocessing
import random
import time
from web3.auto import w3
from Trader import Trader
import settings
from okx import okx_withdraw, okx_withdrawal_subs
import logging.config
from logger_configs import LOGGING_CONFIG
from blockchain import get_tx_max_price, get_now_eth_balance, get_now_token_balance, transfer_all_arbitrum_eth
from eth_account import Account
from inner_funcs import print_with_time
import traceback


logging.config.dictConfig(LOGGING_CONFIG)
error_logger = logging.getLogger('error_logger')


def swap_wrapper(func_name):
    count_repeats = 0
    start_balance = 0

    def inner_swap(self, public_key, token1, count, token2, name):
        nonlocal count_repeats, start_balance
        count_repeats += 1
        if count_repeats == 1:
            if token2 == 'ETH':
                start_balance = get_now_token_balance(public_key, token1)
            else:
                start_balance = get_now_token_balance(public_key, token2)

        try:
            if count_repeats == 5:
                if token1 == 'ETH':
                    raise SystemExit
                else:
                    raise StopIteration

            func = self.trader.__getattribute__(func_name)
            func(token1, count, token2)

            if token2 == 'ETH':
                end_balance = get_now_token_balance(public_key, token1)
            else:
                end_balance = get_now_token_balance(public_key, token2)

            if end_balance == start_balance:
                time.sleep(30)
                if token2 == 'ETH':
                    end_balance = get_now_token_balance(public_key, token1)
                else:
                    end_balance = get_now_token_balance(public_key, token2)

                if end_balance == start_balance:
                    raise Exception

        except SystemExit:
            raise SystemExit
        except StopIteration:
            raise StopIteration
        except Exception as e:
            error_logger.info(f'\n\n\n\nОшибка в обмене токенов \n{traceback.format_exc()}')
            self.trader.driver.quit()
            self.init_trader()
            inner_swap(self, public_key, token1, count, token2, name)

    return inner_swap


def retry(func_name):
    count = 0

    def inner(self, *args, **kwargs):
        nonlocal count
        count += 1
        if count == 4:
            return False
        try:
            func = self.trader.__getattribute__(func_name)
            func(*args, **kwargs)
            return True
        except Exception:
            error_logger.info(f'\n\n\n\nОшибка в перезапускаемом процессе \n{traceback.format_exc()}')
            self.trader.driver.quit()
            self.init_trader()
            return inner(self, *args, **kwargs)
    return inner


class Worker:
    def __init__(self, info):
        self.public_key = info['public_key']
        self.mnemonic = info['mnemonic']
        self.proxy = info['proxy']
        self.withdraw_address = info['okx']
        self.my_number = info['count']
        self.screen = settings.SCREEN
        self.init_trader()
        if not settings.WORK_ANTIDETECT_MODE:
            self.work()
            self.trader.driver.quit()
            print_with_time(f'Аккаунт {self.my_number}: работа закончена')

    def init_trader(self):
        try:
            self.trader = Trader(seed_phrase=self.mnemonic, show_display=self.screen, proxy=self.proxy)
            if not settings.WORK_ANTIDETECT_MODE:
                self.trader.change_network('zksync')
        except Exception:
            try:
                self.trader.driver.quit()
            except Exception:
                pass
            try:
                self.trader = Trader(seed_phrase=self.mnemonic, show_display=self.screen, proxy=self.proxy)
                if not settings.WORK_ANTIDETECT_MODE:
                    self.trader.change_network('zksync')
            except Exception:
                print_with_time(f'Аккаунт {self.my_number}: Самая критическая ошибка, не запустилась')
                raise Exception('Ошибка запуска')

    def syncswap_swapper(self, settings_copy, balance, token1, token2):
        print_with_time(f'Аккаунт {self.my_number}: Пытаюсь обменять {token1}-{token2} на syncswap')
        try:
            swap_wrapper('syncswap_swap')(self, self.public_key, token1, balance, token2, 'syncswap')
        except SystemExit:
            print_with_time(f'Аккаунт {self.my_number}: произошла ошибка на syncswap, не удалось обменять {token1}-{token2}, пропускаю')
            settings_copy['syncswap'] = False
        except StopIteration:
            print_with_time(f'Аккаунт {self.my_number}: произошла критическая ошибка на syncswap, не удалось обменять {token1}-{token2}')
            settings_copy['STOP'] = True
        else:
            print_with_time(f'Аккаунт {self.my_number}: Завершен свап на SYNCSWAP {token1}-{token2}')

        if token2 != 'ETH':
            balance = get_now_token_balance(self.public_key, token2)
        else:
            balance = 0
        return balance

    def others_swapper(self, name, settings_copy, balance, token1, token2):
        method_name = name+'_swap'
        print_with_time(f'Аккаунт {self.my_number}: Пытаюсь обменять {token1}-{token2} на {name}')
        try:
            swap_wrapper(method_name)(self, self.public_key, token1, balance, token2, name)
        except SystemExit:
            print_with_time(f'Аккаунт {self.my_number}: произошла ошибка на {name}, не удалось обменять {token1}-{token2}, пропускаю')
            settings_copy[name] = False
        except StopIteration:
            print_with_time(f'Аккаунт {self.my_number}: произошла критическая ошибка на {name}, не удалось обменять {token1}-{token2}, пытаюсь вернуть токены через SYNCSWAP')
            try:
                swap_wrapper('syncswap_swap')(self, self.public_key, token1, balance, 'ETH', 'syncswap')
            except StopIteration:
                print_with_time(f'Аккаунт {self.my_number}: произошла критическая ошибка на syncswap, не удалось обменять {token1}-{token2}')
                settings_copy['STOP'] = True
            settings_copy[name] = False
        else:
            print_with_time(f'Аккаунт {self.my_number}: Завершен свап на {name} {token1}-{token2}')

        if token2 != 'ETH':
            balance = get_now_token_balance(self.public_key, token2)
        else:
            balance = 0
        return balance

    def work(self):
        if settings.ENTER_MONEY:
            print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс пополнения с биржи')
            volume = settings.VOLUME
            try:
                okx_withdraw(self.public_key, volume, self.my_number)
            except Exception:
                error_logger.info(f'\n\n\n\nОшибка в процессе вывода средств с биржи \n{traceback.format_exc()}')
                print_with_time(f'Не удалось вывести средства с биржи, прекращаю работу аккаунта {self.my_number}')
                return
        settings_copy = {
            'syncswap': settings.syncswap,
            'sync_count_swaps': random.randint(settings.syncswap_swap[0], settings.syncswap_swap[1]),
            'SYNCSWAP_LIQUIDUTY': settings.SYNCSWAP_LIQUIDUTY,
            'mute': settings.mute,
            'mute_count_swaps': random.randint(settings.mute_swap[0], settings.mute_swap[1]),
            'space': settings.space,
            'space_count_swaps': random.randint(settings.space_swap[0], settings.space_swap[1]),
            'pancake': settings.pancake,
            'pancake_count_swaps': random.randint(settings.pancake_swap[0], settings.pancake_swap[1]),
            'mav': settings.mav,
            'mav_count_swaps': random.randint(settings.mav_swap[0], settings.mav_swap[1]),
            'MUTE_LIQUIDUTY': settings.MUTE_LIQUIDUTY,
            'MUTE_REMOVE_LIQUIDUTY': settings.MUTE_REMOVE_LIQUIDUTY,
            'BRIDGE': settings.BRIDGE,
            'DOMEN': settings.DOMEN,
            'eralend_supply': settings.eralend_supply,
            'eralend_withdraw': settings.eralend_withdraw,
            'zkswap': settings.zkswap,
            'zkswap_count_swap': random.randint(settings.zkswap_count_swap[0], settings.zkswap_count_swap[1]),
            'izi_token': settings.IZI_TOKEN,
            'cake_token': settings.CAKE_TOKEN,
            'space_token': settings.SPACE_TOKEN,
            'mav_token': settings.MAV_TOKEN,
        }
        while True:
            print_with_time(f'Аккаунт {self.my_number}. Начинаю новый цикл действий')
            random_mod = random.randint(1, 4)

            if settings_copy['syncswap'] and random_mod == 1:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю работать с syncswap')
                if settings_copy['sync_count_swaps'] >= 4:
                    max_fee = get_tx_max_price(4)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0:
                        print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                        settings_copy['STOP'] = True
                        break

                    balance = self.syncswap_swapper(settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('syncswap'):
                        continue

                    balance = self.syncswap_swapper(settings_copy, balance, 'USDC', 'USDT')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('syncswap'):
                        continue

                    balance = self.syncswap_swapper(settings_copy, balance, 'USDT', 'USD+')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('syncswap'):
                        continue

                    self.syncswap_swapper(settings_copy, balance, 'USD+', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('syncswap'):
                        continue

                    settings_copy['sync_count_swaps'] -= 4

                elif settings_copy['sync_count_swaps'] >= 2:
                    max_fee = get_tx_max_price(2)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0:
                        print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                        settings_copy['STOP'] = True
                        break

                    balance = self.syncswap_swapper(settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('syncswap'):
                        continue

                    self.syncswap_swapper(settings_copy, balance, 'USDC', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('syncswap'):
                        continue

                    settings_copy['sync_count_swaps'] -= 2
                else:
                    print_with_time(f'Аккаунт {self.my_number} работа с syncswap закончена.')
                    settings_copy['syncswap'] = False

            if settings_copy['izi_token'] and random_mod == 2:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс покупки токена izi')
                max_fee = get_tx_max_price(2)
                eth_balance = get_now_eth_balance(self.mnemonic)
                want_to_spend = settings.count_izi - settings.count_izi * random.randint(1, 5) / 100
                if eth_balance < max_fee + want_to_spend:
                    print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                    settings_copy['STOP'] = True
                    break

                balance = self.syncswap_swapper(settings_copy, want_to_spend, 'ETH', 'iZi')
                if settings_copy.get('STOP', False):
                    settings_copy['izi_token'] = False
                    break
                if balance == 0:
                    settings_copy['izi_token'] = False
                    continue

                self.syncswap_swapper(settings_copy, balance, 'iZi', 'ETH')
                if settings_copy.get('STOP', False):
                    settings_copy['izi_token'] = False
                    break
                print_with_time(f'Аккаунт {self.my_number}. Завершена покупка токенов izi')
                settings_copy['izi_token'] = False

            if settings_copy['mav_token'] and random_mod == 2:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс покупки токена mav')
                max_fee = get_tx_max_price(2)
                eth_balance = get_now_eth_balance(self.mnemonic)
                want_to_spend = settings.count_MAV - settings.count_MAV * random.randint(1, 5) / 100
                try:
                    want_to_spend = float(str(want_to_spend)[:8])
                except Exception:
                    pass

                if eth_balance < max_fee + want_to_spend:
                    print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                    settings_copy['STOP'] = True
                    break

                balance = self.syncswap_swapper(settings_copy, want_to_spend, 'ETH', 'MAV')
                if settings_copy.get('STOP', False):
                    settings_copy['mav_token'] = False
                    break
                if balance == 0:
                    settings_copy['mav_token'] = False
                    continue

                self.syncswap_swapper(settings_copy, balance, 'MAV', 'ETH')
                if settings_copy.get('STOP', False):
                    settings_copy['mav_token'] = False
                    break
                print_with_time(f'Аккаунт {self.my_number}. Работа с токеном mav закончена')
                settings_copy['mav_token'] = False

            if settings_copy['space_token'] and random_mod == 3:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс покупки токена SPACE')
                max_fee = get_tx_max_price(2)
                eth_balance = get_now_eth_balance(self.mnemonic)
                want_to_spend = settings.count_SPACE - settings.count_SPACE * random.randint(1, 5) / 100
                if eth_balance < max_fee + want_to_spend:
                    print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                    settings_copy['STOP'] = True
                    break

                balance = self.syncswap_swapper(settings_copy, want_to_spend, 'ETH', 'SPACE')
                if settings_copy.get('STOP', False):
                    settings_copy['space_token'] = False
                    break
                if balance == 0:
                    settings_copy['space_token'] = False
                    continue

                self.syncswap_swapper(settings_copy, balance, 'SPACE', 'ETH')
                if settings_copy.get('STOP', False):
                    settings_copy['space_token'] = False
                    break
                print_with_time(f'Аккаунт {self.my_number}. Работа с токеном SPACE закончена')
                settings_copy['space_token'] = False

            if settings_copy['cake_token'] and random_mod == 3:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс покупки токена cake')
                max_fee = get_tx_max_price(2)
                eth_balance = get_now_eth_balance(self.mnemonic)
                now_volume = eth_balance - max_fee
                if now_volume < 0:
                    print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                    settings_copy['STOP'] = True
                    break
                now_volume = 0.0001 + random.randint(1, 5) / 100 * 0.0001
                result = retry('pancake_swap')(self, 'ETH', now_volume, 'CAKE')
                if result:
                    print_with_time(f'Аккаунт {self.my_number}. Завершена покупка токена cake')
                else:
                    print_with_time(f'Аккаунт {self.my_number}. Не смог завершить покупку токена cake')
                print_with_time(f'Аккаунт {self.my_number} работа с токеном cake закончена.')
                settings_copy['cake_token'] = False

            if settings_copy['zkswap'] and random_mod == 4:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю работать с zkswap')
                if settings_copy['zkswap_count_swap'] >= 2:
                    max_fee = get_tx_max_price(2)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0:
                        print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                        settings_copy['STOP'] = True
                        break

                    balance = self.others_swapper('zkswap', settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('zkswap'):
                        continue

                    self.others_swapper('zkswap', settings_copy, balance, 'USDC', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('zkswap'):
                        continue

                    settings_copy['zkswap_count_swap'] -= 2
                else:
                    print_with_time(f'Аккаунт {self.my_number}. Работа с zkswap закончена')
                    settings_copy['zkswap'] = False

            if settings_copy['mute'] and random_mod == 3:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю работать с mute')
                if settings_copy['mute_count_swaps'] >= 2:
                    max_fee = get_tx_max_price(2)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0.01:
                        print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                        settings_copy['mute'] = False
                        break

                    balance = self.others_swapper('mute', settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('mute'):
                        continue

                    self.others_swapper('mute', settings_copy, balance, 'USDC', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('mute'):
                        continue

                    settings_copy['mute_count_swaps'] -= 2
                else:
                    print_with_time(f'Аккаунт {self.my_number}. Работа с mute закончена')
                    settings_copy['mute'] = False

            if settings_copy['space'] and random_mod == 4:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю работать с space')
                if settings_copy['space_count_swaps'] >= 2:
                    max_fee = get_tx_max_price(2)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0:
                        print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                        settings_copy['STOP'] = True
                        break

                    balance = self.others_swapper('space', settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('space'):
                        continue

                    self.others_swapper('space', settings_copy, balance, 'USDC', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('space'):
                        continue

                    settings_copy['space_count_swaps'] -= 2
                else:
                    print_with_time(f'Аккаунт {self.my_number}. Работа с space закончена')
                    settings_copy['space'] = False

            if settings_copy['pancake'] and random_mod == 1:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю работать с pancake')
                if settings_copy['pancake_count_swaps'] >= 2:
                    max_fee = get_tx_max_price(2)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0:
                        print_with_time(f'Аккаунт {self.my_number}: недостаточно баланса для транзакций')
                        settings_copy['STOP'] = True
                        break

                    balance = self.others_swapper('pancake', settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('pancake'):
                        continue

                    self.others_swapper('pancake', settings_copy, balance, 'USDC', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('pancake'):
                        continue

                    settings_copy['pancake_count_swaps'] -= 2
                else:
                    print_with_time(f'Аккаунт {self.my_number}. Работа с pancakeswap закончена')
                    settings_copy['pancake'] = False

            if settings_copy['mav'] and random_mod == 2:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю работать с mav')
                if settings_copy['mav_count_swaps'] >= 2:
                    max_fee = get_tx_max_price(2)
                    eth_balance = get_now_eth_balance(self.mnemonic)
                    now_volume = eth_balance - max_fee
                    if now_volume < 0:
                        print_with_time(f'Аккаунт {self.my_number} недостаточно баланса для транзакций')
                        settings_copy['STOP'] = True
                        break

                    balance = self.others_swapper('mav', settings_copy, now_volume, 'ETH', 'USDC')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('mav'):
                        continue

                    self.others_swapper('mav', settings_copy, balance, 'USDC', 'ETH')
                    if settings_copy.get('STOP', False):
                        break
                    elif not settings_copy.get('mav'):
                        continue

                    settings_copy['mav_count_swaps'] -= 2
                else:
                    print_with_time(f'Аккаунт {self.my_number}. работа с mav была завершена')
                    settings_copy['mav'] = False

            if settings_copy['MUTE_LIQUIDUTY']:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс добавления ликвидности на mute')
                eth_balance = get_now_eth_balance(self.mnemonic)
                count_eth = settings.MUTE_ADD_LIQUIDUTY
                if (count_eth * 2 + get_tx_max_price(3)) > eth_balance:
                    raise Exception(f'Аккаунт {self.my_number}: Недостаточно баланса для добавления ликвидности в MUTE')

                self.syncswap_swapper(settings_copy, count_eth, 'ETH', 'USDC')
                if settings_copy.get('STOP', False):
                    break

                balance = get_now_token_balance(self.public_key, 'USDC')
                print_with_time(f'Аккаунт {self.my_number}: Пытаюсь добавить ликвидность на mute')
                result = retry('mute_add_liquiduty')(self, balance)
                if result:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность на mute добавлена')
                else:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность на mute не удалось добавить')
                    self.syncswap_swapper(settings_copy, balance, 'USDC', 'ETH')
                settings_copy['MUTE_LIQUIDUTY'] = False
                settings_copy['MUTE_REMOVE_LIQUIDUTY'] = False

            if settings_copy['SYNCSWAP_LIQUIDUTY'] and random_mod == 1:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс добавления ликвидности на syncswap')
                eth_balance = get_now_eth_balance(self.mnemonic)
                if get_tx_max_price(4) > eth_balance:
                    raise Exception('Недостаточно баланса для транзакций')

                self.syncswap_swapper(settings_copy, 0.0001, 'ETH', 'USDC')
                if settings_copy.get('STOP', False):
                    break

                balance = get_now_token_balance(self.public_key, 'USDC')
                if balance == 0:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность на syncswap не удалось добавить')
                    settings_copy['SYNCSWAP_LIQUIDUTY'] = False
                    continue

                print_with_time(f'Аккаунт {self.my_number}: Пытаюсь добавить ликвидность на syncswap')
                result = retry('syncswap_add_liquiduty')(self, balance)
                if result:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность на syncswap добавлена')
                else:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность на syncswap не удалось добавить')
                print_with_time(f'Аккаунт {self.my_number}: работа с добавление ликвидности на syncswap была запушена')
                settings_copy['SYNCSWAP_LIQUIDUTY'] = False

            if settings_copy['MUTE_REMOVE_LIQUIDUTY']:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс удаления ликвидности с mute')
                eth_balance = get_now_eth_balance(self.mnemonic)
                if get_tx_max_price(2) > eth_balance:
                    raise Exception(f'Аккаунт {self.my_number}: Недостаточно баланса для транзакций')

                result = retry('mute_remove_liquiduty')(self)
                if result:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность c mute удалена')
                else:
                    print_with_time(f'Аккаунт {self.my_number}: Ликвидность с mute не удалось удалить')
                print_with_time(f'Аккаунт {self.my_number}: ликвидность была удалена с mute, далее будет произвоиден обмен токенов')
                settings_copy['MUTE_REMOVE_LIQUIDUTY'] = False

                balance = get_now_token_balance(self.public_key, 'USDC')

                self.syncswap_swapper(settings_copy, balance, 'USDC', 'ETH')
                if settings_copy.get('STOP', False):
                    break

            if settings_copy['BRIDGE'] and random_mod == 3:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю бридж токенов в ETH')
                count = settings.bridge_count
                moddifier = random.randint(1, 5)
                count = float(str(count + count * moddifier / 100)[:8])
                eth_balance = get_now_eth_balance(self.mnemonic)
                if count + get_tx_max_price(1) > eth_balance:
                    raise Exception('Недосточно баланса для моста')

                result = retry('zkbridge_bridge')(self, count)
                if result:
                    print_with_time(f'Аккаунт {self.my_number}: Выполнин бридж в сеть эфира')
                else:
                    print_with_time(f'Аккаунт {self.my_number}: Не удалось выполнить бридж в сеть эфира')
                print_with_time(f'Аккаунт {self.my_number}: бридж в сеть эфира был завершен')
                settings_copy['BRIDGE'] = False

            if settings_copy['eralend_supply'] and random_mod == 4:
                print_with_time(f'Аккаунт {self.my_number}: Пытаюсь добавить обеспечение в eralend')
                count_eth = settings.eralend_supply_amount
                eth_balance = get_now_eth_balance(self.mnemonic)
                if count_eth + get_tx_max_price(1) > eth_balance:
                    raise Exception('Недосточно баланса для добавления обеспечения')

                result = retry('eralend_supply')(self, count_eth)
                if result:
                    print_with_time(f'Аккаунт {self.my_number}: Добавлена обеспечение в eralend')
                else:
                    print_with_time(f'Аккаунт {self.my_number}: Не удалось добавить обеспечение в eralend')
                print_with_time(f'Аккаунт {self.my_number}: Обеспечение в eralend было добавлено')
                settings_copy['eralend_supply'] = False

            if settings_copy['DOMEN'] and random_mod == 3:
                print_with_time(f'Аккаунт {self.my_number}. Начинаю процесс покупки домена')
                eth_balance = get_now_eth_balance(self.mnemonic)
                if 0.0023 + get_tx_max_price(1) > eth_balance:
                    raise Exception('Недостаточно баланса для покупки домена')

                result = retry('domain')(self, self.public_key[:10])
                if result:
                    print_with_time(f'Аккаунт {self.my_number}: покупка домена выполнена')
                else:
                    print_with_time(f'Аккаунт {self.my_number}: Не удалось выполнить покупку домена')
                print_with_time(f'Аккаунт {self.my_number}: работа с доменом завершена')
                settings_copy['DOMEN'] = False

            if all(element is False for element in [settings_copy['DOMEN'], settings_copy['BRIDGE'], settings_copy['MUTE_REMOVE_LIQUIDUTY'], settings_copy['MUTE_LIQUIDUTY'], settings_copy['mav'], settings_copy['pancake'], settings_copy['mute'], settings_copy['syncswap'], settings_copy['space'], settings_copy['SYNCSWAP_LIQUIDUTY'], settings_copy['eralend_supply'], settings_copy['cake_token'], settings_copy['mav_token'], settings_copy['izi_token'], settings_copy['space_token']]):
                break

        if settings_copy.get('STOP'):
            print_with_time(f'Аккаунт {self.my_number}. Произошла ошибка, поэтому работа над аккаунтом не была закончена')
            return

        if settings_copy['eralend_withdraw']:
            print_with_time(f'Аккаунт {self.my_number}: Пытаюсь вывести обеспечение в eralend')
            count_eth = settings.eralend_withdraw_amount
            eth_balance = get_now_eth_balance(self.mnemonic)
            if get_tx_max_price(1) > eth_balance:
                raise Exception('Недосточно баланса для вывода из eralend')

            result = retry('eralend_withdraw')(self, count_eth)
            if result:
                print_with_time(f'Аккаунт {self.my_number}: Успешный вывод из eralend')
            else:
                print_with_time(f'Аккаунт {self.my_number}: Не удался вывод из eralend')
            print_with_time(f'Аккаунт {self.my_number}: eralend вывод средс был завершен')
            settings_copy['eralend_withdraw'] = False

        if settings.WITHDRAW_MONEY:
            print_with_time(f'Аккаунт {self.my_number}. Собираюсь выводить деньги')
            eth_balance = get_now_eth_balance(self.mnemonic)
            percent = settings.percentage
            count_eth_to_withdraw = float(str(eth_balance * percent / 100)[:6]) - get_tx_max_price(1) - 0.001
            if float(count_eth_to_withdraw) + get_tx_max_price(1) - 0.005 > eth_balance:
                raise Exception(f'Аккаунт {self.my_number}. Недосточно баланса для вывода средств уменьшите процент вывода')

            result = retry('orbiter')(self, count_eth_to_withdraw)
            print_with_time(f'Аккаунт {self.my_number}. Воспользовался мостом orbiter')
            if result:
                print_with_time(f'Аккаунт {self.my_number}: eth успешно переведен в arbitrum')
            else:
                print_with_time(f'Аккаунт {self.my_number}: eth не удалось перевести в arbitrum')
                return
            tx_hash = transfer_all_arbitrum_eth(self.withdraw_address, self.mnemonic, self.public_key)
            print_with_time(f'Аккаунт {self.my_number}. Отправлена транзакция в okx {tx_hash} (arbitrum)')
            print_with_time(f'Аккаунт {self.my_number}. Жду пока транзакция будет доставлена в okx')
            time.sleep(250)
            okx_withdrawal_subs()


def start():
    with open('file.txt', 'r+') as file:
        lines = file.readlines()
        for count, line in enumerate(lines):
            if count == 0:
                continue
            if ')' in line:
                continue
            lines[count] = f'{count}) ' + line
        file.seek(0)
        file.writelines(lines)
        file.truncate()

    wallets = []
    with open('file.txt', 'r') as file:
        count = 0
        for line in file.readlines():
            if count == 0:
                count += 1
                continue
            mnemonic, withdraw_address, proxy = line.split(')')[1].split('-')
            proxy = proxy.replace(' ', '').replace('\n', '')
            if proxy:
                first, second = proxy.split('@')
                proxy = {}
                proxy['login'], proxy['password'] = first.split(':')
                proxy['ip'], proxy['port'] = second.split(':')
            else:
                proxy = None
            Account.enable_unaudited_hdwallet_features()
            mnemonic, withdraw_address = mnemonic.strip(), withdraw_address.strip()
            account = w3.eth.account.from_mnemonic(mnemonic)
            public_key = w3.to_checksum_address(account.address)
            wallets.append({'okx': withdraw_address, 'public_key': public_key, 'mnemonic': mnemonic, 'proxy': proxy, 'count': count})
            count += 1

    if settings.WORK_ANTIDETECT_MODE:
        account_num = settings.account_num
        work = Worker(wallets[account_num - 1])
        time.sleep(100000)
    else:
        while wallets:
            process = []
            for _ in range(settings.COUNT_ACCOUNTS):
                try:
                    info = wallets.pop()
                    print_with_time(f'Начинаю работу над аккаунтом {info["count"]}')
                    process.append(multiprocessing.Process(target=Worker, args=(info, )))
                except IndexError:
                    break

            for proc in process:
                proc.start()

            for proc in process:
                proc.join()


if __name__ == "__main__":
    start()
