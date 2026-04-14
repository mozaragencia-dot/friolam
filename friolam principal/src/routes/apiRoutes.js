const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { db, logAudit } = require('../models/repositories');
const { requireAuth, requireRole } = require('../middleware/auth');

const uploadDir = path.join(__dirname, '../public/uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });
const upload = multer({ dest: uploadDir });

const router = express.Router();
router.use(requireAuth);

router.get('/api/me/services', requireRole('technician'), (req, res) => {
  const rows = db.prepare(`SELECT s.*, c.name client_name, sc.local_name, sc.address
  FROM services s JOIN clients c ON c.id=s.client_id JOIN subclients sc ON sc.id=s.subclient_id
  WHERE technician_id=? ORDER BY scheduled_date ASC`).all(req.user.id);
  res.json(rows);
});

router.get('/api/services/:id', (req, res) => {
  const service = db.prepare('SELECT * FROM services WHERE id=?').get(req.params.id);
  if (!service) return res.status(404).json({ error: 'not_found' });
  if (req.user.role === 'technician' && service.technician_id !== req.user.id) return res.status(403).json({ error: 'forbidden' });
  const machines = db.prepare('SELECT * FROM service_machines WHERE service_id=?').all(req.params.id);
  return res.json({ ...service, machines });
});

router.post('/api/services/update-technical', requireRole('technician'), (req, res) => {
  const { id_service, client_phone, fantasy_name, maintenance_data, postmix_data, observations, closing_data } = req.body;
  const service = db.prepare('SELECT * FROM services WHERE id=? AND technician_id=?').get(id_service, req.user.id);
  if (!service) return res.status(404).json({ error: 'service_not_found' });

  db.prepare(`UPDATE services
      SET client_phone=?, fantasy_name=?, maintenance_data=?, postmix_data=?, observations=?, closing_data=?, updated_at=CURRENT_TIMESTAMP
      WHERE id=?`).run(
    client_phone ?? service.client_phone,
    fantasy_name ?? service.fantasy_name,
    maintenance_data ?? service.maintenance_data,
    postmix_data ?? service.postmix_data,
    observations ?? service.observations,
    closing_data ?? service.closing_data,
    id_service
  );
  logAudit(req.user.id, 'update', 'service_technical', id_service, 'Actualización técnica desde app');
  res.json({ ok: true });
});

router.post('/api/services/machines', requireRole('technician'), (req, res) => {
  const { service_id, machine_name, model, serial, brand, diagnosis, work_done, spare_parts, observations, machine_status } = req.body;
  const service = db.prepare('SELECT id FROM services WHERE id=? AND technician_id=?').get(service_id, req.user.id);
  if (!service) return res.status(403).json({ error: 'forbidden' });
  const result = db.prepare(`INSERT INTO service_machines(service_id,machine_name,model,serial,brand,diagnosis,work_done,spare_parts,observations,machine_status)
    VALUES(?,?,?,?,?,?,?,?,?,?)`).run(service_id, machine_name, model, serial, brand, diagnosis, work_done, spare_parts, observations, machine_status);
  logAudit(req.user.id, 'create', 'service_machine', result.lastInsertRowid, 'Máquina agregada desde app');
  res.json({ ok: true, id: result.lastInsertRowid });
});

router.post('/api/services/upload', requireRole('technician'), upload.single('file'), (req, res) => {
  const { service_id, media_type } = req.body;
  const service = db.prepare('SELECT id FROM services WHERE id=? AND technician_id=?').get(service_id, req.user.id);
  if (!service) return res.status(403).json({ error: 'forbidden' });
  const normalizedType = ['photo', 'signature_tech', 'signature_client'].includes(media_type) ? media_type : 'photo';
  db.prepare('INSERT INTO service_media(service_id,media_type,file_path) VALUES(?,?,?)').run(service_id, normalizedType, req.file.filename);
  res.json({ ok: true, file: req.file.filename });
});

router.post('/api/services/status', (req, res) => {
  const { id_service, status } = req.body;
  if (id_service === undefined || status === undefined) {
    return res.status(400).json({ error: 'id_service and status are required' });
  }
  const service = db.prepare('SELECT * FROM services WHERE id = ?').get(id_service);
  if (!service) return res.status(404).json({ error: 'service_not_found' });
  if (req.user.role === 'technician' && service.technician_id !== req.user.id) return res.status(403).json({ error: 'forbidden' });
  db.prepare('UPDATE services SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?').run(status, id_service);
  logAudit(req.user.id, 'status_change', 'service', id_service, `status=${status}`);
  return res.json({ ok: true, id_service, status });
});

module.exports = router;
