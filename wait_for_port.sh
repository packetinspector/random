#!/bin/bash

wait_mysql() {

SERVER=`sed -n 's/.*<host>\([^<]*\)<\/host>$/\1/p' /home/osmc/.kodi/userdata/advancedsettings.xml | head -1`
PORT=`sed -n 's/.*<port>\([^<]*\)<\/port>$/\1/p' /home/osmc/.kodi/userdata/advancedsettings.xml | head -1`
if [ -z "$PORT" ]
then
        PORT=3306
fi

if [ -z "$SERVER" ]
then
        echo "No MySQL Configured. Skipping."
else
        echo "Testing mysql server: $SERVER:$PORT"
        #while ! ping -c1 -w1 $SERVER &>/dev/null
        while ! timeout 1 cat < /dev/null > /dev/tcp/$SERVER/$PORT
        do
                echo -n "."
                sleep 1
        done
        echo "MySQL Up"
        exit 1
fi

}

wait_mysql
