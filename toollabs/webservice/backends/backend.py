from abc import ABCMeta, abstractmethod


class Backend(object):
    __metaclass__ = ABCMeta
    """
    A webservice backend that submits and runs the actual webservice in a cluster
    """
    STATE_STOPPED = 0
    STATE_RUNNING = 1
    STATE_PENDING = 2

    def __init__(self, webservice):
        self.webservice = webservice

    @abstractmethod
    def get_state(self):
        """
        Returns state of webservice.

        One of Backend.STATE_STOPPED, Backend.STATE_RUNNING or Backend.STATE_PENDING
        """
        pass

    @abstractmethod
    def request_start(self):
        """
        Asynchronously start the webservice on the cluster.

        Callers then need to poll get_state() to figure out if it is complete.
        """
        pass

    @abstractmethod
    def request_stop(self):
        """
        Asynchronously stop the webservice on the cluster

        Callers then need to poll get_state() to figure out if it is complete.
        """
        pass