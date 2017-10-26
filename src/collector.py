#!/usr/bin/env python

import os
import base64
import zipfile
import httplib2
import shutil
import datetime

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from lib.file_finder import get_embedded_filename
from lib.secrets_manager import Crypt

try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('--path')
    parser.add_argument('--token')
    flags = parser.parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Snoopy Collector'

user_id = 'me'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'snoopy_collector.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(
            get_embedded_filename(CLIENT_SECRET_FILE),
            SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_path_parts(subject):
    colon = subject.index(':')
    return subject[:colon], subject[colon + 2:]


def ensure_directory(name, is_dir=False):
    if is_dir:
        os.makedirs(name)
    else:
        if not os.path.exists(os.path.dirname(name)):
            os.makedirs(os.path.dirname(name))


def fix_bad_zip_file(zipFile):
    with open(zipFile, 'r+b') as f:
        data = f.read()
        pos = data.rfind(b'\x50\x4b\x05\x06')  # End of central directory
        if (pos > 0):
            f.seek(pos + 20)  # size of 'ZIP end of central directory record'
            f.truncate()
            f.write(b'\x00\x00')


def open_zip(zip_name):
    try:
        return zipfile.ZipFile(zip_name, 'r')
    except zipfile.BadZipFile:
        fix_bad_zip_file(zip_name)
        return zipfile.ZipFile(zip_name, 'r')


def unzip_files(zip_name, directory, subject):
    num = 0
    try:
        with open_zip(zip_name) as zip_ref:
            for i, filename in enumerate(zip_ref.namelist()):
                if filename.endswith('.png'):
                    part = zip_ref.read(filename)
                    dev, name = get_path_parts(subject)
                    png = '{}/{}/{} - {}.png'.format(directory, dev, name, i)
                    ensure_directory(png)
                    with open(png, 'wb') as f:
                        f.write(part)
                        num += 1
    except zipfile.BadZipFile:
        pass
    os.remove(zip_name)
    return num


def get_body(message):
    plain_part = list(filter(
        lambda p: p['mimeType'] == 'text/plain',
        message['payload']['parts']))[0]
    return base64.b64decode(plain_part['body']['data']).decode()


def get_header(message, key):
    headers = list(filter(
        lambda h: h['name'] == key,
        message['payload']['headers']))
    return headers[0]['value'] if len(headers) == 1 else None


def log(subject, message, directory, device):
    filename = '{}/{}/_log.txt'.format(directory, device)
    ensure_directory(filename)
    with open(filename, 'a') as f:
        f.write('==============================\n')
        f.write('{}\n\n'.format(subject))
        f.write('{}\n'.format(message))
        f.write('==============================\n\n\n')


# TODO: putting this here for now -- you should probably make the collector
# into a class and store the crypt as a field
crypt = Crypt(flags.token)


def check_token(body):
    # assuming that the token is always appended to the body
    token = body[body.index('\ntoken:') + 8:]
    token = token[2:len(token) - 1]
    token = base64.b64decode(token.encode())
    return flags.token in crypt.decrypt(token)


def download_attachments(service, user_id, msg_id, store_dir):
    num = 0
    try:
        message = service.users().messages().get(
            userId=user_id, id=msg_id).execute()
        body = get_body(message)
        subject = get_header(message, 'Subject')
        device, remainder = get_path_parts(subject)
        if 'phone' not in device.lower() and not check_token(body):
            msg = 'ALERT! NO INSTALLATION TOKEN.\n'
            msg += 'body: {}'
            body = msg.format(body)
        log(remainder, body, store_dir, device)
        for part in message['payload']['parts']:
            if 'attachmentId' in part['body']:
                data = None
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(
                        userId=user_id,
                        messageId=msg_id,
                        id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = '/'.join([store_dir, 'a.zip'])
                with open(path, 'wb') as f:
                    f.write(file_data)
                    num += unzip_files(path, store_dir, subject)
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))
    return num


def get_messages_with_labels(service, user_id, label_ids=[]):
    try:
        response = service.users().messages().list(
            userId=user_id,
            labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(
                userId=user_id,
                labelIds=label_ids,
                pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def get_label_id(service, user_id, label_name):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    match = list(filter(lambda x: x['name'] == label_name, labels))
    return match[0]


def delete_message(service, user_id, msg_id):
    try:
        service.users().messages().delete(userId=user_id, id=msg_id).execute()
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def collect(store_dir, should_delete=True):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    label = get_label_id(service, user_id, 'Monitoring')
    messages = get_messages_with_labels(service, user_id, [label['id']])
    num = 0
    if not os.path.isdir(store_dir):
        os.makedirs(store_dir)
    for i, message in enumerate(messages):
        msg_id = message['id']
        num += download_attachments(service, user_id, msg_id, store_dir)
        if should_delete:
            delete_message(service, user_id, msg_id)
    time = str(datetime.datetime.now())
    print('{}: downloaded {} attachments'.format(time, num))


def remove_trash(trash_dir):
    shutil.rmtree(trash_dir, ignore_errors=True)


def main():
    if not flags.path:
        print("please provide a directory to store the images in")
        return
    trash_dir = '{}/_trash'.format(flags.path)
    remove_trash(trash_dir)
    ensure_directory(trash_dir, True)
    collect(flags.path)
    # collect(flags.path, False)


if __name__ == '__main__':
    main()
