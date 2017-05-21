
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

    def getMemory(self):
        api = self.getApiClient()
        ret = api.get('user/memory', path='')
        return self.normalize(ret)

    def getSegment(self, segmentid):
        api = self.getApiClient()
        segment = api.get('user/memory-segment', segment=segmentid)
        return self.normalize(segment)

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
    print('Backing up Screeps memory')

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

    memorystring = backup.getMemory()

    with open("%s/memory.json" % (directory,), "w") as text_file:
        text_file.write(memorystring)

    print('Memory backed up')
    print('Backing up segments')

    for i in range(0, 100):
        segmentstring = backup.getSegment(i)
        if segmentstring and len(segmentstring) > 0:
            with open("%s/segment_%s.json" % (directory, i), "w") as text_file:
                print('Saving segment %s' % (i,))
                text_file.write(segmentstring)

    symlink = '%s/current' % (base_directory,)
    if os.path.lexists(symlink):
        os.remove(symlink)
    os.symlink(directory, symlink)
