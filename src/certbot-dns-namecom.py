#!/usr/bin/env python3

import time
import os
import sys
import json
import requests


class NameComDNS:
    def __init__(self, username, token, domain_name):
        self.username = username
        self.token = token
        self.domain_name = domain_name

    def list_records(self):
        url = 'https://api.name.com/v4/domains/%s/records' % self.domain_name
        r = requests.get(url, auth=(self.username, self.token))

        return r.json()

    def create_record(self, data):
        url = 'https://api.name.com/v4/domains/%s/records' % self.domain_name
        r = requests.post(url, data=json.dumps(data), auth=(self.username, self.token))
        if r.status_code == 200 or r.status_code == 201:
            return r.json()
        else:
            raise Exception('name.com API %s Error: %s' % (r.status_code, r.content))

    def del_record(self, record_id):
        url = 'https://api.name.com/v4/domains/%s/records/%s' % (self.domain_name, record_id)
        r = requests.delete(url, data=data, auth=(self.username, self.token))

        print(r.json())


if __name__ == '__main__':

    # Get command line arguments
    cmd = sys.argv[0]
    if (cmd != "clean"):
        cmd = "add"

    # Get and validate environment variables
    certbot_domain = os.environ.get('CERTBOT_DOMAIN')
    certbot_validation = os.environ.get('CERTBOT_VALIDATION')
    if (certbot_domain is None):
        raise Exception('Expecting "CERTBOT_DOMAIN" environment variable to be set, but it wasn\'t.')
    if (certbot_validation is None):
        raise Exception('Expecting "CERTBOT_VALIDATION" environment variable to be set, but it wasn\'t.')

    # Create data object for API
    data = {
        'domainName': certbot_domain,
        'host': '_acme-challenge',
        'fqdn': '_acme-challenge.lonelyassistant.net',
        'type': 'TXT',
        'answer': certbot_validation,
        'ttl': 300,
    }

    # Get name.com credentials from config and validate
    conffile = os.environ.get('CERTBOT_DNS_NAMECOM_CONFIG') or "/etc/certbot-dns-namecom.config.json"
    if (not os.path.exists(conffile)):
        raise Exception('Expecting config file to exist at `' + conffile + '`, but it doesn\'t')
    f = open(conffile)
    config = json.load(f)
    f.close()

    username = config['namecom']['username']
    token = config['namecom']['token']
    waitsec = config.get('waitsec', 30)

    if (username is None):
        raise Exception("Missing field 'namecom.username' in config file")
    if (token is None):
        raise Exception("Missing field 'namecom.token' in config file")

    # Instantiate our class
    ncd = NameComDNS(username, token, certbot_domain)

    if cmd == 'add':
        # If we're adding a record, create it
        print("Adding records to name.com DNS")
        ncd.create_record(data)

    elif cmd == 'clean':
        # Otherwise, delete
        print("Deleting ACME records from name.com DNS")
        j = ncd.list_records()

        for record in j['records']:
            if record['host'] == '_acme-challenge':
                ncd.del_record(record['id'])

    if (waitsec != 0):
        print("Waiting %s seconds for DNS to propagate" % waitsec)
        time.sleep(waitsec)



