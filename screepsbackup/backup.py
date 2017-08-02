
from base64 import b64decode
import datetime
import errno
import gzip
import os
from os.path import expanduser
import screepsapi
import sys
import yaml

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


class Backup(object):

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

    def getMemory(self, shard):
        api = self.getApiClient()
        ret = api.get('user/memory', path='', shard=shard)
        return self.normalize(ret)

    def getSegment(self, segmentid, shard):
        api = self.getApiClient()
        segment = api.get('user/memory-segment', segment=segmentid, shard=shard)
        return self.normalize(segment)

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


    def normalize(self, ret):
        if not ret:
            return False
        if 'data' not in ret:
            return False
        if ret['data'] is None:
            return False
        if ret['data'][:3] == 'gz:':
            string = StringIO(b64decode(ret['data'][3:]))
            gzipfile = gzip.GzipFile(fileobj=string)
            return gzipfile.read()
        else:
            return ret['data']


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        base_directory = sys.argv[1]
    else:
        cwd = os.getcwd()
        base_directory = cwd

    backup = Backup()

    timelabel = datetime.datetime.now().strftime("screeps-%Y_%m_%d_%H_%M_%S")
    directory = '%s/%s' % (base_directory, timelabel)
    if not os.path.exists(directory):
        os.makedirs(directory)

    shards = backup.getShards()
    for shard in shards:

        print('Backing up Screeps memory for %s' % (shard,))
        memorystring = backup.getMemory(shard)

        with open("%s/%s_memory.json" % (directory,shard), "w") as text_file:
            text_file.write(memorystring)

        print('Memory backed up')
        print('Backing up segments for %s' % (shard,))

        for i in range(0, 100):
            segmentstring = backup.getSegment(i, shard)
            if segmentstring and len(segmentstring) > 0:
                with open("%s/%s_segment_%s.json" % (directory, shard, i), "w") as text_file:
                    print('Saving segment %s from %s' % (i,shard))
                    text_file.write(segmentstring.encode('utf-8').strip())

        symlink = '%s/current' % (base_directory,)
        if os.path.lexists(symlink):
            os.remove(symlink)
        os.symlink(directory, symlink)
