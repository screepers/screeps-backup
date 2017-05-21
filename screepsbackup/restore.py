
import datetime
import os
from os.path import expanduser
import requests
import screepsapi
import sys
import yaml


class Restore(object):

    apiclient = False
    settings = False

    def getSettings(self):
        if not self.settings:
            cwd = os.getcwd()
            path = cwd + '/.settings.yaml'
            if not os.path.isfile(path):
                path = cwd + '/.screeps_settings.yaml'
            if not os.path.isfile(path):
                path = expanduser('~') + '/.screeps_settings.yaml'
            if not os.path.isfile(path):
                print 'no settings file found'
                sys.exit(-1)
                return False
            with open(path, 'r') as f:
                self.settings = yaml.load(f)
        return self.settings

    def getApiClient(self):
        if not self.apiclient:
            settings = self.getSettings()
            self.apiclient = screepsapi.API(
                           u=settings['screeps_username'],
                           p=settings['screeps_password'],
                           ptr=settings['screeps_ptr'],
                           host=settings['screeps_host'])
        return self.apiclient

    def saveMemory(self, memstring):
        print('saving memory')
        api = self.getApiClient()
        return api.set_memory('', memstring)

    def saveSegment(self, segid, segmentstring):
        print('saving segment %s' % segid)
        api = self.getApiClient()
        return api.set_segment(segid, segmentstring)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
    else:
        cwd = os.getcwd()
        directory = cwd

    print('Continuing will overwrite all of your data on the server.')
    while True:
        ans = raw_input('Are you sure you want to do this? [Y/n]: ')
        if not ans:
            continue
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            break
        if ans == 'n' or ans == 'N':
            exit(-1)

    print('Restoring Screeps data')

    restore = Restore()

    mempath = "%s/memory.json" % (directory,)
    if os.path.isfile(mempath):
        with open(mempath, "r") as text_file:
            memstring = text_file.read()
            restore.saveMemory(memstring)
            print('Memory restored.')
    else:
        print('No memory data found in this directory')
        exit(-1)

    for i in range(0, 100):
        segmentpath = "%s/segment_%s.json" % (directory, i)
        if os.path.isfile(segmentpath):
            with open(segmentpath, "r") as text_file:
                segmentstring = text_file.read()
                restore.saveSegment(i, segmentstring)
                print('Restored segment %s' % (i,))

