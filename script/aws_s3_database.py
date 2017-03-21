#!/usr/bin/env python
"""
    * PREREQUISITE
        $ pip install boto3

    * FEATURES

    * REFERENCE

    * FURTHER IMPROVEMENT

"""
import os
import sys
import argparse
import boto3
import logging

########################################################################################################################
#   SYSTEM PARAMETERS.

LOCAL_PATH = '/cloopin.ivs/database/'
# CLOOPIN_IVS_DB = '../db.sqlite3'
# CLOOPIN_IVS_DB_S3_PATH = 'database/test.txt'
LOCAL_CLOOPIN_IVS_DB = 'test.txt'
S3_CLOOPIN_IVS_DB = 'database/test.txt'

########################################################################################################################
#   LOCAL FUNCTIONS.


def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


def upload_db_to_s3():
    try:
        # Let's use Amazon S3...
        s3 = boto3.resource('s3')

        # Print all bucket names...
        for bucket in s3.buckets.all():
            print bucket.name

    except Exception as e:
        print e

    pass


def download_db_from_s3():
    bucket_name = 'bucket_name'
    # connect to the bucket
    conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)
    # go through the list of files
    bucket_list = bucket.list()
    for l in bucket_list:
        keyString = str(l.key)
        # check if file exists locally, if not: download it
        if not os.path.exists(LOCAL_PATH+keyString):
            l.get_contents_to_filename(LOCAL_PATH+keyString)

########################################################################################################################

if __name__ == "__main__":

    if len(sys.argv) == 1:
        sys.argv.extend(["-u"])

    parser = argparse.ArgumentParser(description="Amazon S3 upload and download of ivsearch database, db.sqlite3")
    parser.add_argument("-u", "--upload", dest="upload", default=False, action="store_true", help="Upload db.sqlite3")
    parser.add_argument("-d", "--download", dest="download", default=False, action="store_true",
                        help="Download db.sqlite3")
    args = parser.parse_args()

    if args.upload:
        upload_db_to_s3()
    elif args.download:
        download_db_from_s3()







