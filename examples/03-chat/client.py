#!/usr/bin/env python

import time
import threading

from string import printable
from blessed import Terminal
from sickserv import SickServWSClient, set_init_key

set_init_key('yellow-submarine')
ssc = SickServWSClient('127.0.0.1', port=1337)
ssc.subscribe(endpoint='init')
ssc.send({'endpoint': 'init'})
ssc.subscribe(endpoint='send')
ssc.subscribe(endpoint='queue')

term = Terminal()

def draw_prompt():
    with term.location(0, term.height):
        print('> ' + ' '*(term.width-2), end='')

def recv_chat():
    M = 1
    while True:
        ssc.send({'endpoint': 'queue', 'a':'b'})
        response = ssc.recv('queue')
        if not response:
            time.sleep(1)
            continue
        with term.location(0, M):
            for r in response:
                print(r['sysid'] + ': ' + r['message'])
                M += 1

rt = threading.Thread(target=recv_chat)
rt.daemon = True
rt.start()

def main():
    msg = ''
    msglen = 2
    draw_prompt()

    while True:
        with term.cbreak():
            user_input = term.inkey()

        if repr(user_input) == 'KEY_ENTER':
            payload = {'endpoint': 'send', 'message': msg}
            ssc.send(payload)
            msg = ''
            msglen = 2
            draw_prompt()
            continue

        if repr(user_input) == 'KEY_DELETE':
            with term.location(msglen-1, term.height):
                print(' ', end='')
            msg = msg[:-1]
            msglen -= 1
            continue

        if user_input in list(printable):
            with term.location(msglen, term.height):
                print(user_input, end='')
                msg += user_input
                msglen += 1

if __name__ == '__main__':
    main()