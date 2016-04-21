# NDT End-to-End Client Worker

[![Build
Status](https://travis-ci.org/m-lab/ndt-e2e-clientworker.svg?branch=master)](https://travis-ci.org/m-lab/ndt-e2e-clientworker)
[![Coverage
Status](https://coveralls.io/repos/m-lab/ndt-e2e-clientworker/badge.svg?branch=master&service=github)](https://coveralls.io/github/m-lab/ndt-e2e-clientworker?branch=master)

## Pre-Requisites

To run tests against non-Banjo clients, the user can install pre-requisites
with:

```
pip install -r requirements.txt
```

To run tests against the Banjo NDT client, the user needs to [install
mitmproxy](http://docs.mitmproxy.org/en/latest/install.html) and either create
a mitmdump replay file or use an existing one. For details on creating a replay
file, see the section below.

## Creating a mitmdump HTTP Replay File

For clients that are difficult to host as static files, the NDT client wrapper
uses `mitmdump` to replay HTTP traffic to replicate the behavior of those
clients, but without communicating with a remote server. In order to replicate
a web application that hosts an NDT client, the user must first create a
`mitmdump` HTTP replay file.

For example, imagine that we wish to locally replicate an NDT client hosted at:

  http://example.com/tests/ndt

### 1. Start `mitmdump`

We first run `mitmdump` as follows:

```
mitmdump \
  --port 8123 \
  --reverse http://example.com \
  --no-http2 \
  --setheader :~q:Host:example.com \
  --wfile /tmp/example.com-output.replay
```

This runs `mitmdump` as a [reverse
proxy](http://docs.mitmproxy.org/en/latest/features/reverseproxy.html) against
example.com. We also rewrite the `Host:` header so that our reverse proxy
forwards HTTP requests to the real example.com server and makes them appear
similar to normal requests.

### 2. Capture browser traffic

With `mitmdump` running, open a browser and navigate to:

  http://localhost:8123/tests/ndt

After the NDT test is complete, end the `mitmdump` with Ctrl+C and the replay
file will appear in the output path.

### 3. Run client\_wrapper

Once we have a replay file, we can run the `client_wrapper` as follows:

```
python client_wrapper/client_wrapper.py \
  --client <client name> \
  --browser firefox \
  --server ndt-iupui-mlab2-nuq0t.measurement-lab.org \
  --client_path /tmp/example.com-output.replay \
  --output /tmp
```

### Limitations

The reverse proxy only captures traffic intended for a single origin (domain +
port pair). If the web application's NDT client relies on CORS requests to
to multiple origins (not including mlab-ns), the `client_wrapper` NDT HTTP
replay server will not be able to replicate the web app locally. The replay
server does handle CORS requests to mlab-ns by creating a fake mlab-ns server
locally.
