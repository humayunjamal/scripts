#!/usr/bin/env python
import datetime
import os, subprocess, re, commands
from cli.log import LoggingApp
from pprint import pprint

__author__ = 'humayun.jamal'




class LogProcessing(LoggingApp):




    def ProcessFile(self, logfile):
        self.log.info("Opening File")
        f = open(logfile,'r')
        lines = f.readlines()
        f.close()
        self.log.info("Reading Line by line from the File , starting Loop")
        for line in lines:

            self.log.info("Breaking each line into list items split by space")
            chunk=line.split()
            specSubject=[]
            messageid=[]
            for item in chunk:
                self.log.info("Searching for item which starts with id=")
                foundmsg=re.findall('^id\=', item)
                if foundmsg:
                    messageid.append(item)
                self.log.info("Searching for Subject which starts with T=\"")
                subject=re.findall('^T\=\"\w+', item)
                if subject:
                    index=chunk.index(item)
                    for spcSub in chunk[index:]:
                        specSubject.append(spcSub)
                        self.log.info("Searching for Subject which ends with \"")
                        endofSub=re.findall('\"$', spcSub)
                        if endofSub:
                            break
                    print "The message ID is %s The subject is %s" %(''.join(messageid).split('=', 1)[-1],''.join(specSubject).split('=', 1)[-1])


    def main(self):
        if self.params.dry_run is True:
            self.log.info("************* DRY RUN - NO CHANGES WILL BE MADE ***********")
            self.dryrunprefix = "DRYRUN NO CHANGE: " if self.params.dry_run else ""


        if not self.params.log_file:
            self.log.error("No Log file specified - aborting")
            sys.exit()


        self.ProcessFile(self.params.log_file)




if __name__ == "__main__":

    creator=LogProcessing(name="LogProcessing", description="""
Log Processing """)
    creator.add_param("-f", "--log-file", help="log file name to process", default=False, required=True, action="store")
    creator.add_param("-d", "--dry-run", help="Doesnt make changes but only shows what will be changed", default=False, action="store_true")

    creator.run()