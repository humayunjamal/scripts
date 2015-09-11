#!/usr/bin/env python
import boto,boto.iam,boto.utils
import yaml
import csv
import datetime
import os
import collections
import urllib
import json
import sys
import time
# you need to pip install pyCLI
from cli.log import LoggingApp
from pprint import pprint
import boto.ec2.autoscale
from boto.ec2.elb import ELBConnection
from boto import regioninfo
from boto import ec2
from datetime import datetime
from datetime import timedelta

__author__ = 'humayun.jamal'




class AutomatedSnapShot(LoggingApp):


    def get_attached_vol(self, c):

        print inst_id
        vols = c.get_all_volumes(filters={'attachment.instance-id': inst_id})
        return vols



    def make_snapshots(self, c, vols):
        for vol in vols:
            desc = self.snapshot_description(vol, inst_id, today)
            snap = c.create_snapshot(vol.id, description=desc)
            snap.add_tag('Name', inst_id+"-snapshot-"+vol.id)
            while snap.status != 'completed':
                snap.update()
                print "The SnapShot-ID : %s Status is : %s @ %s" % (snap.id, snap.status, datetime.now())
            time.sleep(5)
            if snap.status == 'completed':
                print snap.id + ' is complete.'
                break


    def snapshot_description(self, volume, instance_id, date):
        return "Snapshot-%s-Instance-%s-On-%s" % (volume.id, instance_id, date)


    def snapshot_retention (self, c, vols):
        for vol in vols:
            desc = self.snapshot_description(vol, inst_id, four_weeks_ago)
            self.log.info("The Desciption of Four weeks ago snapshot we are looking for is %s" % desc)
            four_weeks_ago_snapshot = c.get_all_snapshots(filters = {"description": desc})

            for snap in four_weeks_ago_snapshot:
                print "Found snapshot %s older then four weeks which will now be deleted" % snap.id
                try:
            #delete snapshot
                    c.delete_snapshot(snap.id)
                except:
                    print "no snapshot four weeks ago to delete!"





    def main(self):
        if self.params.dry_run is True:
            self.log.info("************* DRY RUN - NO CHANGES WILL BE MADE ***********")

            self.dryrunprefix = "DRYRUN NO CHANGE: " if self.params.dry_run else ""

        self.log.info("connecting to ec2 region %s" % self.params.region)

        global now, today, four_weeks_ago, inst_id
        now = datetime.now()
        today = now.date()
        four_weeks_ago = (today - timedelta(days=28))
        inst_id = boto.utils.get_instance_metadata()['instance-id']

        print "Four weeks ago tIme = %s" % four_weeks_ago


        if not self.params.access_key and not self.params.secret_key:
            # try and do an instance role conx
            c = boto.ec2.connect_to_region(self.params.region)
        else:
            # use the command line creds to connect
            c = boto.ec2.connect_to_region(self.params.region,
                                       aws_access_key_id=self.params.access_key,
                                       aws_secret_access_key=self.params.secret_key)



        self.log.debug("Connection: %s" % c)
        if not c:
            self.log.error("No ec2 connection could be established - aborting")
            sys.exit()

        vols = self.get_attached_vol(c)

        self.make_snapshots(c, vols)
        self.snapshot_retention(c, vols)



if __name__ == "__main__":

    creator=AutomatedSnapShot(name="AutomatedSnapShot", description="""
Take snapshot of the attached volumes the script is running on the instance and delete snapshots older then four weeks""")
    creator.add_param("-a", "--access-key", help="aws access key", default=False, required=False, action="store")
    creator.add_param("-b", "--secret-key", help="aws secret key", default=False, required=False, action="store")
    creator.add_param("-r", "--region", help="aws region", default=False, required=True, action="store")
    creator.add_param("-d", "--dry-run", help="Doesnt make changes but only shows what will be changed", default=False, action="store_true")

    creator.run()