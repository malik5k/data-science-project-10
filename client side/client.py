#!/usr/bin/env python3

import socket
import argparse
import sys
import json

def get_args():
    '''Gets the arguments from the command line.'''
    parser = argparse.ArgumentParser("Run the script to get the required informations from the server.")
    
    # -- Create the descriptions for the commands
    i_desc = "The IP address of the Server"
    s_desc = "The service wanted from the server (get_count or get_data)"
    l_desc = "The label_name is required in case you want the service get_count (either positive or negative)."
    c_desc = "The Count (is required in case of get_data service)"
    sort_desc = "The sorting rule for data either ASC ascending or DESC for descending (default ASC)."
	
	# -- Add required and optional groups
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
	
	# -- Create the arguments
    required.add_argument("-i", help=i_desc, required=True)
    required.add_argument("-s", help=s_desc, choices=['get_count','get_data'], required=True)
    optional.add_argument("-l", help=l_desc, choices=['positive','negative'])
    optional.add_argument("-c", help=c_desc)
    optional.add_argument("-sort", help=sort_desc, choices=['ASC','DESC'], default='ASC')
	
	# -- Get the arguments from the console
    args = parser.parse_args()
    if args.s == 'get_count' and not args.l:
        print("Error : The -l (label_name) is required in case you want the service get_count (either positive or negative)")
        sys.exit(1)
    elif args.s == 'get_data' and not args.c and not args.sort_order:
        print("""Error : The -c (count) and -sort [ASC or DESC] are required in case 
		you want the service get_data (either positive or negative)""")
        sys.exit(1)
    return args


args = get_args()
data = dict()
if args.s == 'get_count': 
    data['service'] = 'get_count'
    data['label_name'] = args.l
    data['count'] = args.c
else:
    data['service'] = 'get_data'
    data['count'] = args.c
    data['sort_order'] = args.sort

data = json.dumps(data)
HOST = args.i
PORT = 3000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        s.sendall(bytes(data, 'utf-8'))
		# get the data size from the server
        data_size = json.loads(s.recv(1024))
        received_payload = b""
        reamining_payload_size = data_size
		# start reciving the data.
        while reamining_payload_size != 0:
            received_payload += s.recv(reamining_payload_size)
            reamining_payload_size = data_size - len(received_payload)
        data = json.loads(received_payload)
    except socket.error as e:
        print('Unexpected Error')
        print(e)
        sys.exit(1)

print('Received', data)