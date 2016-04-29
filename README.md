# catnats

`cat` for [NATS](http://nats.io) gnatsd server. Works for both TLS and non-TLS connections.


## NEWS

* **2016-04-29**: Version 0.1.0:

  * Changed how the server address is specified. You can now use `--addr host:port`
  * If no adddress is specified, the default `127.0.0.1:4222` is used.
  * Added the following `CONNECT` message parameters: `--user`, `--pass` and `--verbose`. If any of
  these parameters is given in the command line, a `CONNECT` message is sent to the server.


## Requirements

Python 2.7.6+ or Python 3.4+ is required.

Non-TLS connections should work on all platforms. TLS connections require:

* on Ubuntu 14.04, Python 2.7 and Python 3.4 works out of the box
* on OSX (El-Capitan) you need to install an updated version of Python with updated OpenSSL
using `brew install python --with-brewed-openssl`
* on Windows, Python 3.5 works

## Usage

`catnats.py [options]`

### Options:

* `-addr`: Specify the server address and port in the form of `HOST:PORT` 
* `-q` or `--quiet`: Suppress output
* `--pong`: Enable automatically sending a `PONG` message to gnatsd
when a `PING` message is received (to keep the connection alive)
* `--no-exit`: Do not exit automatically (unless there is an error)
* `--user USER`: Send a `CONNECT` message with `user` field set to `USER`
* `--pass PASSWORD`: Send a `CONNECT` message with `pass` field set to `PASSWORD`
* `--verbose true | false`: Send a `CONNECT` message with `verbose` field set to `VERBOSE`
 
### Examples

Works with pipes:

```
$ printf 'connect {}\r\nping\r\n' | ./catnats.py -q --addr demo.nats.io:4443
```

And without:

```
$ ./catnats.py --pong --addr demo.nats.io:4443
```

Publish time and date every 5 seconds:

```
$ while true; do time=`date` && \
  printf "PUB device-time.$(hostname) ${#time}\r\n${time}\r\n" | \
  ./catnats.py --quiet --addr demo.nats.io:4443; sleep 5; done
```

Send load average every 5 seconds (on Linux)

```
$ while true; do payload=`cat /proc/loadavg | cut -f 1-3 -d" "` && \
  printf "PUB device-avgload.$(hostname) ${#payload}\r\n${payload}\r\n" | \
  ./catnats.py --quiet --addr demo.nats.io:4222; sleep 5; done
```

The same on OSX

```
$ while true; do payload=`sysctl -n vm.loadavg | cut -f 2-4 -d" "` && \
  printf "PUB device-avgload.$(hostname) ${#payload}\r\n${payload}\r\n" | \
  ./catnats.py --quiet --addr demo.nats.io:4222; sleep 5; done
```

## License

```
Copyright (c) 2016, Yuce Tekol <yucetekol@gmail.com>.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

* The names of its contributors may not be used to endorse or promote
  products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
