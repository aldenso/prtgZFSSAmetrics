#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: Aldo Sotolongo
# @Date:   2017-05-12 21:34:39
# @Last Modified by:   aldenso
# @Last Modified time: 2017-05-15 03:32:18
# Description: PRTG script to get zfssa metrics
# Usage: on additional parameters for sensor you can use:
# --host <zfssa_ip> --username <username> --password <password>
# --host <zfssa_ip> --username <username> --password <password> --include cpu,disk,nfs3
# --host <zfssa_ip> --username <username> --password <password> --include smb2,nfs2,iscsi

import sys
import json
import getopt
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from paepy.ChannelDefinition import CustomSensorResult

# to disable warning
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See:
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

###############################################################################
# Holders for PRTG additional parameters
###############################################################################
HOST = ""
USERNAME = ""
PASSWORD = ""
EXCLUDECHECKS = []
INCLUDECHECKS = []

###############################################################################
# Get PRTG Additional Parameters
###############################################################################
prtgparams = json.loads(sys.argv[1:][0])
params = str.split(prtgparams["params"])
opts, args = getopt.getopt(params, "h:u:p:i:e",
                           ["host=", "username=", "password=",
                            "include=", "exclude=", ])
for opt, arg in opts:
    if opt in ("-h", "--host"):
        HOST = str(arg)
    elif opt in ("-u", "--username"):
        USERNAME = str(arg)
    elif opt in ("-p", "--password"):
        PASSWORD = str(arg)
    elif opt in ("-e", "--exclude"):
        EXCLUDECHECKS = arg.split(",")
    elif opt in ("-i", "--include"):
        INCLUDECHECKS = arg.split(",")

###############################################################################
# constants
###############################################################################
ZAUTH = (USERNAME, PASSWORD)
URL = "https://{}:215/api".format(HOST)
HEADER = {"Content-Type": "application/json"}
TIMEOUT = 20
CPURES = "/analytics/v1/datasets/cpu.utilization/data?start=now&seconds=1"
NFS2RES = "/analytics/v1/datasets/nfs2.ops/data?start=now&seconds=1"
NFS3RES = "/analytics/v1/datasets/nfs3.ops/data?start=now&seconds=1"
NFS4RES = "/analytics/v1/datasets/nfs4.ops/data?start=now&seconds=1"
DISKRES = "/analytics/v1/datasets/io.ops/data?start=now&seconds=1"
FCRES = "/analytics/v1/datasets/fc.ops/data?start=now&seconds=1"
ISCSIRES = "/analytics/v1/datasets/iscsi.ops/data?start=now&seconds=1"
SMBRES = "/analytics/v1/datasets/smb.ops/data?start=now&seconds=1"
SMB2RES = "/analytics/v1/datasets/smb2.ops/data?start=now&seconds=1"
NICRES = "/analytics/v1/datasets/nic.kilobytes/data?start=now&seconds=1"


###############################################################################
# Limit Max Warnings and Limit Max Error values.
###############################################################################
MAXWARNCPU, MAXERRORCPU = 60, 80
MAXWARNNFS2, MAXERRORNFS2 = 50000, 100000
MAXWARNNFS3, MAXERRORNFS3 = 50000, 100000
MAXWARNNFS4, MAXERRORNFS4 = 40000, 80000
MAXWARNDISK, MAXERRORDISK = 25000, 50000
MAXWARNFC, MAXERRORFC = 6000, 8000
MAXWARNISCSI, MAXERRORISCSI = 6000, 8000
MAXWARNSMB, MAXERRORSMB = 40000, 80000
MAXWARNSMB2, MAXERRORSMB2 = 40000, 80000
MAXWARNNIC, MAXERRORNIC = 500000, 1000000


###############################################################################
# Custom Sensor class.
###############################################################################
class AdvancedCustomSensorResult(CustomSensorResult):
    """Extend CustomSensorResult to include additional parameters"""
    def add_channel(
            self,
            channel_name,
            is_limit_mode=False,
            limit_max_error=None,
            limit_max_warning=None,
            limit_min_error=None,
            limit_min_warning=None,
            limit_error_msg=None,
            limit_warning_msg=None,
            decimal_mode=None,
            mode=None,
            value=None,
            unit='Custom',
            is_float=False,
            value_lookup=None,
            show_chart=True,
            custom_unit=None,
            warning=False,
            primary_channel=False
    ):
        channel = {}

        # Process in parent class
        super(AdvancedCustomSensorResult, self).add_channel(
            channel_name, is_limit_mode, limit_max_error,
            limit_max_warning, limit_min_error, limit_min_warning,
            limit_error_msg, limit_warning_msg,
            decimal_mode, mode, value, unit, is_float, value_lookup,
            show_chart, warning, primary_channel)

        # Get channel from the original class
        if primary_channel:
            channel = self.channels[0]
        else:
            channel = self.channels[len(self.channels) - 1]

        # Additional parameters
        if custom_unit is not None and self.__is_customunit_valid(custom_unit):
            channel['CustomUnit'] = custom_unit

        # Re-save channel
        if primary_channel:
            self.channels[0] = channel
        else:
            self.channels[len(self.channels) - 1] = channel

    @staticmethod
    def __is_customunit_valid(unit):

        valid_unit = {
            "Ops/sec",
            "Kilobytes/sec"
        }

        if unit in valid_unit:
            return True
        else:
            return False


###############################################################################
# return channels
###############################################################################
channels = AdvancedCustomSensorResult()


def cpu():
    try:
        req = requests.get(URL + CPURES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="CPU Usage Percent",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Percent",
                                 limit_max_warning=MAXWARNCPU,
                                 limit_max_error=MAXERRORCPU,
                                 is_limit_mode=1,
                                 primary_channel=True
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check cpu: {} |"
        else:
            channels.sensor_message += "| can't check cpu: {} |"


def nfs2():
    try:
        req = requests.get(URL + NFS2RES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="NFS2",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNNFS2,
                                 limit_max_error=MAXERRORNFS2,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check nfs2: {} |"
        else:
            channels.sensor_message += "| can't check nfs2: {} |"


def nfs3():
    try:
        req = requests.get(URL + NFS3RES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="NFS3",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNNFS3,
                                 limit_max_error=MAXERRORNFS3,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check nfs3: {} |"
        else:
            channels.sensor_message += "| can't check nfs3: {} |"


def nfs4():
    try:
        req = requests.get(URL + NFS4RES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="NFS4",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNNFS4,
                                 limit_max_error=MAXERRORNFS4,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check nfs4: {} |"
        else:
            channels.sensor_message += "| can't check nfs4: {} |"


def disk():
    try:
        req = requests.get(URL + DISKRES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="Disk",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNDISK,
                                 limit_max_error=MAXERRORDISK,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check disk: {} |"
        else:
            channels.sensor_message += "| can't check disk: {} |"


def fc():
    try:
        req = requests.get(URL + FCRES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="FC",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNFC,
                                 limit_max_error=MAXERRORFC,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check fc: {} |"
        else:
            channels.sensor_message += "| can't check fc: {} |"


def iscsi():
    try:
        req = requests.get(URL + ISCSIRES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="ISCSI",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNISCSI,
                                 limit_max_error=MAXERRORISCSI,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check iscsi: {} |"
        else:
            channels.sensor_message += "| can't check iscsi: {} |"


def smb():
    try:
        req = requests.get(URL + SMBRES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="SMB",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNSMB,
                                 limit_max_error=MAXERRORSMB,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check smb: {} |"
        else:
            channels.sensor_message += "| can't check smb: {} |"


def smb2():
    try:
        req = requests.get(URL + SMB2RES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="SMB2",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNSMB2,
                                 limit_max_error=MAXERRORSMB2,
                                 is_limit_mode=1,
                                 custom_unit="Ops/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check smb2: {} |"
        else:
            channels.sensor_message += "| can't check smb2: {} |"


def nic():
    try:
        req = requests.get(URL + NICRES,
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for data in j.values():
            channels.add_channel(channel_name="NIC",
                                 value=data["data"]["value"],
                                 is_float=False,
                                 unit="Custom",
                                 limit_max_warning=MAXWARNNIC,
                                 limit_max_error=MAXERRORNIC,
                                 is_limit_mode=1,
                                 custom_unit="Kilobytes/sec"
                                 )
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check nic: {} |"
        else:
            channels.sensor_message += "| can't check nic: {} |"


###############################################################################
# Default list of enabled checks to run
###############################################################################
ENABLEDCHECKS = {
    "cpu": cpu,
    "nfs2": nfs2,
    "nfs3": nfs3,
    "nfs4": nfs4,
    "disk": disk,
    "fc": fc,
    "iscsi": iscsi,
    "smb": smb,
    "smb2": smb2,
    "nic": nic
}


###############################################################################
# MAIN Function
###############################################################################
def main():
    if len(INCLUDECHECKS) != 0 and len(EXCLUDECHECKS) != 0:
        channels.add_error("Sensor failed: can't use include and exclude")
    elif len(INCLUDECHECKS) != 0:
        for check in INCLUDECHECKS:
            ENABLEDCHECKS[check]()
    elif len(EXCLUDECHECKS) != 0:
        for check in EXCLUDECHECKS:
            del ENABLEDCHECKS[check]
        for check in ENABLEDCHECKS:
            ENABLEDCHECKS[check]()
    else:
        for check in ENABLEDCHECKS:
            ENABLEDCHECKS[check]()
    if len(channels.channels) == 0:
        channels.add_error("No channels can be retrieved")
    print(channels.get_json_result())


if __name__ == "__main__":
    main()
