from .Trader import Trader
import socket

class TraderSocket:
    def __init__(self):
        self.trader = Trader()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, TRADER_PORT))
        self.now_net = ''
        self.restart_listen()

    def restart_listen(self):
        while True:
            try:
                self.listen()
            except Exception:
                print('Произошла ошибка, пытаюсь слушать дальше')

    def send_data(self, data):
        data = json.dumps(data)
        self.client_socket.sendall(data.encode())

    def listen(self):
        self.socket.listen()
        self.client_socket, self.client_address = self.socket.accept()
        while True:
            data = self.client_socket.recv(4096)
            data = json.loads(data.decode())
            if data.get('method') == 'swap':
                result = self.swap(data)
            elif data.get('method') == 'change_network':
                result = self.change_network(data)
            self.send_data(result)

    def change_network(self, data):
        new_net = data.get('net')
        if self.now_net != new_net:
            self.trader.change_network('zksync')

    def swap(self, data):
        site = data.get('site')
        token1 = data.get('token1')
        count = float(data.get('count'))
        token2 = data.get('token2')
        self.trader.swap(site, token1, count, token2)


if __name__ == '__main__':
    TraderSocket()