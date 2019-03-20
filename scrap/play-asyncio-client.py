import time
from sys import stdin

if __name__ == '__main__':
    bar = 'foo'
    while True:
        print(bar)

        bar = input()

        time.sleep(1)