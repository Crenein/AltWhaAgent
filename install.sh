#!/bin/bash

# Instalar docker
apt-get update
apt-get install -y \
    ca-certificates \
    curl \
    gnupg

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Pedir al usuario los valores de las variables necesarias
read -p "Ingrese el subdominio de su ISPbrain: " subdomain
read -p "Ingrese el id de la cuenta de AltWha: " account
read -p "Ingrese el usuario de API ISPbrain: " user
read -p "Ingrese la contraseña de API ISPbrain: " password

# Correr el docker con las variables ingresadas por el usuario
docker run -d \
--env ISPBRAIN_SUBDOMAIN="$subdomain" \
--env ISPBRAIN_ACCOUNT="$account" \
--env ISPBRAIN_USER="$user" \
--env ISPBRAIN_PASSWORD="$password" \
-v /root/.local/share/mudslide:/usr/src/app/cache \
-v log:/root/AltWha/log crenein/altwhasender:v1.0.3
