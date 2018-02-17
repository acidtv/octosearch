#/bin/sh

set -e

if [ "$EUID" -ne 0 ]
  then echo "Please run as root. Try: sudo !!"
  exit 1
fi

# install prereqs
apt update
apt install -y apt-transport-https openjdk-9-jre

# add elastic apt repo
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list

# install elastic
apt-get update 
apt-get install -y elasticsearch

# try starting elastic
systemctl start elasticsearch

echo ""
echo "Elasticsearch was installed and started."
echo "Type 'journalctl -f' to check the systemd logs."
echo ""
echo "Oh, and if elastic refuses to start you probably need to type 'sudo sysctl -w vm.max_map_count=262144', because elasticsearch insists on that."
echo "If this is a container you need to execute that on the host."
