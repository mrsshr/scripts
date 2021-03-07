#!/usr/bin/env python3

import sys
import subprocess
import requests
from datetime import datetime


def main(args):
    if len(args) < 2:
        print('usage: sync-cloudflare.py [output path]')
        return

    output = args[1]
    now = datetime.utcnow().isoformat()
    ips = []

    resp = requests.get('https://www.cloudflare.com/ips-v4')
    resp.raise_for_status()
    ips.extend([ip for ip in resp.text.strip().split('\n')])

    resp = requests.get('https://www.cloudflare.com/ips-v6')
    resp.raise_for_status()
    ips.extend([ip for ip in resp.text.strip().split('\n')])

    new_ips = '\n'.join(ips)

    try:
        with open('/tmp/cloudflare_origin_pulls.cache', 'r') as f:
            cached_ips = f.read()
    except FileNotFoundError:
        cached_ips = ''

    if new_ips == cached_ips:
        return

    lines = []
    lines.append('#')
    lines.append(f'# Cloudflare Origin Pulls ({now})')
    lines.append('#')
    lines.append('')

    for ip in ips:
        lines.append(f'set_real_ip_from {ip};')

    lines.append('')
    lines.append('real_ip_header CF-Connecting-IP;')
    lines.append('')

    content = '\n'.join(lines)

    with open(output, 'w') as f:
        f.write(content)

    print(content)

    subprocess.run(['/usr/sbin/nginx', '-t'], check=True)
    subprocess.run(['/usr/bin/systemctl', 'reload', 'nginx'], check=True)

    with open('/tmp/cloudflare_origin_pulls.cache', 'w') as f:
        f.write(new_ips)


if __name__ == '__main__':
    main(sys.argv)
