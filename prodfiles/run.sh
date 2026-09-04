#!/bin/bash
appdir=/usr/src/app
bash ${appdir}/migration/migration.sh ${appdir}/migration > /tmp/migration.txt
python ${appdir}/src/web.py &
/usr/sbin/crond -f 
