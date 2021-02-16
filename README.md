# certbot-dns-name-com
A certbot DNS plugin for name.com  
Usage:  

check:  
    $ certbot-auto renew --cert-name yourdomain.com --manual-auth-hook /path/to/certbot_dns_auth.sh --dry-run

renew:  
    $ certbot-auto renew --cert-name yourdomain.com --manual-auth-hook /path/to/certbot_dns_auth.sh

