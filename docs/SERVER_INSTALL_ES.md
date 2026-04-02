# Manual de instalación de Friolam Web App en servidor (Ubuntu 22.04/24.04)

Este manual está orientado a la nueva versión web con vistas separadas para:

- Técnico: `/tecnico`
- Administrador: `/administrador`
- Gerente: `/gerente`

## 1) Instalar dependencias base

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
```

## 2) Preparar carpeta y usuario de servicio

```bash
sudo adduser --system --group --home /opt/friolam friolam
sudo mkdir -p /opt/friolam/app
sudo chown -R friolam:friolam /opt/friolam
```

## 3) Clonar el proyecto

```bash
sudo -u friolam -H git clone <URL_DEL_REPOSITORIO> /opt/friolam/app
```

## 4) Crear entorno virtual e instalar app

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
'
```

## 5) Prueba rápida manual

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
source .venv/bin/activate
friolam-web
'
```

Si arranca bien, verás: `Friolam web app escuchando en http://0.0.0.0:8000`.

## 6) Configurar como servicio systemd

Crea `/etc/systemd/system/friolam.service` con:

```ini
[Unit]
Description=Friolam Web App
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

Aplicar cambios:

```bash
sudo systemctl daemon-reload
sudo systemctl enable friolam
sudo systemctl start friolam
```

Verificar:

```bash
sudo systemctl status friolam
curl -I http://127.0.0.1:8000/
curl -I http://127.0.0.1:8000/tecnico
curl -I http://127.0.0.1:8000/administrador
curl -I http://127.0.0.1:8000/gerente
```

## 7) (Opcional) Exponer con Nginx en 80/443

Si quieres acceso público con dominio y SSL, monta Nginx como reverse proxy hacia `127.0.0.1:8000`.

## 8) Actualización

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
git pull --ff-only
source .venv/bin/activate
pip install -e .
'
sudo systemctl restart friolam
```

---

Si quieres, te puedo dejar también el archivo exacto de Nginx para producción con HTTPS.

## 9) ¿Se puede subir por FTP a cualquier servidor?

Sí, **se puede**, pero no es lo más recomendable para despliegues repetibles.

### Cuándo sí te sirve FTP/SFTP

- Tienes hosting sencillo sin acceso Git.
- Solo necesitas una instalación básica/manual.

### Recomendación

- Mejor usar **SFTP** (más seguro) en vez de FTP plano.
- Mantener en el servidor una carpeta como `/opt/friolam/app` y subir allí el proyecto.

### Flujo mínimo por SFTP

1. Subir archivos del proyecto a `/opt/friolam/app`.
2. Entrar por SSH y crear entorno virtual:
   ```bash
   cd /opt/friolam/app
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -e .
   ```
3. Ejecutar prueba:
   ```bash
   .venv/bin/friolam-web
   ```
4. Configurar `systemd` como en la sección anterior para que quede persistente.

### Limitaciones de FTP

- No tienes control de versiones como con Git.
- Es más fácil sobrescribir archivos por error.
- Más difícil automatizar despliegues.

Si quieres, te preparo una variante del manual específica para **hosting compartido (cPanel/Plesk)**.

