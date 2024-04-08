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

apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

mkdir /root/altwha
mkdir /root/altwha/$subdomain$account
mkdir /root/altwha/$subdomain$account/log

# Correr el docker con las variables ingresadas por el usuario
docker run --name $subdomain$account -d \
--env ISPBRAIN_SUBDOMAIN="$subdomain" \
--env ISPBRAIN_ACCOUNT="$account" \
--env ISPBRAIN_USER="$user" \
--env ISPBRAIN_PASSWORD="$password" \
--restart=always \
-v /root/altwha/$subdomain$account/mudslide:/usr/src/app/cache \
-v /root/altwha/$subdomain$account/log:/opt/AltWha/log crenein/altwhasender:v1.5
