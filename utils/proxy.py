# download tor : homebrew install tor
# start tor in terminal by 'tor'
# congfigure /opt/homebrew/etc/tor/torrc file
# enable ControlPort 9051
# enable CookieAuthentication 1
# restart tor maybe have to kill tor from activity monitor
# maybe pip install pysocks required
import requests
from stem import Signal
from stem.control import Controller


def renew_proxy():
    with Controller.from_port(port=9051) as c:
        c.authenticate(password="nhhtq103")
        c.signal(Signal.NEWNYM)  # change ip address
    proxy = {
        "http": "socks5://localhost:9050",
        "https": "socks5://localhost:9050",
    }
    r = requests.get("https://httpbin.org/get", proxies=proxy)  # using TOR network
    print(r.json()["origin"])
    return proxy
