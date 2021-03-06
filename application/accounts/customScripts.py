import os
import platform
import django.db.utils
import threading, time
from .models import DatabaseConnection, ServerConnection, NginxInstallation, PhpInstallation


class Server_ping(object):
    """Pings a server

    :param ip_list: A list of ip addresses
    """

    def __init__(self, *args, **kwargs):
        self.list = []

    def server_status(self, ip_list):
        self.list = ip_list
        status_list = []
        for item in ip_list:
            if platform.system() == "Windows":
                response = os.system("ping " + item + " -n 1")
            else:
                response = os.system("ping -c 1 " + item)

            if response == 0:
                status_list.append('Running')
                print item, 'is up!'
            else:
                status_list.append("Can't connect")
                print item, 'is down!'

        return status_list


class SuccessfullInstall:
    """ A class with methods that checks if services installed correctly

    :param output: The status output of an Ansible play
    :param Server: The server the output correlates to
    """

    def __init__(self, *args, **kwargs):
        self.list = []

    def check_install_db(self, output, server):
        check = 'Install database server,{}'.format(server)
        check_two = 'Uninstall Database-server,{}'.format(server)
        if check in output:
            if output[check] == 'Success':
                return True
        elif check_two in output:
            if output[check_two] == 'Success':
                return True
        else:
            return False

    def check_install_nginx(self, output, server):
        check = 'Install nginx,{}'.format(server)
        if check in output:
            if output[check] == 'Success':
                return True
        checks = 'Uninstall Nginx-server,{}'.format(server)
        if checks in output:
            if output[checks] == 'Success':
                return True
        else:
            return False

    def check_install_php(self, output, server):
        check = 'install php packages,{}'.format(server)
        if check in output:
            if output[check] == 'Success':
                return True
        checks = 'Uninstall Php-packages,{}'.format(server)
        if checks in output:
            if output[checks] == 'Success':
                return True
        else:
            return False


class ServerQuery:
    """ Queries the database for servers that has installed:

            Databases
            Nginx
            Php
    """

    def __init__(self, *args, **kwargs):
        self.list = []

    def get_server_choices(self):
        try:
            squery = ServerConnection.objects.order_by(
                'server_nickname').values_list('server_nickname', flat=True).distinct()
            squery.choices = [('all', 'Choose all')] + [(id, id) for id in squery]
            return squery.choices
        except:
            print "Exception: get_server_choices is bypassed"

    def get_installed_db_servers(self):
        try:
            squery = DatabaseConnection.objects.order_by(
                'server_name').values_list('server_name', flat=True).distinct().filter(database='MySql')
            squery.choices = [(id, id) for id in squery]
            return squery.choices
        except:
            print "Exception: get_installed_db_servers is bypassed"

    def get_installed_postgres_servers(self):
        try:
            squery = DatabaseConnection.objects.order_by(
                'server_name').values_list('server_name', flat=True).distinct().filter(database='PostgreSql')
            squery.choices = [(id, id) for id in squery]
            return squery.choices
        except:
            print "Exception: get_installed_postgres_servers is bypassed"

    def get_installed_nginx(self):
        try:
            squery = NginxInstallation.objects.order_by(
                'servers').values_list('servers', flat=True).distinct()
            squery.choices = [(id, id) for id in squery]
            return squery.choices
        except:
            print "Exception: get_installed_nginx is bypassed"

    def get_installed_php(self):
        try:
            squery = PhpInstallation.objects.order_by(
                'servers').values_list('servers', flat=True).distinct()
            squery.choices = [(id, id) for id in squery]
            return squery.choices
        except:
            print "Exception: get_installed_php is bypassed"


class ElapsedTimeThread(threading.Thread):
    """"Stoppable thread that prints the time elapsed"""
    def __init__(self):
        super(ElapsedTimeThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        thread_start = time.time()
        while not self.stopped():
            print("\rElapsed Time {:.0f} seconds".format(time.time()-thread_start))
            time.sleep(1)


