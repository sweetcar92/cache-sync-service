#!/usr/bin/env python3
"""
Sync service: Uploads data output files to Google Drive using OAuth 2.0.
Keeps only the 2 most recent files per dataset prefix.
"""

import os
import sys
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def get_drive_service(client_id, client_secret, refresh_token):
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    credentials.refresh(Request())
    return build('drive', 'v3', credentials=credentials)


def upload_file(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, mimetype='application/epub+zip', resumable=True)
    file_metadata = {'name': file_name, 'parents': [folder_id]}

    print(f"Uploading: {file_name}")
    created = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, createdTime'
    ).execute()
    print(f"   Uploaded (ID: {created['id']})")
    return created['id']


def cleanup_old_files(service, folder_id, prefix, keep=2):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        spaces='drive',
        orderBy='createdTime desc',
        fields='files(id, name, createdTime)'
    ).execute()

    all_files = [f for f in results.get('files', []) if f['name'].startswith(prefix)]

    print(f"\nCleaning prefix {prefix}*: {len(all_files)} file(s) found")
    to_delete = all_files[keep:]
    if to_delete:
        for f in to_delete:
            service.files().delete(fileId=f['id']).execute()
            print(f"   Deleted: {f['name']}")
    else:
        print(f"   No cleanup required")


if __name__ == '__main__':
    folder_id     = os.environ.get('GDRIVE_FOLDER_ID')
    client_id     = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    target_files_str = os.environ.get('TARGET_FILES', '')

    missing = [k for k, v in {
        'GDRIVE_FOLDER_ID': folder_id,
        'GOOGLE_CLIENT_ID': client_id,
        'GOOGLE_CLIENT_SECRET': client_secret,
        'GOOGLE_REFRESH_TOKEN': refresh_token,
        'TARGET_FILES': target_files_str
    }.items() if not v]

    if missing:
        print(f"Error: Missing variables: {', '.join(missing)}")
        sys.exit(1)

    target_files = [f.strip() for f in target_files_str.split(',') if f.strip()]
    existing = [f for f in target_files if os.path.exists(f)]

    if not existing:
        print("Error: No target files found to upload.")
        sys.exit(1)

    service = get_drive_service(client_id, client_secret, refresh_token)

    prefixes_uploaded = []
    for f_path in existing:
        upload_file(service, f_path, folder_id)
        name = os.path.basename(f_path)
        match = re.match(r'^(.+?)_\d{4}-\d{2}-\d{2}_', name)
        prefix = match.group(1) + '_' if match else name[:10]
        prefixes_uploaded.append(prefix)

    print("\n--- Cleaning old files ---")
    for prefix in set(prefixes_uploaded):
        cleanup_old_files(service, folder_id, prefix, keep=2)

    print("\nFinished!")
