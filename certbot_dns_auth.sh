#!/bin/bash
paction=$1

if [[ "$paction" != "clean" ]]; then
	paction="add"
fi

pythoncmd="/path/to/venv/bin/python3"

echo $CERTBOT_DOMAIN
echo $CERTBOT_VALIDATION

$pythoncmd '/path/to/name_com_dns.py' $paction $CERTBOT_DOMAIN $CERTBOT_VALIDATION >>"/var/log/certd.log"

if [[ "$paction" == "add" ]]; then
        # DNS TXT f
        /bin/sleep 40
fi
