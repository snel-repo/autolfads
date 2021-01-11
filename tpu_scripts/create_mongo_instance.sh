#! /bin/bash

gcloud compute instances create mongo --machine-type=f1-micro --zone=us-central1-f --scopes=cloud-platform  --tags=mongo-tag --metadata startup-script='#! /bin/bash
apt-get install dirmngr
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo "deb http://repo.mongodb.org/apt/debian stretch/mongodb-org/4.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
apt-get update
sudo apt-get install -y mongodb-org
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
'

sleep 4m
echo "creating tmux session"
session_name_acct="mongo_session_acct"
session_name="mongo_session"
internal_ip=$(gcloud --format="value(INTERNAL_IP)" compute instances list --filter='name:mongo')
tmux kill-session -t $session_name 2>/dev/null
tmux kill-session -t $session_name_acct 2>/dev/null

tmux new-session -d -s $session_name gcloud compute ssh mongo
tmux send-keys "mkdir db; cd db; mkdir db_data; cd" C-m
tmux send-keys "mongod --dbpath db/db_data" C-m
tmux set -t $session_name remain-on-exit on 2>/dev/null
sleep 1m

tmux new-session -d -s $session_name_acct gcloud compute ssh mongo
tmux send-keys "mongo --host 127.0.0.1:27017" C-m
tmux send-keys "use admin" C-m
tmux send-keys "db.createUser({user: \"pbt_user\", pwd: \"pbt0Pass\", roles: [ { role: \"userAdminAnyDatabase\", db: \"admin\" } ]})" C-m
tmux send-keys "db.grantRolesToUser(\"pbt_user\", [{ role: \"readWriteAnyDatabase\", db: \"admin\" }])" C-m
tmux send-keys "quit()" C-m
sleep 1m

tmux send-keys -t $session_name C-c
tmux kill-session -t $session_name 2>/dev/null
tmux send-keys -t $session_name_acct "mongod --auth --dbpath db/db_data --bind_ip ${internal_ip}" C-m
tmux set -t $session_name_acct remain-on-exit on 2>/dev/null


