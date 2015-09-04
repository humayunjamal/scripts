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
import time 
# you need to pip install pyCLI
from cli.log import LoggingApp
from pprint import pprint
import boto.ec2.autoscale 
__author__ = 'humayun.jamal'

 


class AwsStartShutASG(LoggingApp):


    def check_asg(self, c, bc, asg_list):
        self.log.info("Checking if ASGS exists \"%s\"" % (self.params.autoscaling_group_name))
        asgs = c.get_all_groups()

        for group in asgs:
            for asgName in asg_list:
                if asgName == group.name:
                    print "YES the group exists"
                    if self.params.stop:
                        c.suspend_processes(group.name)
                        print "The ASG group is now suspended" 
                        self.stopInstances(bc, group)
                    elif self.params.start:
                        c.resume_processes(group.name)
                        print "The ASG group is now resumed" 
                        self.startInstances(bc, group)



    def stopInstances(self, bc, asg):
        self.log.info("Stopping instances for the ASG \"%s\"" % (asg.name))
        instance_ids = [i.instance_id for i in asg.instances]
        print "shutting down Instance IDS %s " % instance_ids
        for inst in instance_ids:
            bc.stop_instances(instance_ids=[inst])
            print "The instance %s is now being stopped" % inst
            print "Checking status of instance"
            self.checkInstanceState(bc,inst, "stopped")


    def checkInstanceState(self, bc, id, state):
        instances = bc.get_only_instances()
        for inst in instances:
            if inst.id == id:
                print "The Instance State is \"%s\"" % inst.state
                while inst.state != state: 
                    time.sleep(60)
                    inst.update()
                    print "The Instance State is \"%s\"" % inst.state
                    if inst.state == state:
                        print "The instance is now completely in %s state" % inst.state
                        break
                    elif inst.state == "terminated" or inst.state == "shutting-down":
                        print "The instance is in  %s state so exiting and moving on to next" % inst.state
                        break



    def startInstances(self, bc, asg):
        self.log.info("Starting instances for the ASG \"%s\"" % (asg.name))
        instance_ids = [i.instance_id for i in asg.instances]
        print "sStarting UP Instance IDS %s " % instance_ids
        for inst in instance_ids:
            bc.start_instances(instance_ids=[inst])
            print "The instance %s is now being started" % inst
            print "Checking status of instance"
            self.checkInstanceState(bc,inst, "running")



    



    def main(self):
        if self.params.dry_run is True:
		self.log.info("************* DRY RUN - NO CHANGES WILL BE MADE ***********")

        self.dryrunprefix = "DRYRUN NO CHANGE: " if self.params.dry_run else ""

        self.log.info("connecting to ec2 region %s" % self.params.region) 

        asg_list = self.params.autoscaling_group_name.split(",")

        c = None
        bc = None
        if not self.params.access_key and not self.params.secret_key:
            # try and do an instance role conx
            c = boto.ec2.autoscale.connect_to_region(self.params.region)
            bc = boto.ec2.connect_to_region(self.params.region)
        else:
            # use the command line creds to connect
            c = boto.ec2.autoscale.connect_to_region(self.params.region,
                                       aws_access_key_id=self.params.access_key,
                                       aws_secret_access_key=self.params.secret_key)
            bc = boto.ec2.connect_to_region(self.params.region,
                                       aws_access_key_id=self.params.access_key,
                                       aws_secret_access_key=self.params.secret_key)

        self.log.debug("Connection: %s" % c)
        if not c:
            self.log.error("No connection could be established - aborting")
            sys.exit()
        if not bc:
            self.log.error("No connection could be established - aborting")
            sys.exit()

        if self.params.autoscaling_group_name is not None:
            self.check_asg(c,bc,asg_list)
        self.log.info("Finished")
        


if __name__ == "__main__":

    creator=AwsStartShutASG(name="AwsStartShutASG", description="""
Starts and shutdown instances of the specified ASG while suspending autoscaling process which kicks off autoscaling actions 
""")
    creator.add_param("-a", "--access-key", help="aws access key", default=False, required=False, action="store")
    creator.add_param("-b", "--secret-key", help="aws secret key", default=False, required=False, action="store")
    creator.add_param("-r", "--region", help="aws region", default=False, required=False, action="store")
    creator.add_param("-g", "--autoscaling-group-name", help="comma seperated autoscaling group names to process", required=True, action="store") 
    creator.add_param("-i", "--start", help="start the instances", required=False, action="store_true", default=False) 
    creator.add_param("-p", "--stop", help="stop the instances", required=False, action="store_true", default=False) 
    creator.add_param("-d", "--dry-run", help="Doesnt make changes but only shows what will be changed", default=False, action="store_true")
    
    creator.run()
    
