#!/usr/bin/env python3


import socket
import json
import database_service as ds
import sys
import os


def main():
    HOST = '0.0.0.0'
    PORT = 3000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = json.loads(data)
                    if data['service'] == 'get_count':
                        data = ds.get_data_count(data['label_name'], data['count'])
                        conn.sendall(bytes(json.dumps(len(data)), 'utf-8'))
                    else:
                        data = ds.get_data(data['count'] , data['sort_order'])
                        conn.sendall(bytes(json.dumps(len(data)), 'utf-8'))
                    conn.sendall(bytes(data, 'utf-8'))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Server Interrupted')
        print('Closing all connections')
        ds.close_conn()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)