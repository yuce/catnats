# catnats

`cat` for [NATS](http://nats.io) gnatsd server. Works for both TLS and non-TLS connections.

## Requirements

Python 2.7.6+ or Python 3.4+ is required.

Non-TLS connections should work on all platforms. TLS connections requires:

* on Ubuntu 14.04, Python 2.7 and Python 3.4 works out of the box
* on OSX (El-Capitan) you need to install an updated version of Python with updated OpenSSL
using `brew install python --with-brewed-openssl`
* on Windows, Python 3.5 works

## Usage

`catnats.py gnatsd_host gnatsd_port`

Example:

```
$ printf 'connect {}\r\nping\r\n' | ./catnats.py demo.nats.io 4443
```

Of course, pipes are not needed:

```
$ ./catnats.py demo.nats.io 4443
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