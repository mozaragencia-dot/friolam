# Manual de instalación de Friolam Web App + Backend (Ubuntu 22.04/24.04)

Esta versión incluye:

- Web app por rol (`/tecnico`, `/administrador`, `/gerente`)
- Backend SQLite embebido
- API (`/api/roles`, `/api/tecnico`, `/api/administrador`, `/api/gerente`)

## 1) Instalar dependencias base

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
```

## 2) Preparar carpeta y usuario

```bash
sudo adduser --system --group --home /opt/friolam friolam
sudo mkdir -p /opt/friolam/app
sudo chown -R friolam:friolam /opt/friolam
```

## 3) Copiar código (Git o SFTP)

Con Git:

```bash
sudo -u friolam -H git clone <URL_DEL_REPOSITORIO> /opt/friolam/app
```

Con SFTP: sube el proyecto completo a `/opt/friolam/app`.

## 4) Instalar app

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
'
```

## 5) Ejecutar y validar backend

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
source .venv/bin/activate
friolam-web
'
```

En otra terminal:

```bash
curl http://127.0.0.1:8000/api/roles
curl http://127.0.0.1:8000/api/administrador
curl http://127.0.0.1:8000/api/gerente
```

## 6) Configurar systemd

Crea `/etc/systemd/system/friolam.service`:

```ini
[Unit]
Description=Friolam Web App + Backend
After=network.target

[Service]
Type=simple
User=friolam
Group=friolam
WorkingDirectory=/opt/friolam/app
ExecStart=/opt/friolam/app/.venv/bin/friolam-web
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable friolam
sudo systemctl start friolam
sudo systemctl status friolam
```

## 7) Datos del backend

La app crea automáticamente `data/friolam.db` en el `WorkingDirectory`.

Haz backup:

```bash
cp /opt/friolam/app/data/friolam.db /opt/friolam/app/data/friolam.db.bak
```

## 8) Actualizar

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
git pull --ff-only
source .venv/bin/activate
pip install -e .
'
sudo systemctl restart friolam
```
