from datetime import datetime


def print_with_time(msg):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f'{formatted_time}: {msg}')