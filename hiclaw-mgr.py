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

HUMANS_REGISTRY = '/root/hiclaw-fs/agents/manager/humans-registry.json'
WORKERS_REGISTRY = '/root/hiclaw-fs/agents/manager/workers-registry.json'

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

def load_json(path, default_struct):
    if not os.path.exists(path):
        return default_struct
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return default_struct

def save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {path}")
    except Exception as e:
        print(f"Error saving {path}: {e}")

def list_registry(reg_type):
    if reg_type == 'humans':
        data = load_json(HUMANS_REGISTRY, {"version": 1, "updated_at": "", "humans": {}})
        print(f"\n=== Humans Registry (Total: {len(data.get('humans', {}))}) ===")
        for hid, info in data.get('humans', {}).items():
            print(f"ID: {hid:<12} | Matrix: {info.get('matrix_user_id', ''):<38} | Name: {info.get('display_name', ''):<15} | Perm: {info.get('permission_level', 1)}")
        print()
    elif reg_type == 'workers':
        data = load_json(WORKERS_REGISTRY, {"version": 1, "updated_at": "", "workers": {}})
        print(f"\n=== Workers Registry (Total: {len(data.get('workers', {}))}) ===")
        for wid, info in data.get('workers', {}).items():
            print(f"ID: {wid:<12} | Matrix: {info.get('matrix_user_id', ''):<38} | Name: {info.get('display_name', ''):<15} | Status: {info.get('status', 'online')}")
        print()

def add_human(hid, matrix_id, name, perm):
    data = load_json(HUMANS_REGISTRY, {"version": 1, "updated_at": "", "humans": {}})
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    data['updated_at'] = now
    if 'humans' not in data:
        data['humans'] = {}
    data['humans'][hid] = {
        "matrix_user_id": matrix_id,
        "display_name": name,
        "permission_level": int(perm),
        "created_at": data['humans'].get(hid, {}).get('created_at', now)
    }
    save_json(HUMANS_REGISTRY, data)

def add_worker(wid, matrix_id, name, status):
    data = load_json(WORKERS_REGISTRY, {"version": 1, "updated_at": "", "workers": {}})
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    data['updated_at'] = now
    if 'workers' not in data:
        data['workers'] = {}
    data['workers'][wid] = {
        "matrix_user_id": matrix_id,
        "display_name": name,
        "status": status,
        "created_at": data['workers'].get(wid, {}).get('created_at', now)
    }
    save_json(WORKERS_REGISTRY, data)

def remove_registry(reg_type, item_id):
    path = HUMANS_REGISTRY if reg_type == 'humans' else WORKERS_REGISTRY
    data = load_json(path, {"version": 1, "updated_at": "", reg_type: {}})
    if reg_type in data and item_id in data[reg_type]:
        del data[reg_type][item_id]
        data['updated_at'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        save_json(path, data)
        print(f"Successfully removed {item_id} from {reg_type} registry.")
    else:
        print(f"ID {item_id} not found in {reg_type} registry.")

def print_help():
    print('''
HiClaw User, Worker & Room Management CLI (hiclaw-mgr)
------------------------------------------------------
Matrix Core Commands:
  hiclaw-mgr list                    - List all registered users in Matrix DB
  hiclaw-mgr add <user> <pass>       - Create a new user in Matrix DB
  hiclaw-mgr reset <user> <newpass>  - Reset user password in Matrix DB
  hiclaw-mgr deactivate <user>       - Deactivate a user in Matrix DB

OpenClaw Registry Commands (Humans & Workers):
  hiclaw-mgr list-humans             - List human users in humans-registry.json
  hiclaw-mgr list-workers            - List agent workers in workers-registry.json
  hiclaw-mgr add-human <id> <matrix_id> <name> [perm] - Add/update human in registry
  hiclaw-mgr add-worker <id> <matrix_id> <name> [status] - Add/update worker in registry
  hiclaw-mgr remove-human <id>       - Remove human from registry
  hiclaw-mgr remove-worker <id>      - Remove worker from registry

Room Governance Commands:
  hiclaw-mgr list-rooms <user_id>    - List all rooms a user is in
  hiclaw-mgr force-join <user> <room>- Force join a user to a room
  hiclaw-mgr delete-room <room_id>   - Permanently delete a room from Matrix DB
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
    elif cmd == 'list-humans':
        list_registry('humans')
    elif cmd == 'list-workers':
        list_registry('workers')
    elif cmd == 'add-human':
        if len(sys.argv) < 5:
            print('Usage: hiclaw-mgr add-human <id> <matrix_user_id> <display_name> [perm_level]')
            sys.exit(1)
        perm = sys.argv[5] if len(sys.argv) > 5 else 1
        add_human(sys.argv[2], sys.argv[3], sys.argv[4], perm)
    elif cmd == 'add-worker':
        if len(sys.argv) < 5:
            print('Usage: hiclaw-mgr add-worker <id> <matrix_user_id> <display_name> [status]')
            sys.exit(1)
        status = sys.argv[5] if len(sys.argv) > 5 else 'online'
        add_worker(sys.argv[2], sys.argv[3], sys.argv[4], status)
    elif cmd == 'remove-human':
        if len(sys.argv) < 3:
            print('Usage: hiclaw-mgr remove-human <id>')
            sys.exit(1)
        remove_registry('humans', sys.argv[2])
    elif cmd == 'remove-worker':
        if len(sys.argv) < 3:
            print('Usage: hiclaw-mgr remove-worker <id>')
            sys.exit(1)
        remove_registry('workers', sys.argv[2])
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
