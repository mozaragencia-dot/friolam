# Manual de despliegue: Friolam con Ionic Dashboard + backend SQLite

## 1) Instalar dependencias

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
```

## 2) Preparar servidor

```bash
sudo adduser --system --group --home /opt/friolam friolam
sudo mkdir -p /opt/friolam/app
sudo chown -R friolam:friolam /opt/friolam
```

## 3) Subir código

```bash
sudo -u friolam -H git clone <URL_DEL_REPO> /opt/friolam/app
```

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

## 5) Ejecutar y validar

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
source .venv/bin/activate
friolam-web
'
```

Validar:

```bash
curl http://127.0.0.1:8000/api/dashboard
```

Abrir interfaz:

- `http://TU_SERVIDOR:8000/ionic`

## 6) Base de datos de archivo

- Archivo principal: `/opt/friolam/app/data/friolam_gigante.db`
- Backup:

```bash
cp /opt/friolam/app/data/friolam_gigante.db /opt/friolam/app/data/friolam_gigante.db.bak
```

## 7) Servicio systemd

`/etc/systemd/system/friolam.service`

```ini
[Unit]
Description=Friolam Ionic Dashboard
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

```bash
sudo systemctl daemon-reload
sudo systemctl enable friolam
sudo systemctl start friolam
sudo systemctl status friolam
```
