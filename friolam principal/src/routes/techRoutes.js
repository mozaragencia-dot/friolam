const express = require('express');
const { requireAuth, requireRole } = require('../middleware/auth');
const { db, statusLabels } = require('../models/repositories');

const router = express.Router();
router.use(requireAuth, requireRole('technician'));

router.get('/tech', (req, res) => {
  const stats = db.prepare('SELECT status, COUNT(*) total FROM services WHERE technician_id=? GROUP BY status').all(req.user.id);
  const summary = { pending: 0, done: 0 };
  stats.forEach((s) => {
    if ([0, 1, 2, 3, 4].includes(s.status)) summary.pending += s.total;
    if (s.status === 5) summary.done += s.total;
  });
  res.render('tech/home', { summary, user: req.user });
});

router.get('/tech/services', (req, res) => {
  const services = db.prepare(`SELECT s.*, c.name client_name, sc.local_name, sc.address FROM services s
  JOIN clients c ON c.id=s.client_id JOIN subclients sc ON sc.id=s.subclient_id
  WHERE s.technician_id=? ORDER BY scheduled_date ASC`).all(req.user.id);
  res.render('tech/services', { services, statusLabels });
});

router.get('/tech/services/:id', (req, res) => {
  const service = db.prepare(`SELECT s.*, c.name client_name, sc.local_name, sc.address, sc.phone subclient_phone FROM services s
  JOIN clients c ON c.id=s.client_id JOIN subclients sc ON sc.id=s.subclient_id
  WHERE s.id=? AND s.technician_id=?`).get(req.params.id, req.user.id);
  if (!service) return res.status(404).send('Servicio no encontrado');
  const machines = db.prepare('SELECT * FROM service_machines WHERE service_id=?').all(req.params.id);
  res.render('tech/service-detail', { service, machines, statusLabels });
});

module.exports = router;
