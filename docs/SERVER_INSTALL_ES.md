# Deploy en servidor (Hostinger VPS) - Ionic + Node

## 1) Instalar Node.js 20+

```bash
sudo apt update
sudo apt install -y curl
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2) Subir proyecto

```bash
git clone <URL_DEL_REPO> /opt/friolam
cd /opt/friolam
npm install
```

## 3) Ejecutar

```bash
npm start
```

## 4) Producción (recomendado)

Usar PM2 + Nginx reverse proxy a puerto 8000.
