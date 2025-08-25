#!/bin/bash

# Pedir al usuario los valores de las variables necesarias
read -p "Ingrese el subdominio de su ISPbrain: " subdomain
read -p "Ingrese el id de la cuenta de AltWha: " account
read -p "Ingrese el usuario de API ISPbrain: " user
read -p "Ingrese la contraseña de API ISPbrain: " password

# Instalar docker
apt-get update
apt-get install -y \
    ca-certificates \
    curl \
    gnupg

if ! test -f /etc/apt/keyrings/docker.gpg; then
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
fi

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin python3-pip

pip3 install --break-system-packages requests-cache
pip3 install --break-system-packages python-dotenv

mkdir /root/altwha
mkdir /root/altwha/$subdomain$account

cd /root/altwha/$subdomain$account

curl -L "https://raw.githubusercontent.com/Crenein/AltWha/refs/heads/master/main.py?token=GHSAT0AAAAAAC3KN7BKP3LD6TPNIXYUL5GI2FMQNUQ" -o main.py

mkdir /root/altwha/$subdomain$account/log

echo "ISPBRAIN_SUBDOMAIN=$subdomain" > /root/altwha/$subdomain$account/.env
echo "ISPBRAIN_ACCOUNT=$account" >> /root/altwha/$subdomain$account/.env
echo "ISPBRAIN_USER=$user" >> /root/altwha/$subdomain$account/.env
echo "ISPBRAIN_PASSWORD=$password" >> /root/altwha/$subdomain$account/.env

# Crear cron job para ejecutar main.py al iniciar el sistema
(crontab -l 2>/dev/null; echo "@reboot cd /root/altwha/$subdomain$account && python3 main.py") | crontab -

# Login
docker run -v /root/altwha/$subdomain$account/mudslide:/usr/src/app/cache -it robvanderleek/mudslide login
