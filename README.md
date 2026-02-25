## 🔐 Password Manager Self-Hosted

Un password manager sicuro e self-hosted su Raspberry Pi, accessibile da remoto tramite Tailscale con connessione HTTPS.

## ✨ Caratteristiche
* **Self-Hosted:** I dati non lasciano mai il tuo Raspberry Pi.
* **Accesso Remoto Sicuro:** Tramite Tailscale VPN, accessibile da smartphone e PC.
* **HTTPS Nativo:** Reverse proxy Nginx configurato con certificati SSL forniti da Tailscale.
* **Sempre Attivo:** Gestito tramite demone `systemd` per l'esecuzione in background.

---

## 🏗️ Architettura

1. **Tailscale:** Crea un tunnel sicuro, fornendo un IP privato (`100.x.x.x`) e un dominio MagicDNS (es. `tuo-dominio.ts.net`).
2. **Nginx (Reverse Proxy):** Ascolta in HTTPS, gestisce i certificati SSL e passa il traffico all'applicazione locale in modo invisibile.
3. **Python / Flask (Backend):** L'applicazione gira in background sulla porta `5000` (`127.0.0.1:5000`).
4. **SQLite:** Database per memorizzare le credenziali in modo sicuro.

---

## ⚙️ Prerequisiti

- Raspberry Pi OS
- Python 3.7+
- Tailscale 
- Nginx

## 🚀 Installazione

### 1. Aggiorna il sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Installa le dipendenze

```bash
# Python e pip
sudo apt install python3 python3-pip python3-venv -y

# Nginx
sudo apt install nginx -y

# Git (se necessario)
sudo apt install git -y
```

### 3. Installa Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Segui le istruzioni per autenticare il dispositivo.

### 4. Scarica il progetto

```bash
cd /home/pi
git clone  password-manager
cd password-manager
```

### 5. Crea ambiente virtuale Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Ottieni i certificati SSL da Tailscale

Vai su [Tailscale Admin Console](https://login.tailscale.com/admin/machines) e:

1. Trova il tuo Raspberry Pi
2. Clicca sui tre puntini → **Manage certificates**
3. Scarica `cert.pem` e `key.pem`

Copia i certificati sul Raspberry Pi:

```bash
mkdir -p /home/pi/certs
# Copia i file cert.pem e key.pem in /home/pi/certs/
chmod 644 /home/pi/certs/cert.pem
chmod 600 /home/pi/certs/key.pem
```

## ⚙️ Configurazione

### 1. Configura l'applicazione Flask

Modifica `app.py` per eseguire in modalità localhost:

```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
```

### 2. Configura Nginx

Crea il file di configurazione:

```bash
sudo nano /etc/nginx/sites-available/vault
```

Incolla questa configurazione (sostituisci i valori):

```nginx
server {
    listen 443 ssl;
    server_name YOUR-HOSTNAME.tailnet-XXXX.ts.net;

    # Certificati SSL di Tailscale
    ssl_certificate /home/pi/certs/cert.pem;
    ssl_certificate_key /home/pi/certs/key.pem;

    # Proxy verso Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

}

Attiva la configurazione:

```bash
sudo ln -s /etc/nginx/sites-available/vault /etc/nginx/sites-enabled/
sudo nginx -t  # Verifica configurazione
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3. Crea il servizio systemd

```bash
sudo nano /etc/systemd/system/vault.service
```

Incolla questa configurazione:

```ini
[Unit]
Description=Password Manager 
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/password-manager
Environment="PATH=/home/pi/password-manager/venv/bin"
ExecStart=/home/pi/password-manager/venv/bin/python3 /home/pi/password-manager/app.py

# Restart automatico in caso di crash
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Attiva il servizio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vault.service
sudo systemctl start vault.service
```

Verifica lo stato:

```bash
sudo systemctl status vault.service
```

## 🎯 Utilizzo

### Accesso all'applicazione

1. **Da PC/Mobile connesso a Tailscale:**
   ```
   https://YOUR-HOSTNAME.tailnet-XXXX.ts.net
   ```

2. **Primo accesso:**
   - Imposta una password forte (master password)

3. **Gestione password:**
   - Aggiungi nuove credenzial
   - Genera password sicure

### Comandi utili

```bash
# Visualizza log dell'applicazione
sudo journalctl -u vault.service -f

# Riavvia il servizio
sudo systemctl restart vault.service

# Ferma il servizio
sudo systemctl stop vault.service

# Verifica stato Nginx
sudo systemctl status nginx

# Ricarica configurazione Nginx (senza downtime)
sudo nginx -s reload

# Test configurazione Nginx
sudo nginx -t
```
