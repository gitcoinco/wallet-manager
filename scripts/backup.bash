#!/bin/bash

: <<'END'
Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
END

date
BACKUPSTR=`date +"%Y%m%d"`
MONTH=`date +"%m"`
DAY=`date +"%d"`
YEAR=`date +"%Y"`
PG_DUMP="/usr/lib/postgresql/9.6/bin/pg_dump"
export PGPASSWORD=$(cat app/app/.env | grep "DATABASE_URL" | awk -F "=" '{print $2}' | awk -F "@" '{print $1}' | awk -F ":" '{print $3}')
export HOST=$(cat app/app/.env | grep "DATABASE_URL" | awk -F "=" '{print $2}' | awk -F "@" '{print $2}' | awk -F ":" '{print $1}')
IS_PROD=$(cat app/app/.env | grep ENV | grep prod | wc -l)
if [ "$IS_PROD" -eq "1" ]; then
    $PG_DUMP gitcoin -U gitcoin -h $HOST | s3cmd put - s3://gitcoinbackups/$YEAR/$MONTH/$DAY/$BACKUPSTR-$(hostname).sql
else
    echo "not prod"
fi


