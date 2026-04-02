# Manual de instalación de Friolam en un servidor (Ubuntu 22.04/24.04)

Este manual explica cómo preparar un servidor Linux, desplegar Friolam y dejarlo ejecutándose como servicio con `systemd`.

> Si usas otra distro, los pasos son muy similares pero pueden cambiar los comandos de paquetes.

## 1) Requisitos previos

- Servidor con Ubuntu 22.04+.
- Usuario con permisos `sudo`.
- Acceso SSH al servidor.
- Puerto abierto para SSH (`22`) y, si expondrás API/web, el puerto de tu app (por ejemplo `8000`) o un reverse proxy (`80/443`).

## 2) Actualizar sistema e instalar dependencias

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
```

Verifica versiones:

```bash
python3 --version
git --version
```

## 3) Crear usuario de servicio (recomendado)

```bash
sudo adduser --system --group --home /opt/friolam friolam
```

Esto crea un usuario sin login interactivo para ejecutar la app de forma más segura.

## 4) Descargar el proyecto

```bash
sudo mkdir -p /opt/friolam/app
sudo chown -R friolam:friolam /opt/friolam
sudo -u friolam -H git clone <URL_DEL_REPOSITORIO> /opt/friolam/app
```

Ejemplo de actualización futura:

```bash
sudo -u friolam -H bash -lc 'cd /opt/friolam/app && git pull --ff-only'
```

## 5) Crear entorno virtual e instalar Friolam

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
'
```

Prueba rápida:

```bash
sudo -u friolam -H bash -lc 'cd /opt/friolam/app && source .venv/bin/activate && friolam'
```

Si todo está bien, deberías ver un mensaje similar a:

`Friolam is set up and running (v0.1.0).`

## 6) Configuración con variables de entorno (plantilla)

Crea archivo de entorno:

```bash
sudo -u friolam -H bash -lc 'cat > /opt/friolam/app/.env <<"ENV"
# Variables de entorno para Friolam
APP_ENV=production
# APP_PORT=8000
ENV'
```

> Ajusta estas variables según evolucione la aplicación.

## 7) Crear servicio systemd

Crea `/etc/systemd/system/friolam.service`:

```ini
[Unit]
Description=Friolam service
After=network.target

[Service]
Type=simple
User=friolam
Group=friolam
WorkingDirectory=/opt/friolam/app
EnvironmentFile=/opt/friolam/app/.env
ExecStart=/opt/friolam/app/.venv/bin/friolam
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Recarga y arranca:

```bash
sudo systemctl daemon-reload
sudo systemctl enable friolam
sudo systemctl start friolam
```

Ver estado y logs:

```bash
sudo systemctl status friolam
sudo journalctl -u friolam -f
```

## 8) Actualizar sin detener demasiado tiempo

```bash
sudo -u friolam -H bash -lc '
cd /opt/friolam/app
git pull --ff-only
source .venv/bin/activate
pip install -e .
'
sudo systemctl restart friolam
```

## 9) Verificaciones de salud sugeridas

- Proceso activo: `systemctl is-active friolam`
- Últimos logs: `journalctl -u friolam -n 100 --no-pager`
- Si hay endpoint HTTP (futuro): `curl -f http://127.0.0.1:8000/health`

## 10) Problemas comunes

1. **`ModuleNotFoundError` al arrancar**
   - Verifica que instalaste con `pip install -e .` dentro del venv correcto.
2. **Permisos denegados**
   - Revisa propiedad: `sudo chown -R friolam:friolam /opt/friolam`.
3. **Servicio en bucle de reinicio**
   - Inspecciona logs con `journalctl -u friolam -e`.
4. **No responde externamente**
   - Revisa firewall (`ufw status`) y/o reverse proxy.

## 11) Hardening mínimo recomendado

- Mantener sistema actualizado (`apt upgrade`).
- No ejecutar con `root`.
- Limitar puertos abiertos.
- Usar HTTPS (Nginx/Caddy + Let's Encrypt) cuando exista interfaz HTTP pública.
- Añadir backups automáticos del código/configuración.

---

Si quieres, en el siguiente paso puedo prepararte un **manual equivalente para Docker + docker-compose** para despliegues más portables.
