import os
from toollabs.webservice import WebService


class JSWebService(WebService):
    NAME = 'nodejs'
    QUEUE = 'webgrid-generic'

    def check(self):
        package_path = self.tool.get_homedir_subpath('www/js/package.json')
        if not os.path.exists(package_path):
            raise WebService.InvalidWebServiceException(
                'Could not find ~/www/js/package.json. '
                'Are you sure you have a proper nodejs '
                'application in ~/www/js?')

    def run(self, port):
        super(JSWebService, self).run(port)
        os.chdir(self.tool.get_homedir_subpath('www/js'))
        os.execv('/usr/bin/npm', ['/usr/bin/npm', 'start'])
