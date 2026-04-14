# FRIOLAM principal

Webapp/PWA completa para gestión técnica en terreno, con backend administrativo, app móvil para técnicos, API REST y PDF de hoja de servicio.

## 1) Arquitectura propuesta

- **Backend monolito modular Node.js + Express** (capas: rutas, middleware, modelos/repositorio, servicios).
- **Dashboard admin web** con EJS + CSS responsive.
- **App técnico PWA** con vistas móviles, service worker y manifest instalable.
- **API REST JSON** para app técnico y acciones de estado.
- **Base central** SQLite para demo local + migración SQL compatible MySQL/MariaDB.
- **Módulos**: usuarios/roles, clientes, subclientes, servicios, máquinas, evidencia media, PDF, auditoría.

## 2) Estructura de carpetas

```txt
friolam principal/
├── database/migrations/001_initial.sql
├── docs/
├── scripts/seed.js
├── src/
│   ├── db/database.js
│   ├── middleware/auth.js
│   ├── models/repositories.js
│   ├── public/
│   │   ├── css/app.css
│   │   └── js/app.js
│   ├── routes/
│   │   ├── adminRoutes.js
│   │   ├── apiRoutes.js
│   │   ├── authRoutes.js
│   │   └── techRoutes.js
│   ├── views/
│   │   ├── admin/
│   │   ├── auth/
│   │   ├── tech/
│   │   └── partials/
│   └── server.js
└── package.json
```

## 3) Modelo de base de datos

Tablas principales:
- `users` (admin, technician, supervisor)
- `clients`
- `subclients`
- `services` (tabla central)
- `service_machines` (múltiples máquinas por servicio)
- `service_media` (fotos y firmas)
- `audit_logs`

Estados:
- `0 nuevo`
- `1 asignado`
- `2 en proceso`
- `3 pendiente validación`
- `4 terminado parcial`
- `5 terminado final`

## 4) Flujo completo punta a punta

1. Admin crea servicio (`/admin/services/new`).
2. Servicio se guarda en DB (`services`).
3. Admin asigna técnico (campo `technician_id`, estado pasa a asignado).
4. Técnico entra a `/tech/services` y ve sólo sus tareas.
5. Técnico abre detalle `/tech/services/:id`.
6. Completa mantención, postmix, observaciones, cierre.
7. Registra máquinas y evidencia.
8. Actualiza estado con endpoint body `{id_service,status}`.
9. Backend visualiza y filtra por estado.
10. Se genera PDF en `/Services/view/:id`.

## 5) Endpoints API principales

- `GET /api/me/services` → servicios asignados al técnico autenticado.
- `GET /api/services/:id` → detalle servicio + máquinas.
- `POST /api/services/update-technical` → actualización técnica (restricción de edición aplicada).
- `POST /api/services/machines` → agrega máquina al servicio.
- `POST /api/services/upload` → sube foto/firma.
- `POST /api/services/status` → cambia estado por `id_service` desde body.

## 6) Restricciones de negocio implementadas

- El técnico sólo puede editar desde API:
  - `client_phone`
  - `fantasy_name`
  - + campos técnicos (`maintenance_data`, `postmix_data`, etc.)
- No puede editar client/subclient base ni reasignación.
- En cambio de estado se valida pertenencia del técnico al servicio.

## 7) Postmix (estructura mínima)

El campo `postmix_data` almacena checklist consolidado (JSON/texto serializado), incluyendo:
- carbonatador, bomba, tableros, conexiones, agua, gas, siropes, fugas
- limpieza/sanitización/prueba/calibración
- presión agua, presión CO2, temperatura
- estado final, observaciones, repuestos, nueva visita

## 8) Instalación y uso

```bash
cd "friolam principal"
npm install
npm run seed
npm run dev
```

Accesos demo:
- Admin: `admin@friolam.cl` / `Admin123*`
- Técnico: `tec1@friolam.cl` / `Tec123*`
- Supervisor: `super@friolam.cl` / `Super123*`

## 9) Implementación por fases (roadmap)

### Fase 1 (base funcional)
- autenticación/roles
- clientes/subclientes
- crear y asignar servicios
- filtros y estados en admin

### Fase 2 (app técnico)
- listado, detalle, formulario técnico
- mantención + postmix
- máquinas, fotos, firmas
- cambio de estado desde body

### Fase 3 (cierre profesional)
- PDF profesional con branding
- reportes avanzados/exportaciones
- historial por cliente/máquina
- auditoría extendida y observabilidad

## 10) Recomendaciones para producción esta noche

- Migrar DB a MySQL/MariaDB usando `database/migrations/001_initial.sql`.
- Configurar `JWT_SECRET` robusto y HTTPS.
- Usar almacenamiento S3/Cloud para fotos/firmas.
- Añadir validaciones de input (Joi/Zod) y rate-limit.
- Separar front React/Ionic si se requiere app híbrida nativa en próxima iteración.
