#! /usr/bin/env python3

# Copyright (c) 2016, Yuce Tekol <yucetekol@gmail.com>.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.

# * The names of its contributors may not be used to endorse or promote
#   products derived from this software without specific prior written
#   permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import socket
import ssl
import threading
import time
import json
import argparse


VERSION = '0.1.2'
DEFAULT_PORT = 4222

"""
nats 127.0.0.1:4222 CONNECT --user user --pass 123 PUB loadavg.$(hostname) -p "$(cat /proc/loadavg)"
vs
payload=`cat /proc/loadavg` && printf "PUB loadavg.$(hostname) ${#payload}\r\n${payload}\r\n" | nats -q --user demo --pass 123 --addr 127.0.0.1:4222 
"""

def connect(host, port):
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def parse_info(data):
    if not data.startswith('INFO '):
        raise Exception("Expected an INFO msg here, but didn't receive it.")
    return json.loads(data[5:])


def has_ping_in(data):
    # Note that we are oversimplifying things a lot here
    # There can be more than one PING msg, or there can be none
    # (e.g., if a MSG contains PING\r\n in its payload)
    # Sending a single PONG for 0 or many PINGs should be safe.
    return b'PING\r\n' in data


def send_pong(sock):
    sock.send(b'PONG\r\n')


def can_upgrade_ssl(data):
    nl = data.index(b'\r\n')
    if nl > 0:
        server_info = parse_info(data[:nl].decode('ascii'))
        return server_info['tls_required']
    return False


def receiver(sock, auto_pong=False, quiet=False):
    while 1:
        try:
            data = sock.recv(4096)
            if not data:
                os._exit(0)
            if auto_pong and has_ping_in(data):
                send_pong(sock)
            if not quiet:
                try:
                    print(data.decode('utf-8'), end='')
                except Exception:
                    print('[BINARY BLOB]')
        except socket.error as e:
            print(e, file=sys.stderr)
            os._exit(0)


def make_connect_message(params):
    if all(not x for x in params.values()):
        return ''
    return 'CONNECT {}\r\n'.format(json.dumps(params))


def extract_host_port(s):
    host_port = s.split(':', 1)
    if len(host_port) == 1:
        return host_port[0], DEFAULT_PORT
    if len(host_port) > 2:
        raise Exception('Invalid address: {}'.format(s))
    return host_port[0], int(host_port[1])


def parse_verbose(s):
    if s is None:
        return None
    elif s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise Exception('Invalid `verbose` value: {}'.format(s))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help='specify host:port')
    parser.add_argument('--user', help='specify the `user` field in the CONNECT message')
    parser.add_argument('--pass', help='specify the `password` field in the CONNECT message')
    parser.add_argument('--verbose', help='specify the `verbose` field in the CONNECT message')
    parser.add_argument('-q', '--quiet',
                        help='suppress output',
                        action='store_true')
    parser.add_argument('--raw',
                        help='raw input (do not convert the input to text)',
                        action='store_true')
    parser.add_argument('--pong',
                        help='turns auto-PONG on',
                        action='store_true')
    parser.add_argument('--no-exit',
                        help='do not exit automatically (unless there is an error)',
                        action='store_true')
    parser.add_argument('--version',
                        help='Display the version and exit',
                        action='store_true')                        
  
    args = parser.parse_args()
    
    if args.version:
        print(VERSION)
        sys.exit(0)
        
    host_port = args.addr or '127.0.0.1:4222'
    host, port = extract_host_port(host_port)

    try:
        sock = connect(host, port)
    except socket.error as e:
        print(e, file=sys.stderr)
        sys.exit(2)
        
    if args.raw:
        sys.stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0)        

    # gnatsd sends the INFO message on connect.
    # parse it and upgrade the socket to SSL if necessary
    data = sock.recv(4096)
    if can_upgrade_ssl(data):
        sock = ssl.wrap_socket(sock)
    if not args.quiet:
        try:
            print(data.decode('utf-8'), end='')
        except UnicodeEncodeError:
            print('[BINARY BLOB]')

    connect_verbose = parse_verbose(args.verbose)
    connect_msg = make_connect_message({'user': args.user,
                                        'pass': getattr(args, 'pass'),
                                        'verbose': connect_verbose})
    if connect_msg:
        sock.send(connect_msg.encode('ascii'))

    t = threading.Thread(target=receiver,
                         args=(sock,),
                         kwargs=dict(auto_pong=args.pong, quiet=args.quiet))
    t.setDaemon(True)
    t.start()

    try:
        while 1:
            if args.raw:            
                line = sys.stdin.read()
            else:
                line = sys.stdin.readline().rstrip('\r\n').encode('utf-8')
            if not line:
                if args.no_exit:
                    time.sleep(1)
                else:
                    break
            else:
                sock.send(line if args.raw else line + b'\r\n')
        time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
