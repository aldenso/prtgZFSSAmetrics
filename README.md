# prtgZFSSAmetrics

PRTG Python Advanced script to get metrics from analitics datasets using ZFS Storage Appliance Rest api.

## Dependencies

request (use pip) and paepy (included in prtg).

It is a good idea to get pip for your prtg server, so use any of the following links in how to get pip:

* <https://packaging.python.org/installing/#requirements-for-installing-packages>
* <https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation>

### Usage

Copy your script to "\Custom Sensors\python" directory (example: *C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\python*).

Include your sensor as **Python Script Advanced**.

In **Additional Parameters** tab, use some pattern like the next examples:

    --host <zfssa_ip> --username monitor --password <password>
    --host <zfssa_ip> --username monitor --password <password> --include cpu,disk,nfs3,iscsi
    --host <zfssa_ip> --username monitor --password <password> --exclude nfs2,smb,fc

### Notes

* You need a ZFSSA user with enough privileges to get data from datasets.
* The Rest service must be enable in the ZFSSA.
* Be careful about the number of metrics to retrieve and the time it takes (frequency shouldn't be so agresive).
* You need Administrator privileges in the PRTG server to copy the scripts, install pip and the packages with pip.


### Available metrics (name:dataset) at the moment, you can use the names for include or exclude parameters:

* cpu:cpu.utilization
* nfs2:nfs2.ops
* nfs3:nfs3.ops
* nfs4:nfs4.ops
* disk:io.ops
* fc:fc.ops
* iscsi:iscsi.ops
* smb:smb.ops
* smb2:smb2.ops
* nic:nic.kilobytes