import logging
import configparser
import re
from datetime import datetime
from pyrogram import Client, Filters, InputPhoneContact, errors
from aiogram import Bot, Dispatcher, executor, types

config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config['credentials']['telegram-api'])
dp = Dispatcher(bot)

APP = Client(session_name="my_account", api_id=config['credentials']['pyrogram_api_id'],
             api_hash=config['credentials']['pyrogram_api_hash'])
APP.start()

def message_to_str(message):
    str_ = f'{datetime.now()} '
    if message["from"]["id"] == int(config["settings"]['owner_id']):
        str_ += f'from owner '
    elif "username" in message["from"]:
        str_ += f'from @{message["from"]["username"]} '
    elif 'first_name' in message["from"]:
        str_ += f'from {message["from"]["first_name"]} ({message["from"]["id"]}) '
    else:
        str_ += f'from {message["from"]["id"]} '
    if 'forward_from' in message:
        str_ += 'forwarded from '
        if "username" in message["forward_from"]:
            str_ += f'@{message["forward_from"]["username"]} '
        elif 'first_name' in message["forward_from"]:
            str_ += f'{message["forward_from"]["first_name"]} ({message["forward_from"]["id"]}) '
        else:
            str_ += f'{message["forward_from"]["id"]} '
    elif 'forward_sender_name' in message:
        str_ += f'forwerded from {message["forward_sender_name"]} '
    str_ += f'with "{message["text"]}"'
    return str_


def user_to_str(user):
    if user:
        str_ = 'get user: '
        if user.username:
            str_ += f'@{user["username"]}'
        elif user.first_name:
            str_ += f'{user["first_name"]} ({user["id"]})'
        else:
            str_ += f'{user["id"]}'
        return str_
    else:
        return ' ';


def user_info_from_message(message):
    if message and 'from' in message:
        str_ = 'This user info\n'
        if 'first_name' in message['from']:
            str_ += f'First name: {message["from"]["first_name"]}\n'
        if 'last_name' in message['from']:
            str_ += f'Last name: {message["from"]["last_name"]}\n'
        if 'username' in message['from']:
            str_ += f'Username: @{message["from"]["username"]}\n'
        if 'id' in message['from']:
            str_ += f'id: <code>{message["from"]["id"]}</code>\n'
        if message['chat']['id'] < 0:
            str_ += f'chat id:<code>{message["chat"]["id"]}</code>\n'
        return str_
    else:
        return ' ';


def user_info_from_user(user, from_channel: bool = False):
    if user and not from_channel:
        str_ = 'This user info\n'
        if user.first_name:
            str_ += f'First name: {user["first_name"]}\n'
        if user.last_name:
            str_ += f'Last name: {user["last_name"]}\n'
        if user.username:
            str_ += f'Username: @{user["username"]}\n'
        if user.id:
            str_ += f'id: <code>{user["id"]}</code>\n'
        return str_
    elif from_channel:
        str_ = 'This channel info\n'
        if user.chat.title:
            str_ += f'Title: {user.chat.title}\n'
        if user.chat.id:
            str_ += f'id: <code>{user.chat.id}</code>\n'
        return str_
    else:
        return ' ';


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Hello, i will help you with geting user's info by id, telephone, telegram username and etc., type <b>/help</b> for more info",
        parse_mode='html')


@dp.message_handler(commands=['help'])
async def send(message: types.Message):
    str_ = f"<b>/get_me</b> - get my info\n" \
                f"type telephone in +YXXXXXXXXXX format to get user by telephone\n" \
                f"type username in @XXXXXXXXXX format to get user by username\n" \
                f"type id in XXXX format to get user by id\n" \
                f"forward message to get origin sender user"
    await message.answer(str_, parse_mode='html')


@dp.message_handler(commands=['get_me'])
async def send(message: types.Message):
    await message.answer(user_info_from_message(message), parse_mode='html')


@dp.channel_post_handler(lambda x: "text" in x and x.text == "/get_me")
async def send(message: types.Message):
    await message.answer(user_info_from_user(message, True), parse_mode="html")


@dp.message_handler(commands=['about'])
async def send(message: types.Message):
    await message.answer(
        "Bot by @teadove, power by pyrogram and aoigram, best python telegram bot wrappers!\nSourse code: https://gitlab.com/TeaDove/get_useridbot\n(i'm not into licencing, so you can do anything with my code)\nIf you wanna help me, send some money to <code>4276380030569342</code>",
        parse_mode='html')


@dp.message_handler(lambda message: "forward_from" in message and message["forward_from"]["is_bot"] is False)
async def send(message: types.Message):
    str_ = message_to_str(message)
    await message.answer(f'Start searching for user by <b>forwarded message</b>', parse_mode='html')
    try:
        user = APP.get_users(message["forward_from"]["username"])
    except errors.exceptions.flood_420.FloodWait as e:
        await message.answer(
            f'Sorry, you should wait some time before using me because of telegram flood control. Wait for {str(e).split()[5]} seconds. My developers will do their best, to come over this problem.',
            parse_mode='html')
    except:
        await message.answer('Something went wrong!', parse_mode='html')
    else:
        str_ += ' ' + user_to_str(user)
        await message.answer(user_info_from_user(user), parse_mode='html')

@dp.message_handler(regexp='^\d+$')
async def send(message: types.Message):
    str_ = message_to_str(message)
    await message.answer(f'Start seariching for user by this <b>id</b>: {message.text}', parse_mode='html')
    try:
        user = APP.get_users(message.text[0:13])
    except errors.exceptions.flood_420.FloodWait:
        await message.answer(
            f'Sorry, you should wait some time before using me because of telegram flood control. Wait for {str(e).split()[5]} seconds. My developers will do their best, to come over this problem.',
            parse_mode='html')
    except:
        await message.answer('No user with this id\nor telegram blocks me from this user', parse_mode='html')
    else:
        str_ += " " + user_to_str(user)
        await message.answer(user_info_from_user(user), parse_mode='html')


@dp.message_handler(regexp='^@[A-z][A-z0-9_]{4,31}$')
async def send(message: types.Message):
    str_ = message_to_str(message)
    await message.answer(f'Start seariching for user by this <b>username</b>: {message.text}', parse_mode='html')
    try:
        user = APP.get_users(message.text[1:34])
    except errors.exceptions.flood_420.FloodWait as e:
        await message.answer(
            f'Sorry, you should wait some time before using me because of telegram flood control. Wait for {str(e).split()[5]} seconds. My developers will do their best, to come over this problem.',
            parse_mode='html')
    except errors.exceptions.UsernameNotOccupied:
        await message.answer(f'No user with this username', parse_mode='html')
    else:
        str_ += " " + user_to_str(user)
        await message.answer(user_info_from_user(user), parse_mode='html')


@dp.message_handler(regexp='^\+\d{11,15}$')
async def send(message: types.Message):
    str_ = message_to_str(message)
    await message.answer(f'Start searching for user by this <b>number</b>: {message.text}', parse_mode='html')
    try:
        APP.add_contacts([InputPhoneContact(message.text[1:17], "FromGet_useridbot")])
        user = APP.get_users(message.text[1:17])
        userId = user.id
        APP.delete_contacts([message.text[1:17]])
        user = APP.get_users(
            userId)  # Why this hard? Cause if we will simply try get users info from number, we wont be able get his real first and second names
    except errors.exceptions.flood_420.FloodWait as e:
        await message.answer(
            f'Sorry, you should wait some time before using me because of telegram flood control. Wait for '
            f'{str(e).split()[5]} seconds. My developers will do their best, to come over this problem.',
            parse_mode='html')
    except:
        await message.answer('No user with this phone number or his account cannot be found with phone number',
                             parse_mode='html')
    else:
        str_ += " " + user_to_str(user)
        await message.answer(user_info_from_user(user), parse_mode='html')


@dp.message_handler()
async def send(message: types.Message):
    await message.answer("You have typed something in wrong format:(")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
