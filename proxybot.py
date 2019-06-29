# MIT License

# Copyright (c) 2019 Ranx

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# Version: 0.0.1

import json
import logging
from logging.handlers import RotatingFileHandler
import sys

import telebot

CFG_PATH = 'config.json'
def load_config(file_name):
    with open(file_name, encoding='utf-8') as f:
        return json.load(f)
cfg = load_config(CFG_PATH)

logger = logging.getLogger(__name__)
NO_FORWARD_PREFIX_CHARS = '!#$&*+<=>-~'
CONTENT_TYPES = ['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'contact']

tb = telebot.TeleBot(cfg['token'])


def user_access_handler(msg):
    return msg.from_user.id in cfg['users'].values() or msg.from_user.id in cfg['admins'].values()


def admin_access_handler(msg):
    return msg.from_user.id in cfg['admins'].values()


# // Bot handlers //

@tb.message_handler(commands=['groups'], func=user_access_handler)
def handle_groups(message):
    groups_list = []
    for i, group_id in enumerate(cfg['groups']):
        try:
            group_name = getattr(tb.get_chat(group_id), 'title', 'Unknown group')
        except telebot.apihelper.ApiException:
            group_name = '/ Failed to retrieve group info /'
        groups_list.append('{}[{}] {} ({})'.format(
            '> ' if group_id == cfg['current_group'] else '',
            i,
            group_name,
            group_id
        ))
    tb.send_message(message.chat.id, 'Groups:\n' + '\n'.join(groups_list))


@tb.message_handler(commands=['switchgroup'], func=user_access_handler)
def handle_switch_group(message):
    params = message.text.split(' ')
    if len(params) != 2:
        tb.send_message(message.chat.id, '*Usage:* /switchgroup <index>', parse_mode='Markdown')
        return
    if params[1].strip().lower() == 'none':
        cfg['current_group'] = None
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'Reset current group')
        return
    try:
        cfg['current_group'] = cfg['groups'][int(params[1])]
    except (ValueError, IndexError):
        tb.send_message(message.chat.id, 'Incorrect group index')
    else:
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'Current group: ' + getattr(try_get_chat(cfg['current_group']), 'title', 'Unknown group'))


@tb.message_handler(commands=['addgroup'], func=admin_access_handler)
def handle_add_group(message):
    params = message.text.split(' ')
    if len(params) != 2:
        tb.send_message(message.chat.id, '*Usage:* /addgroup <group\\_id>', parse_mode='Markdown')
        return
    try:
        group_id = int(params[1])
        chat = tb.get_chat(group_id)
        if chat.type not in ('group', 'supergroup'):
            raise ValueError
        if group_id in cfg['groups']:
            tb.send_message(message.chat.id, 'Group have been added already')
            return
        cfg['groups'].append(group_id)
    except (ValueError, telebot.apihelper.ApiException):
        tb.send_message(message.chat.id, 'Incorrect group id')
    else:
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'Added {} to group list'.format(getattr(chat, 'title', 'Unknown group')))


@tb.message_handler(commands=['removegroup'], func=admin_access_handler)
def handle_remove_group(message):
    params = message.text.split(' ')
    if len(params) != 2:
        tb.send_message(message.chat.id, '*Usage:* /removegroup <index>', parse_mode='Markdown')
        return
    try:
        group_index = int(params[1])
        if cfg['current_group'] == cfg['groups'][group_index]:
            cfg['current_group'] = None
        del cfg['groups'][group_index]
    except (ValueError, IndexError):
        tb.send_message(message.chat.id, 'Incorrect group index')
    else:
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'Group #{} was removed'.format(group_index))


@tb.message_handler(commands=['users'], func=user_access_handler)
def handle_users(message):
    users_list = '\n'.join(['{} - {}'.format(
        alias, user_id
    ) for alias, user_id in cfg['users'].items()])
    tb.send_message(message.chat.id, 'Users:\n' + users_list)


@tb.message_handler(commands=['adduser'], func=admin_access_handler)
def handle_add_user(message):
    params = message.text.split(' ')
    if len(params) != 3:
        tb.send_message(message.chat.id, '*Usage:* /adduser <user\\_id> <alias>', parse_mode='Markdown')
        return
    if not params[2].isalnum():
        tb.send_message(message.chat.id, 'Only letters and digits are allowed in the alias')
        return
    try:
        user_id = int(params[1])
        chat = tb.get_chat(user_id)
        if not chat.type == 'private':
            raise ValueError
        if user_id in cfg['users'].values():
            tb.send_message(message.chat.id, 'User have been added already')
            return
        cfg['users'][params[2]] = user_id
    except (ValueError, telebot.apihelper.ApiException):
        tb.send_message(message.chat.id, 'Incorrect user id')
    else:
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'User {} was added'.format(params[2]))


@tb.message_handler(commands=['removeuser'], func=admin_access_handler)
def handle_remove_user(message):
    params = message.text.split(' ')
    if len(params) != 2:
        tb.send_message(message.chat.id, '*Usage:* /removeuser <alias>', parse_mode='Markdown')
        return
    try:
        del cfg['users'][params[1]]
    except KeyError:
        tb.send_message(message.chat.id, 'User not found')
    else:
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'User {} was removed'.format(params[1]))


@tb.message_handler(commands=['noforwardprefix'], func=user_access_handler)
def handle_no_forward_prefix(message):
    params = message.text.split(' ')
    if len(params) < 2:
        cfg['no_forward_prefix'] = None
        save_config(cfg, CFG_PATH)
        tb.send_message(message.chat.id, 'Disabled no forward prefix')
        return

    prefix = ' '.join(params[1:]).strip()
    if not all([c in NO_FORWARD_PREFIX_CHARS for c in prefix]):
        tb.send_message(message.chat.id, 'Incorrect prefix, allowed characters:\n' + NO_FORWARD_PREFIX_CHARS)
        return

    cfg['no_forward_prefix'] = prefix
    save_config(cfg, CFG_PATH)
    tb.send_message(message.chat.id, 'Set no forward prefix to ' + prefix)


@tb.message_handler(commands=['getid'])
def handle_get_id(message):
    tb.send_message(message.chat.id, '*Chat ID:* ' + str(message.chat.id), parse_mode='Markdown')


@tb.message_handler(func=lambda msg: msg.chat.type == 'private' and msg.chat.id in cfg['users'].values(), content_types=CONTENT_TYPES)
def handle_private_messages(message):
    for target_chat in ((cfg['current_group'],) if cfg['current_group'] is not None else ()) + tuple(cfg['users'].values()):
        if target_chat == message.chat.id:
            continue
        try:
            if message.content_type == 'sticker':
                sender_name = getattr(message.from_user, 'username', None) or \
                    (getattr(message.from_user, 'first_name', None) or '') + (getattr(message.from_user, 'last_name', None) or '') or 'Unknown user'
                tb.send_message(target_chat, 'Sticker by ' + sender_name)
            if cfg['no_forward_prefix'] is not None and message.content_type == 'text' and message.text.startswith(cfg['no_forward_prefix']):
                tb.send_message(target_chat, message.text)
            else:
                forwarded = tb.forward_message(target_chat, message.chat.id, message.message_id)
                if not isinstance(forwarded, telebot.types.Message):
                    log.warning('Message failed to forward:\n\n{}\n\n'.format(forwarded))
        except telebot.apihelper.apihelper as e:
            log.warning('Failed to send API request:\n' + repr(e))


@tb.message_handler(func=lambda msg: msg.chat.type in ('group', 'supergroup') and msg.chat.id in cfg['groups'], content_types=CONTENT_TYPES)
def handle_group_messages(message):
    for user in cfg['users'].values():
        try:
            if message.content_type == 'sticker':
                sender_name = getattr(message.from_user, 'username', None) or \
                    (getattr(message.from_user, 'first_name', None) or '') + (getattr(message.from_user, 'last_name', None) or '') or 'Unknown user'
                tb.send_message(user, 'Sticker by ' + sender_name)
            forwarded = tb.forward_message(user, message.chat.id, message.message_id)
            if not isinstance(forwarded, telebot.types.Message):
                log.warning('Message failed to forward:\n\n{}\n\n'.format(forwarded))
        except telebot.apihelper.ApiException as e:
            log.warning('Failed to send API request:\n' + repr(e))


def try_get_chat(chat_id):
    try:
        return tb.get_chat(chat_id)
    except telebot.apihelper.ApiException:
        return None


def save_config(cfgobj, file_name):
    with open(file_name, mode='w', encoding='utf-8') as f:
        json.dump(cfgobj, f, indent=4)
 

def error_handler(exctype, value, tb):
    logger.error('An error has occurred.', exc_info=(exctype, value, tb))


def main():
    # Initialize logger
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler('proxybot.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(levelname)s - [%(asctime)s] %(filename)s[L:%(lineno)d] %(message)s'))
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    sys.excepthook = error_handler

    if 'current_group' not in cfg:
        cfg['current_group'] = None
        save_config(cfg, CFG_PATH)

    logger.info('Bot started')

    try:
        tb.polling(none_stop=True)
    except (KeyboardInterrupt, EOFError, SystemExit):
        tb.stop_bot()
    logger.info('Bot stopped')


if __name__ == '__main__':
    main()
