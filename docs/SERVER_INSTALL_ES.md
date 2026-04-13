# Manual de despliegue (Web App Friolam)

Esta versión corre como web app con formularios por rol y dashboard.

## Pasos rápidos

```bash
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip
sudo adduser --system --group --home /opt/friolam friolam
sudo mkdir -p /opt/friolam/app && sudo chown -R friolam:friolam /opt/friolam
sudo -u friolam -H git clone <URL_DEL_REPO> /opt/friolam/app
sudo -u friolam -H bash -lc 'cd /opt/friolam/app && python3 -m venv .venv && source .venv/bin/activate && pip install -e .'
```

Ejecutar:

```bash
sudo -u friolam -H bash -lc 'cd /opt/friolam/app && source .venv/bin/activate && friolam-web'
```

Rutas clave:

- `/dashboard`
- `/tecnico`
- `/administrador`
- `/gerente`

Base de datos archivo:

- `/opt/friolam/app/data/friolam_gigante.db`
