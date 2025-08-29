import time
import datetime
import requests
import os
import subprocess
from dotenv import load_dotenv

#Cargar variables de entorno
load_dotenv()
login = {"username": os.environ['ISPBRAIN_USER'], "password": os.environ['ISPBRAIN_PASSWORD']}
base_url = "https://"+os.environ['ISPBRAIN_SUBDOMAIN']+".ispbrain.io:4443/api/v2"
account_id = os.environ['ISPBRAIN_ACCOUNT']

#Validar dia y hora
def is_valid_time():
    now = datetime.datetime.now()
    if now.weekday() < 6 and 8 <= now.hour < 20:
        return True
    return False

#Obtener token de ISPbrain
def get_ispb_token():
    try:
        response = requests.post(base_url+"/auth", json = login)
        if response.status_code == 200:
            token = response.json()['token_access']
            return token
        else:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(str(now) + " get_ispb_token " + str(response.status_code) + '\n')
            return False

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_ispb_token " + repr(e) + '\n')
        return False
    
#Obtener mensajes de la cuenta
def get_messages(token):
    headers = {"Authorization": token}
    try:
        params={
            "page[size]": 100,
            "page[number]": 1,
            "filter[account_id]": account_id,
            "filter[cancelled]": 0,
            "filter[deleted]": 0,
            "filter[status]": 0
        }
        response = requests.get(base_url+'/altwha_messages', params = params, headers = headers)
        if response.status_code == 200:
            messages = response.json()['data']
            return messages
        else:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(str(now) + " get_messages " + str(response.status_code) + '\n')
            return False

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_messages " + repr(e) + '\n')
        return False
    
#Obtener mensajes de la cuenta
def get_noprocess_messages(token):
    headers = {"Authorization": token}
    try:
        params={
            "page[size]": 100,
            "page[number]": 1,
            "filter[account_id]": account_id,
            "filter[cancelled]": 0,
            "filter[deleted]": 0,
            "filter[status]": 2
        }
        response = requests.get(base_url+'/altwha_messages', params = params, headers = headers)
        if response.status_code == 200:
            messages = response.json()['data']
            return messages
        else:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(str(now) + " get_noprocess_messages " + str(response.status_code) + '\n')
            return False

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_messages " + repr(e) + '\n')
        return False
    
#Success send message
def success_send_message(token, message_id):
    headers = {"Authorization": token}
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    send_at = date+' '+time
    try:
        response = requests.patch(base_url+'/altwha_messages/'+str(message_id), json = {"send_at": send_at, "status": 1}, headers = headers)
        if response.status_code == 200:
            return True
        else:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(str(now) + " success_send_message " + str(response.status_code) + '\n')
            return False

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " success_send_message " + repr(e) + '\n')
        return False

#Error send message
def error_send_message(token, message_id):
    headers = {"Authorization": token}
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    send_at = date+' '+time
    try:
        response = requests.patch(base_url+'/altwha_messages/'+str(message_id), json = {"send_at": send_at, "status": 2}, headers = headers)
        if response.status_code == 200:
            return True
        else:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(str(now) + " error_send_message " + str(response.status_code) + '\n')
            return False

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " error_send_message " + repr(e) + '\n')
        return False
    
def send_messages(token, message):
    try:
        message_id = message['id']
        text = message['message']
        phone = str(message["phone"])
        command = ['docker', 'run', '--rm', '-v', f'{os.getcwd()}/mudslide:/usr/src/app/cache', 'robvanderleek/mudslide', 'send', phone, text]
        commandout = subprocess.check_output(command, timeout=60, stderr=subprocess.PIPE)
        if 'success' in commandout.decode("utf-8"):
            success_send_message(token, message_id)
        else:
            error_send_message(token, message_id)

    except subprocess.CalledProcessError as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(f"{now} Docker command failed: {e.returncode} - {e.stderr.decode('utf-8') if e.stderr else 'No stderr'}\n")
        error_send_message(token, message_id)
        return False

def docker_kill():
    try:
        # Buscar todos los contenedores que usen la imagen robvanderleek/mudslide
        ps_command = ['docker', 'ps', '--filter', 'ancestor=robvanderleek/mudslide', '--format', '{{.ID}}']
        container_ids = subprocess.check_output(ps_command, timeout=30, stderr=subprocess.PIPE).decode('utf-8').strip().split('\n')
        
        # Matar cada contenedor encontrado
        for container_id in container_ids:
            if container_id:  # Verificar que no esté vacío
                kill_command = ['docker', 'kill', container_id]
                subprocess.check_output(kill_command, timeout=30, stderr=subprocess.PIPE)
                
    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(f"{now} Docker kill failed: {repr(e)}\n")
        return False

if __name__ == "__main__":
    
    while True:
            try:
                if is_valid_time():
                    token = get_ispb_token()
                    if token:
                        messages = get_messages(token) + get_noprocess_messages(token)
                        if messages:
                            for message in messages:
                                send_messages(token, message)
            except Exception as e:
                error_send_message(token, message['id'])
                with open('log/error.txt', 'a', encoding='utf-8') as log:
                    now = datetime.datetime.now()
                    log.write(str(now) + " main " + repr(e) + '\n')
            docker_kill()
            time.sleep(120)
