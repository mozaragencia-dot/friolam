const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, 'db.json');

function ensureDb() {
  if (!fs.existsSync(DB_PATH)) {
    const seed = {
      records: [
        { id: 1, role: 'tecnico', nombre: 'Ana', metric_name: 'tickets_abiertos', metric_value: 5 },
        { id: 2, role: 'administrador', nombre: 'Luis', metric_name: 'sistemas_activos', metric_value: 12 },
        { id: 3, role: 'gerente', nombre: 'María', metric_name: 'objetivos_trimestrales', metric_value: 4 }
      ]
    };
    fs.writeFileSync(DB_PATH, JSON.stringify(seed, null, 2));
  }
}

function readDb() {
  ensureDb();
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
}

function writeDb(data) {
  fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2));
}

function listRecords(role = null) {
  const data = readDb();
  return role ? data.records.filter((r) => r.role === role) : data.records;
}

function createOrUpdateRecord(payload) {
  const data = readDb();
  const existing = data.records.find(
    (r) => r.role === payload.role && r.nombre.toLowerCase() === payload.nombre.toLowerCase()
  );

  if (existing) {
    existing.metric_name = payload.metric_name;
    existing.metric_value = Number(payload.metric_value);
    writeDb(data);
    return existing;
  }

  const nextId = data.records.length ? Math.max(...data.records.map((r) => r.id)) + 1 : 1;
  const record = {
    id: nextId,
    role: payload.role,
    nombre: payload.nombre,
    metric_name: payload.metric_name,
    metric_value: Number(payload.metric_value)
  };
  data.records.push(record);
  writeDb(data);
  return record;
}

function dashboardSummary() {
  const records = listRecords();
  return records.reduce((acc, r) => {
    acc[r.role] = (acc[r.role] || 0) + 1;
    return acc;
  }, {});
}

module.exports = { ensureDb, listRecords, createOrUpdateRecord, dashboardSummary, DB_PATH };
