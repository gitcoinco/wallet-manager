'''
    Copyright (C) 2017 Gitcoin Core 

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

'''

BRANCH=$1
DISTID=$2
# deploy script
# assumes that gitcoin repo lives at $HOME/gitcoin
# and that gitcoinenv is the virtualenv under which it lives

# setup
cd 
cd gitcoin/coin
source ../gitcoinenv/bin/activate

# pull from git
git add .
git stash
# If no $BRANCH is specified, it will use the current one
git checkout $BRANCH
git pull origin $BRANCH

#deploy hooks
echo "- install req"
pip install -r requirements/base.txt
echo "- install crontab"
crontab scripts/crontab
cd app
echo "- collect static"
./manage.py collectstatic --noinput -i other
rm -Rf ~/gitcoin/coin/app/static/other
echo "- db"
./manage.py migrate
./manage.py createcachetable

# let gunicorn know its ok to restart
echo "- gunicorn"
sudo systemctl restart gunicorn

# invalidate cloudfront
if [ $DISTID ]; then
    aws cloudfront create-invalidation --distribution-id $DISTID --invalidation-batch="Paths={Quantity=1,Items=["/*"]},CallerReference=$(date)"
fi

# ping google
cd ~/gitcoin/coin; bash scripts/run_management_command.bash ping_google

