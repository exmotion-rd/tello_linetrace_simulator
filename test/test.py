import socket
import time

def main():
    serv_address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    send_len = sock.sendto('t'.encode('utf-8'), serv_address)
    time.sleep(5)
    send_len = sock.sendto('w'.encode('utf-8'), serv_address)
    time.sleep(5)
    send_len = sock.sendto('s'.encode('utf-8'), serv_address)
    time.sleep(5)
    send_len = sock.sendto('a'.encode('utf-8'), serv_address)
    time.sleep(5)
    send_len = sock.sendto('d'.encode('utf-8'), serv_address)
    time.sleep(5)
    send_len = sock.sendto('q'.encode('utf-8'), serv_address)
    time.sleep(5)

if __name__ == '__main__':
    main()
