Certbot DNS Auth Plugin for name.com
===============================================================================================================

There are a number of blog posts on the internet (including [certbot's own](https://certbot.eff.org/faq#does-let-s-encrypt-issue-wildcard-certificates))
indicating that you can use DNS to obtain certificates, but few actual instructions for doing so. This repo
attempts to provide both better end-to-end instructions for obtaining certificates based on DNS authentication
(below) and also a script (written by [@laonon](https://github.com/laonon)) for doing so.


## Installation

### Package-Based

The easiest way is to install the package (currently only available on deb-based systems - please contribute if
you know how to package for other systems!), which is available at https://packages.kaelshipman.me/. It is called
`certbot-dns-namecom`. Installing it will create a configuration file at `/etc/certbot-dns-namecom.config.json`
with values that you've indicated in your package setup.

### Manual

If you prefer to install manually, here's what you need to do (roughly):

1. Put the `src/certbot-dns-name_com.py` script somewhere on your machine (cloning this repo to your home directory
   is sufficient, so long as you don't move it after, since certbot will use the same location for renewals).
2. Have `jq` and `python3` installed.
3. Create a json config file somewhere. **NOTE: This file should be readable only by root, since it will contain
   sensitive credentials for your DNS service.** The default location is `/etc/certbot-dns-namecom.config.json`,
	 but you can technically put it anywhere. If you do use a location other than the default one for your config
   file, you'll have to create a wrapper script that sets the `CERTBOT_DNS_NAMECOM_CONFIG` environment variable
	 like so:

```sh
#!/bin/bash

export CERTBOT_DNS_NAMECOM_CONFIG=/path/to/your/config.json  
/usr/bin/certbot-dns-namecom.py
```


## Usage

Once installed (and configured), all you have to do to issue a certificate is the following:

```sh
# First do a dry run to make sure it's going to work properly
certbot certonly --manual --manual-auth-hook /usr/bin/certbot-dns-namecom.py -d your-domain.com --agree-tos --email you@your-domain.com --dry-run

# Once that succeeds, you can do the real thing
certbot certonly --manual --manual-auth-hook /usr/bin/certbot-dns-namecom.py -d your-domain.com --agree-tos --email you@your-domain.com
```

