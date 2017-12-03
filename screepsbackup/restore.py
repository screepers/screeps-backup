
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

    def saveMemory(self, memstring, shard):
        print('saving memory')
        api = self.getApiClient()
        return api.set_memory('', memstring, shard)

    def saveSegment(self, segid, segmentstring, shard):
        print('saving segment %s' % segid)
        api = self.getApiClient()
        return api.set_segment(segid, segmentstring, shard)

    def getShards(self):
        api = self.getApiClient()
        try:
            shard_data = api.shard_info()['shards']
            shards = [x['name'] for x in shard_data]
            if len(shards) < 1:
                shards = ['shard0']
        except:
            shards = ['shard0']
        return shards


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

    shards = restore.getShards()
    for shard in shards:
        mempath = "%s/%s_memory.json" % (directory,shard)
        if os.path.isfile(mempath):
            with open(mempath, "r") as text_file:
                memstring = text_file.read()
                restore.saveMemory(memstring, shard)
                print('Memory restored.')
        else:
            print('No memory data found in this directory')
            exit(-1)

        for i in range(0, 100):
            segmentpath = "%s/%s_segment_%s.json" % (directory, shard, i)
            if os.path.isfile(segmentpath):
                with open(segmentpath, "r") as text_file:
                    segmentstring = text_file.read()
                    restore.saveSegment(i, segmentstring, shard)
                    print('Restored segment %s' % (i,))

