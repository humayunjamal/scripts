#!/usr/bin/env python
import boto,boto.iam,boto.utils
import yaml
import csv
import datetime
import os, subprocess, re, commands
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




class PuppetCleanup(LoggingApp):




    def bash_command(self, cmd):
        subprocess.Popen(['/bin/bash', '-c', cmd])

    def ProcessFile(self):
        f = open(tempFile,'r')
        lines = f.readlines()
        f.close()

        for item in lines:
            fqdns.append(item)
            matchObj = re.match('i\-\w+\.example\.io',item)
            if matchObj:
                InstIds.append(item.split(".")[0])
            matchObj2 = re.match('\w+\-\w+\-i\-\w+\.\w+\.example\.io',item)
            if matchObj2:
                InstIds.append("i-"+item.split(".")[0].split("-")[3])

        self.DeadorAlive()

        



    def DeadorAlive(self):

        existing_instances = conn.get_all_instance_status()

        EC2Ids = []

        for instance in existing_instances:
            EC2Ids.append(instance.id)

        for pupInst in InstIds:
            if pupInst in EC2Ids:
                print "The Instance %s does exist in EC2 AWS no cleanup required" % pupInst
            elif pupInst not in EC2Ids:
                print "The Instance %s does NOT EXIST in AWS so please clean it UP" %pupInst
                self.Cleanup(pupInst)


    def Cleanup(self, instanceID):
        for fqdn in fqdns:
            if fqdn.find(instanceID) != -1:
                cmd = "/usr/local/bin/clean_node.sh " + fqdn
                print "Node  %s needs to be cleaned up as No records found in AWS" % fqdn
                subprocess.Popen(['/bin/bash', '-c', cmd])



    def main(self):
        if self.params.dry_run is True:
            self.log.info("************* DRY RUN - NO CHANGES WILL BE MADE ***********")
            self.dryrunprefix = "DRYRUN NO CHANGE: " if self.params.dry_run else ""

        self.log.info("connecting to ec2 region %s" % self.params.region)


        global conn, InstIds,tempFile,fqdns
        InstIds = []
        fqdns = []
        tempFile = "/tmp/hosts.txt"


        if not self.params.access_key and not self.params.secret_key:
            # try and do an instance role conx
            conn = boto.ec2.connect_to_region(self.params.region)
        else:
            # use the command line creds to connect
            conn = boto.ec2.connect_to_region(self.params.region,
                                       aws_access_key_id=self.params.access_key,
                                       aws_secret_access_key=self.params.secret_key)



        self.log.debug("Connection: %s" % conn)
        if not conn:
            self.log.error("No ec2 connection could be established - aborting")
            sys.exit()

        self.bash_command('/usr/local/bin/puppet cert list --all|awk {\'print $2\'}|sed -e \'s/^"//\'  -e \'s/"$//\'>/tmp/hosts.txt')
        self.ProcessFile()




if __name__ == "__main__":

    creator=PuppetCleanup(name="PuppetCleanup", description="""
Cleanup Puppet certs which dont exist anymore""")
    creator.add_param("-a", "--access-key", help="aws access key", default=False, required=False, action="store")
    creator.add_param("-b", "--secret-key", help="aws secret key", default=False, required=False, action="store")
    creator.add_param("-r", "--region", help="aws region", default=False, required=True, action="store")
    creator.add_param("-d", "--dry-run", help="Doesnt make changes but only shows what will be changed", default=False, action="store_true")

    creator.run()
