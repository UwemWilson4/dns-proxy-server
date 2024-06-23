# dns-proxy-server

# Never touch your local /etc/hosts file in OS X again

## Requirements

* [Homebrew](https://brew.sh/)

## Install
```
brew install dnsmasq
```

## Setup

### Create config directory
```
mkdir -pv $(brew --prefix)/etc/
```

### Setup *.test

```
echo 'server=127.0.0.1' >> $(brew --prefix)/etc/dnsmasq.conf
```
### Enable logging
```
echo 'log-queries' >> $(brew --prefix)/etc/dnsmasq.conf
echo 'log-facility=/usr/local/var/log/dnsmasq.log' >> $(brew --prefix)/etc/dnsmasq.conf
```

## Autostart dnsmasq - now and after reboot
```
sudo brew services start dnsmasq
```

## Start the custom resolver
```
pipenv run python CustomResolver.py
```

## Finished

That's it! You can run scutil --dns to show all of your current resolvers, and you should see that all requests for a domain ending in .test will go to the DNS server at 127.0.0.1

## N.B. never use .dev as a TLD for local dev work. .test is fine though.