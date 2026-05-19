#!/usr/bin/env python3
import sys
import json
import urllib.request
import os
import time

ADMIN_USER = 'admin'
ADMIN_PASS = 'DSxBDPmnN5j4ftv'
REG_TOKEN = os.environ.get('HICLAW_REGISTRATION_TOKEN', 'c9626fa1fb15b3823b05d9ec94d750047c763447e2fe29f10c3ff5ba852f9bad')
BASE_URL = 'http://127.0.0.1:6167/_matrix/client/v3'
ADMIN_ROOM_ID = '!STjS5Mz5IdHsnAW5jA:matrix-local.hiclaw.io:58080'

def get_admin_token():
    req = urllib.request.Request(f'{BASE_URL}/login', data=json.dumps({
        'type': 'm.login.password',
        'identifier': {'type': 'm.id.user', 'user': ADMIN_USER},
        'password': ADMIN_PASS
    }).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['access_token']
    except Exception as e:
        print(f'Error logging in as admin: {e}')
        sys.exit(1)

def send_admin_room_cmd(cmd):
    token = get_admin_token()
    txn_id = f'txn_{int(time.time()*1000)}'
    url = f'{BASE_URL}/rooms/{ADMIN_ROOM_ID}/send/m.room.message/{txn_id}'
    req = urllib.request.Request(url, data=json.dumps({
        'msgtype': 'm.text',
        'body': f'@conduit:matrix-local.hiclaw.io:58080: {cmd}'
    }).encode('utf-8'), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }, method='PUT')
    try:
        with urllib.request.urlopen(req) as resp:
            pass
    except Exception as e:
        print(f'Error sending command to Admin Room: {e}')
        sys.exit(1)
        
    time.sleep(1.5)
    url_msg = f'{BASE_URL}/rooms/{ADMIN_ROOM_ID}/messages?dir=b&limit=5'
    req_msg = urllib.request.Request(url_msg, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req_msg) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for event in data['chunk']:
                if event['sender'] == '@conduit:matrix-local.hiclaw.io:58080' and event.get('content', {}).get('msgtype') in ['m.notice', 'm.text']:
                    print('\n' + event['content']['body'] + '\n')
                    return
            print('\nCommand sent successfully, but bot reply timed out. Please check Admin Room.\n')
    except Exception as e:
        print(f'Error fetching bot reply: {e}')

def create_user(username, password):
    req = urllib.request.Request(f'{BASE_URL}/register', data=json.dumps({
        'username': username,
        'password': password,
        'auth': {'type': 'm.login.registration_token', 'token': REG_TOKEN}
    }).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f'\nUser created successfully!\nUser ID: {data["user_id"]}\n')
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode('utf-8'))
        print(f'\nFailed to create user: {err.get("error", e)}\n')

def print_help():
    print('''
HiClaw User & Room Management CLI (hiclaw-mgr)
----------------------------------------------
Usage:
  hiclaw-mgr list                    - List all registered users
  hiclaw-mgr add <user> <pass>       - Create a new user
  hiclaw-mgr reset <user> <newpass>  - Reset user password
  hiclaw-mgr deactivate <user>       - Deactivate a user
  hiclaw-mgr list-rooms <user_id>    - List all rooms a user is in
  hiclaw-mgr force-join <user> <room>- Force join a user to a room
  hiclaw-mgr delete-room <room_id>   - Permanently delete a room from DB
''')

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'list':
        send_admin_room_cmd('users list-users')
    elif cmd == 'add':
        if len(sys.argv) < 4:
            print('Usage: hiclaw-mgr add <username> <password>')
            sys.exit(1)
        create_user(sys.argv[2], sys.argv[3])
    elif cmd == 'reset':
        if len(sys.argv) < 4:
            print('Usage: hiclaw-mgr reset <username> <newpassword>')
            sys.exit(1)
        send_admin_room_cmd(f'users reset-password {sys.argv[2]} {sys.argv[3]}')
    elif cmd == 'deactivate':
        if len(sys.argv) < 3:
            print('Usage: hiclaw-mgr deactivate <username>')
            sys.exit(1)
        send_admin_room_cmd(f'users deactivate {sys.argv[2]}')
    elif cmd == 'list-rooms':
        if len(sys.argv) < 3:
            print('Usage: hiclaw-mgr list-rooms <user_id>')
            sys.exit(1)
        send_admin_room_cmd(f'users list-joined-rooms {sys.argv[2]}')
    elif cmd == 'force-join':
        if len(sys.argv) < 4:
            print('Usage: hiclaw-mgr force-join <user_id> <room_id>')
            sys.exit(1)
        send_admin_room_cmd(f'users force-join-room {sys.argv[2]} {sys.argv[3]}')
    elif cmd == 'delete-room':
        if len(sys.argv) < 3:
            print('Usage: hiclaw-mgr delete-room <room_id>')
            sys.exit(1)
        send_admin_room_cmd(f'rooms delete-room -f {sys.argv[2]}')
    else:
        print(f'Unknown command: {cmd}')
        print_help()
        sys.exit(1)
