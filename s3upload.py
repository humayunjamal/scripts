#!/usr/bin/env python
import boto,boto.iam
import yaml
import csv
import datetime
import os
import collections
import urllib
import json
import sys
# you need to pip install pyCLI
from cli.log import LoggingApp
from pprint import pprint
import boto.exception
from boto.s3.key import Key

__author__ = 'humayun.jamal'

 


class S3pullpush(LoggingApp):


    def upload_file(self, bucket):
        self.log.debug("upload_file() ")   
        self.log.info("Uploading  \"%s\" TO s3 bucket \"%s\"" % (self.params.file, self.params.bucket))
        s3file = self.params.file
        s3bucket = self.params.bucket

        k = Key(bucket)
        k.key = s3file
        fileuploadedSize = k.set_contents_from_filename(s3file)
        if os.path.getsize(self.params.file) == fileuploadedSize:
            print "The file was uploaded successfully as both uploaded and local file size are Same"
        else:
            print "The file upload was not successfull as both uploaded and local file size do not match"



    def check_file(self, bucket):
        self.log.info("Checking File \"%s\" if it already exists" % self.params.file)
        bucket_list = bucket.list()
        for l in bucket_list:
            keyString = str(l.key)
            if self.params.file == keyString:
                print "The File already exist on S3 bucket"
                print "The S3 uploaded File size is "
                print l.size
                print "The Local File Size is"
                print os.path.getsize(self.params.file)
                if l.size == os.path.getsize(self.params.file):
                    print "There is no need to upload or upload of the file was successfull"
                    return True 


    def get_bucket(self, c):
        self.log.info("Get Bucket")
        s3bucket = self.params.bucket
        try:
            b = c.get_bucket(s3bucket)
            print 'The bucket exists and you can access it.'
        except Exception, ex:
            print "The bucket Specified either does not exist or this host does not have permission to access it. Please check"
            print ex.error_message
            sys.exit()
        return b

 


    def main(self):
        if self.params.dry_run is True:
		self.log.info("************* DRY RUN - NO CHANGES WILL BE MADE ***********")

        self.dryrunprefix = "DRYRUN NO CHANGE: " if self.params.dry_run else ""

        self.log.info("connecting to ec2 region %s" % self.params.region) 

        c = None
        if not self.params.access_key and not self.params.secret_key:
            # try and do an instance role conx
            c = boto.connect_s3()
        else:
            # use the command line creds to connect
            c = boto.ec2.connect_to_region(self.params.region,
                                       aws_access_key_id=self.params.access_key,
                                       aws_secret_access_key=self.params.secret_key)

        self.log.debug("Connection: %s" % c)
        if not c:
            self.log.error("No connection could be established - aborting")
            sys.exit()

        if self.params.file is not None:
            bucket = self.get_bucket(c)
            if not self.check_file(bucket):
                self.log.info("The file does not exist hence uploading file")
                self.upload_file(bucket)
                if self.params.erase:
                    self.log.info("Erasing Local file after successfull upload")
                    os.remove(self.params.file)

        self.log.info("Finished")
        


if __name__ == "__main__":

    creator=S3pullpush(name="S3PP", description="""
Upload or Download files to Specified s3 bucket using Host IAM role access policy , to check current system role name , please curl curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
""")
    creator.add_param("-k", "--access-key", help="aws access key", default=False, required=False, action="store")
    creator.add_param("-w", "--secret-key", help="aws secret key", default=False, required=False, action="store")
    creator.add_param("-r", "--region", help="aws region", default=False, required=False, action="store")
    creator.add_param("-f", "--file", help="File to upload", required=True, action="store")
    creator.add_param("-b", "--bucket", help="S3 bucket name to upload the file to", required=True, action="store")
    creator.add_param("-d", "--dry-run", help="Doesnt make changes but only shows what will be changed", default=False, action="store_true")
    creator.add_param("-e", "--erase", help="Erase local file once uploaded", default=False, action="store_true")
    creator.run()
    
