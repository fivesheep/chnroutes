from __future__ import with_statement
import zipfile
import StringIO
from models import MyFile
import re
import urllib2
import math
import textwrap
import datetime

from google.appengine.api import files
from google.appengine.ext import blobstore

def generate_all():
    q=MyFile.all()
    mfiles=q.fetch(100)
    
    # delete all old files and data
    for mf in mfiles:
        bk=mf.blob_key
        blobstore.delete(bk)
        # delete data entity
        mf.delete()
    
    # dict of zipfiles being generated and their relevant generators
    generators={'openvpn.zip':generate_ovpn,
            'windows.zip':generate_win,
            'linux.zip':generate_linux,
            'mac.zip':generate_mac,
            'android.zip':generate_android
            }
    
    ip_data = fetch_ip_data()
    
    for fn,g in generators.iteritems():
        data=g(ip_data)
        z=zipit(data) #compress the data
        blob_file=files.blobstore.create('application/zip', 
                                         _blobinfo_uploaded_filename=fn)
        with files.open(blob_file,'a') as f:
            f.write(z)
        files.finalize(blob_file)
        blob_key = files.blobstore.get_blob_key(blob_file)
        mf=MyFile(name=fn,blob_key=str(blob_key))
        mf.update_date=datetime.datetime.now().date()
        mf.put()

def fetch_ip_data():
    #fetch data from apnic
    url=r'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'
    data=urllib2.urlopen(url).read()
    cnregex=re.compile(r'apnic\|cn\|ipv4\|[0-9\.]+\|[0-9]+\|[0-9]+\|a.*',re.IGNORECASE)
    cndata=cnregex.findall(data)
    ip_data=[]

    for item in cndata:
        unit_items=item.split('|')
        starting_ip=unit_items[3]
        num_ip=int(unit_items[4])
        
        imask=0xffffffff^(num_ip-1)
        #convert to string
        imask=hex(imask)[2:]
        mask=[0]*4
        mask[0]=imask[0:2]
        mask[1]=imask[2:4]
        mask[2]=imask[4:6]
        mask[3]=imask[6:8]
        
        #convert str to int
        mask=[ int(i,16 ) for i in mask]
        mask="%d.%d.%d.%d"%tuple(mask)
        
        #mask in *nix format
        mask2=32-int(math.log(num_ip,2))
        
        ip_data.append((starting_ip,mask,mask2))
         
    return ip_data

def generate_ovpn(ip_data, metric=25):
    s=StringIO.StringIO()
    for ip,mask,_ in ip_data:
        route_item="route %s %s net_gateway %d\n"%(ip,mask,metric)
        s.write(route_item)
    return {'routes.txt':s.getvalue()}

def generate_linux(ip_data,metric=25):
    upscript_header=textwrap.dedent("""\
    #!/bin/bash
    export PATH="/bin:/sbin:/usr/sbin:/usr/bin"
    
    OLDGW=`ip route show | grep '^default' | sed -e 's/default via \\([^ ]*\\).*/\\1/'`
    
    if [ $OLDGW == '' ]; then
        exit 0
    fi
    
    if [ ! -e /tmp/vpn_oldgw ]; then
        echo $OLDGW > /tmp/vpn_oldgw
    fi
    
    """)
    
    downscript_header=textwrap.dedent("""\
    #!/bin/bash
    export PATH="/bin:/sbin:/usr/sbin:/usr/bin"
    
    OLDGW=`cat /tmp/vpn_oldgw`
    
    """)
    
    up=StringIO.StringIO()
    down=StringIO.StringIO()
    
    up.write(upscript_header)
    up.write('\n')
    down.write(downscript_header)
    down.write('\n')
    
    for ip,mask,_ in ip_data:
        up.write('route add -net %s netmask %s gw $OLDGW\n'%(ip,mask))
        down.write('route del -net %s netmask %s\n'%(ip,mask))

    down.write('rm /tmp/vpn_oldgw\n')

    return {'ip-pre-up':up.getvalue(),'ip-down':down.getvalue()}

def generate_mac(ip_data,metric=25):
    upscript_header=textwrap.dedent("""\
    #!/bin/sh
    export PATH="/bin:/sbin:/usr/sbin:/usr/bin"
    
    OLDGW=`netstat -nr | grep '^default' | grep -v 'ppp' | sed 's/default *\\([0-9\.]*\\) .*/\\1/'`

    if [ ! -e /tmp/pptp_oldgw ]; then
        echo "${OLDGW}" > /tmp/pptp_oldgw
    fi
    
    dscacheutil -flushcache
    
    """)
    
    downscript_header=textwrap.dedent("""\
    #!/bin/sh
    export PATH="/bin:/sbin:/usr/sbin:/usr/bin"
    
    if [ ! -e /tmp/pptp_oldgw ]; then
            exit 0
    fi
    
    ODLGW=`cat /tmp/pptp_oldgw`
    
    """)
    
    up=StringIO.StringIO()
    down=StringIO.StringIO()
    
    up.write(upscript_header)
    up.write('\n')
    down.write(downscript_header)
    down.write('\n')
    
    for ip,_,mask in ip_data:
        up.write('route add %s/%s "${OLDGW}"\n'%(ip,mask))
        down.write('route delete %s/%s ${OLDGW}\n'%(ip,mask))
    
    down.write('\n\nrm /tmp/pptp_oldgw\n')
    return {'ip-up':up.getvalue(),'ip-down':down.getvalue()}

def generate_win(ip_data,metric=25):

    upscript_header="@echo off\r\n" + """for /F "tokens=3" %%* in ('route print ^| findstr "\\<0.0.0.0\\>"') do set "gw=%%*"\r\n"""
    
    up=StringIO.StringIO()
    down=StringIO.StringIO()
    
    up.write(upscript_header)
    up.write('\r\n')
    up.write('ipconfig /flushdns\r\n')
    
    down.write("@echo off")
    down.write('\r\n')
    
    for ip,mask,_ in ip_data:
        up.write('route add %s mask %s %s metric %d\r\n'%(ip,mask,"%gw%",metric))
        down.write('route delete %s\r\n'%(ip))
    
    return {'vpnup.bat':up.getvalue(),'vpndown.bat':down.getvalue()}


def generate_android(ip_data,metric=25):   
    upscript_header=textwrap.dedent("""\
    #!/bin/sh
    alias nestat='/system/xbin/busybox netstat'
    alias grep='/system/xbin/busybox grep'
    alias awk='/system/xbin/busybox awk'
    alias route='/system/xbin/busybox route'
    
    OLDGW=`netstat -rn | grep ^0\.0\.0\.0 | awk '{print $2}'`
    
    """)
    
    downscript_header=textwrap.dedent("""\
    #!/bin/sh
    alias route='/system/xbin/busybox route'
    
    """)
    
    up=StringIO.StringIO()
    down=StringIO.StringIO()
    
    up.write(upscript_header)
    up.write('\n')
    down.write(downscript_header)
    down.write('\n')
    
    for ip,mask,_ in ip_data:
        up.write('route add -net %s netmask %s gw $OLDGW\n'%(ip,mask))
        down.write('route del -net %s netmask %s\n'%(ip,mask))
    
    return {'vpnup.sh':up.getvalue(),'vpndown.sh':down.getvalue()}

def zipit(data):
    zfile=StringIO.StringIO()
    z=zipfile.ZipFile(zfile,'w',zipfile.ZIP_DEFLATED)
    for fn,d in data.iteritems():
            z.writestr(fn,d)
    z.close()
    return zfile.getvalue()
    
if __name__ == '__main__':
    generate_all()