import subprocess
import os
import re
import xml.etree.ElementTree as ET
from toollabs.webservice.backends import Backend
from toollabs.webservice.services import GenericWebService
from toollabs.webservice.services import JSWebService
from toollabs.webservice.services import LighttpdPlainWebService
from toollabs.webservice.services import LighttpdWebService
from toollabs.webservice.services import PythonWebService
from toollabs.webservice.services import TomcatWebService
from toollabs.webservice.services import UwsgiWebService


class GridEngineBackend(Backend):
    """
    A gridengine job that starts / stops a HTTP serving process (webservice)
    """
    # Specify config for each type that this backend accepts
    # Key is name of type passed in by commandline
    # cls is the Webservice class to instantiate
    # release is an optional key that specifies which release to run this on.
    #   options are: trusty
    #   defaults to 'trusty'
    # queue is an optional key that spcifies which queue to run ths one.
    #   options are: webgrid-lighttpd, webgrid-generic
    #   defaults to 'webgrid-generic'
    CONFIG = {
        'lighttpd': {
            'cls': LighttpdWebService, 'queue': 'webgrid-lighttpd'},
        'lighttpd-plain': {
            'cls': LighttpdPlainWebService, 'queue': 'webgrid-lighttpd'},
        'uwsgi-python': {'cls': PythonWebService},
        'uwsgi-plain': {'cls': UwsgiWebService},
        'nodejs': {'cls': JSWebService},
        'tomcat': {'cls': TomcatWebService},
        'generic': {'cls': GenericWebService}
    }

    def __init__(self, tool, type, extra_args=None):
        super(GridEngineBackend, self).__init__(tool, type, extra_args)
        cfg = GridEngineBackend.CONFIG[type]
        self.webservice = cfg['cls'](tool, extra_args)
        self.release = cfg.get('release', 'trusty')
        self.queue = cfg.get('queue', 'webgrid-generic')
        self.name = '{type}-{toolname}'.format(type=type, toolname=tool.name)
        try:
            memlimit = '/data/project/.system/config/{}.web-memlimit'.format(
                self.tool.name)
            with open(memlimit) as f:
                self.memlimit = f.read().strip()
        except IOError:
            self.memlimit = '4G'

    def _get_job_xml(self):
        """
        Gets job status xml of this job

        :return: ET xml object if the job is found, None otherwise
        """
        output = subprocess.check_output(['qstat', '-xml'])

        # Fix XML.
        output = re.sub('JATASK:[^>]*', 'jatask', output)

        # GE is stupid.
        # Returns output like:
        # <><ST_name>blah</ST_name></>
        # If the job is not found.
        if '<unknown_jobs' in output and '<>' in output:
            return None
        xml = ET.fromstring(output)
        job_name_node = xml.find('.//job_list[JB_name="%s"]' % self.name)
        return job_name_node

    def request_start(self):
        self.webservice.check()
        cmd = '/usr/bin/webservice-runner --register-proxy --type {}'.format(
            self.webservice.name)
        if self.extra_args:
            cmd += " --extra_args '%s'" % self.extra_args
        command = ['qsub',
                   '-e', os.path.expanduser('~/error.log'),
                   '-o', os.path.expanduser('~/error.log'),
                   '-i', '/dev/null',
                   '-q', self.queue,
                   '-l', 'h_vmem=%s,release=%s' % (
                       self.memlimit, self.release
                    ),
                   '-b', 'y',
                   '-N', self.name,
                   cmd]

        subprocess.check_call(command, stdout=open(os.devnull, 'wb'))

    def request_stop(self):
        command = ['/usr/bin/qdel', self.name]
        subprocess.check_call(command, stdout=open(os.devnull, 'wb'))

    def get_state(self):
        job = self._get_job_xml()
        if job is not None:
            state = job.findtext('.//state').lower()
            if 'r' in state:
                return Backend.STATE_RUNNING
            else:
                return Backend.STATE_PENDING
        return Backend.STATE_STOPPED
