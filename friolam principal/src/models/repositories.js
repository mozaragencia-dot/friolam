const { db } = require('../db/database');

const statusLabels = {
  0: 'nuevo',
  1: 'asignado',
  2: 'en proceso',
  3: 'pendiente validación',
  4: 'terminado parcial',
  5: 'terminado final'
};

function logAudit(userId, action, entityType, entityId, detail = '') {
  db.prepare(
    `INSERT INTO audit_logs(user_id, action, entity_type, entity_id, detail) VALUES (?, ?, ?, ?, ?)`
  ).run(userId || null, action, entityType, entityId || null, detail);
}

function getDashboardStats() {
  const servicesByStatus = db.prepare(`SELECT status, COUNT(*) as total FROM services GROUP BY status`).all();
  const totals = Object.keys(statusLabels).reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
  servicesByStatus.forEach((row) => {
    totals[row.status] = row.total;
  });
  return totals;
}

module.exports = { db, statusLabels, logAudit, getDashboardStats };
