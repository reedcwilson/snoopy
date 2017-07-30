#!/usr/bin/env python

import os
import base64
import uuid
import zipfile
import httplib2

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Snoopy Collector'

user_id = 'me'
store_dir = 'HOME_DIRECTORY/screenshots'


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
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def unzip_files(zip_name, directory):
    zip_ref = zipfile.ZipFile(zip_name, 'r')
    num = 0
    for filename in zip_ref.namelist():
        if filename.endswith('.png'):
            part = zip_ref.read(filename)
            with open('{}/{}.png'.format(directory, uuid.uuid4()), 'wb') as f:
                f.write(part)
                num += 1
    zip_ref.close()
    os.remove(zip_name)
    return num


def download_attachments(service, user_id, msg_id, store_dir):
    num = 0
    try:
        message = service.users().messages().get(
            userId=user_id, id=msg_id).execute()
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
                    num += unzip_files(path, store_dir)
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


def collect(should_delete=True):
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
    print('downloaded {} attachments'.format(num))


def main():
    collect()


if __name__ == '__main__':
    main()
