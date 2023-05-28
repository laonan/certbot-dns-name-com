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

    def get_base_domain(self):
        url = 'https://api.name.com/v4/domains/%s' % self.domain_name
        r = requests.get(url, auth=(self.username, self.token))

        return r.json()['domainName']

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

        if r.status_code == 200 or r.status_code == 201:
            print("Record %s successfully deleted" % (record_id))
        else:
            raise Exception('name.com API %s Error: %s' % (r.status_code, r.content))


if __name__ == '__main__':

    # Get command line arguments
    cmd = sys.argv[1]
    if (cmd != "clean"):
        cmd = "add"

    # Get and validate environment variables
    certbot_domain = os.environ.get('CERTBOT_DOMAIN')
    certbot_validation = os.environ.get('CERTBOT_VALIDATION')
    if (certbot_domain is None):
        raise Exception('Expecting "CERTBOT_DOMAIN" environment variable to be set, but it wasn\'t.')
    if (certbot_validation is None):
        raise Exception('Expecting "CERTBOT_VALIDATION" environment variable to be set, but it wasn\'t.')

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

    base_domain = ncd.get_base_domain()
    subdomain = certbot_domain.partition(base_domain)[0].rstrip('.')
    host = ("_acme-challenge." + subdomain).rstrip('.')

    # Create data object for API
    data = {
        'domainName': certbot_domain,
        'host': host,
        'fqdn': f'_acme-challenge.{certbot_domain}',
        'type': 'TXT',
        'answer': certbot_validation,
        'ttl': 300,
    }

    if cmd == 'add':
        # If we're adding a record, create it
        print("Adding records to name.com DNS")
        ncd.create_record(data)

    elif cmd == 'clean':
        # Otherwise, delete
        print("Deleting ACME records from name.com DNS")
        j = ncd.list_records()

        for record in j['records']:
            if 'host' in record:
                if record['host'].startswith('_acme-challenge') and record['answer'] == certbot_validation:
                    ncd.del_record(record['id'])

    if (waitsec != 0):
        print("Waiting %s seconds for DNS to propagate" % waitsec)
        time.sleep(waitsec)



