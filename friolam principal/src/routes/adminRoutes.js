const express = require('express');
const dayjs = require('dayjs');
const PDFDocument = require('pdfkit');
const { db, statusLabels, logAudit, getDashboardStats } = require('../models/repositories');
const { requireAuth, requireRole } = require('../middleware/auth');

const router = express.Router();
router.use(requireAuth, requireRole('admin', 'supervisor'));

router.get('/admin', (req, res) => {
  res.render('admin/dashboard', { stats: getDashboardStats(), statusLabels, user: req.user });
});

router.get('/admin/services', (req, res) => {
  const { status, technician_id, client_id } = req.query;
  let query = `SELECT s.*, c.name client_name, sc.local_name, u.name technician_name
               FROM services s
               JOIN clients c ON c.id = s.client_id
               JOIN subclients sc ON sc.id = s.subclient_id
               LEFT JOIN users u ON u.id = s.technician_id
               WHERE 1=1`;
  const params = [];
  if (status !== undefined && status !== '') { query += ' AND s.status = ?'; params.push(status); }
  if (technician_id) { query += ' AND s.technician_id = ?'; params.push(technician_id); }
  if (client_id) { query += ' AND s.client_id = ?'; params.push(client_id); }
  query += ' ORDER BY s.created_at DESC';
  const services = db.prepare(query).all(...params);
  const technicians = db.prepare("SELECT id, name FROM users WHERE role='technician'").all();
  const clients = db.prepare('SELECT id, name FROM clients').all();
  res.render('admin/services', { services, technicians, clients, statusLabels, filters: req.query });
});

router.post('/admin/services', (req, res) => {
  const payload = req.body;
  const result = db.prepare(`INSERT INTO services
    (service_name,ticket,invoice,client_id,subclient_id,technician_id,status,service_type,scheduled_date,scheduled_time,observations,client_phone,fantasy_name)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).run(
    payload.service_name,
    payload.ticket,
    payload.invoice,
    payload.client_id,
    payload.subclient_id,
    payload.technician_id || null,
    payload.technician_id ? 1 : 0,
    payload.service_type,
    payload.scheduled_date,
    payload.scheduled_time,
    payload.observations,
    payload.client_phone,
    payload.fantasy_name
  );
  logAudit(req.user.id, 'create', 'service', result.lastInsertRowid, JSON.stringify(payload));
  res.redirect('/admin/services');
});

router.get('/admin/services/new', (_req, res) => {
  const clients = db.prepare('SELECT id, name FROM clients').all();
  const subclients = db.prepare('SELECT id, local_name, client_id, phone, fantasy_name FROM subclients').all();
  const technicians = db.prepare("SELECT id, name FROM users WHERE role='technician'").all();
  res.render('admin/service-new', { clients, subclients, technicians });
});

router.get('/admin/services/:id', (req, res) => {
  const service = db.prepare(`SELECT s.*, c.name client_name, sc.local_name, sc.address, sc.commune, sc.city, u.name technician_name
    FROM services s
    JOIN clients c ON c.id = s.client_id
    JOIN subclients sc ON sc.id = s.subclient_id
    LEFT JOIN users u ON u.id = s.technician_id
    WHERE s.id = ?`).get(req.params.id);
  const machines = db.prepare('SELECT * FROM service_machines WHERE service_id=?').all(req.params.id);
  const media = db.prepare('SELECT * FROM service_media WHERE service_id=?').all(req.params.id);
  res.render('admin/service-view', { service, machines, media, statusLabels });
});

router.get('/Services/view/:id', (req, res) => {
  const service = db.prepare(`SELECT s.*, c.name client_name, sc.local_name, sc.address, u.name technician_name
    FROM services s JOIN clients c ON c.id=s.client_id JOIN subclients sc ON sc.id=s.subclient_id
    LEFT JOIN users u ON u.id=s.technician_id WHERE s.id=?`).get(req.params.id);
  const machines = db.prepare('SELECT * FROM service_machines WHERE service_id=?').all(req.params.id);
  res.setHeader('Content-Type', 'application/pdf');
  const doc = new PDFDocument();
  doc.pipe(res);
  doc.fontSize(18).text('FRIOLAM - Hoja de Servicio');
  doc.moveDown();
  doc.fontSize(11).text(`Servicio #${service.id} - ${service.service_name}`);
  doc.text(`Estado: ${statusLabels[service.status]}`);
  doc.text(`Cliente: ${service.client_name} / Local: ${service.local_name}`);
  doc.text(`Dirección: ${service.address || ''}`);
  doc.text(`Técnico: ${service.technician_name || 'Sin asignar'}`);
  doc.text(`Fecha Programada: ${service.scheduled_date || ''} ${service.scheduled_time || ''}`);
  doc.text(`Observaciones: ${service.observations || ''}`);
  doc.moveDown().text('Checklist Mantención:');
  doc.text(service.maintenance_data || 'Sin datos');
  doc.moveDown().text('Checklist Postmix:');
  doc.text(service.postmix_data || 'Sin datos');
  doc.moveDown().text('Máquinas Intervenidas:');
  machines.forEach((m) => doc.text(`- ${m.machine_name} ${m.brand || ''} ${m.model || ''} | ${m.work_done || ''}`));
  doc.moveDown().text(`Generado: ${dayjs().format('YYYY-MM-DD HH:mm')}`);
  doc.end();
});

router.post('/admin/clients', (req, res) => {
  db.prepare('INSERT INTO clients(name,tax_id,contact_email,contact_phone,observations) VALUES (?,?,?,?,?)')
    .run(req.body.name, req.body.tax_id, req.body.contact_email, req.body.contact_phone, req.body.observations);
  res.redirect('/admin/settings');
});

router.post('/admin/subclients', (req, res) => {
  db.prepare(`INSERT INTO subclients(client_id,local_name,fantasy_name,address,commune,city,phone,email,channel,observations)
    VALUES (?,?,?,?,?,?,?,?,?,?)`).run(
    req.body.client_id, req.body.local_name, req.body.fantasy_name, req.body.address, req.body.commune,
    req.body.city, req.body.phone, req.body.email, req.body.channel, req.body.observations
  );
  res.redirect('/admin/settings');
});

router.get('/admin/settings', (_req, res) => {
  const clients = db.prepare('SELECT * FROM clients ORDER BY id DESC').all();
  const subclients = db.prepare('SELECT s.*, c.name client_name FROM subclients s JOIN clients c ON c.id=s.client_id ORDER BY s.id DESC').all();
  const technicians = db.prepare("SELECT id,name,email FROM users WHERE role='technician'").all();
  res.render('admin/settings', { clients, subclients, technicians });
});

module.exports = router;
