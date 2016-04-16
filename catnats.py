#! /usr/bin/env python

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


def connect(host, port):
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def parse_info(data):
    if not data.startswith('INFO '):
        raise Exception("Expected an INFO msg here, but didn't receive it.")
    return json.loads(data[5:])

def can_upgrade_ssl(data):
    nl = data.index(b'\r\n')
    if nl > 0:
        server_info = parse_info(data[:nl].decode('utf-8'))
        return server_info['tls_required']
    return False

def receiver(sock):
    while 1:
        try:
            data = sock.recv(4096)
            if not data:
                os._exit(0)
            print(data.decode('utf-8'), end='')
        except socket.error as e:
            print(e, file=sys.stderr)
            os._exit(0)

def main():
    if len(sys.argv) != 3:
        print('usage: {0} host port'.format(sys.argv[0]))
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    try:
        sock = connect(host, port)
    except socket.error as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    # gnatsd sends the INFO message on connect.
    # parse it and upgrade the socket to SSL if necessary
    data = sock.recv(4096)
    if can_upgrade_ssl(data):
        sock = ssl.wrap_socket(sock)
    print(data.decode('utf-8'), end='')

    t = threading.Thread(target=receiver, args=(sock,))
    t.setDaemon(True)
    t.start()

    try:
        while 1:
            line = sys.stdin.readline()
            line = line.rstrip('\r\n').encode('utf-8')
            if not line:
                break
            sock.send(line + b'\r\n')
        time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
