const express = require('express');
const path = require('path');
const { ensureDb, listRecords, createOrUpdateRecord, dashboardSummary, DB_PATH } = require('./store');

ensureDb();

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'web')));

app.get('/api/dashboard', (_req, res) => {
  const items = listRecords();
  res.json({ summary_by_role: dashboardSummary(), total_records: items.length });
});

app.get('/api/records', (req, res) => {
  const role = req.query.role || null;
  const items = listRecords(role);
  res.json({ total: items.length, items });
});

app.post('/api/records', (req, res) => {
  const { role, nombre, metric_name, metric_value } = req.body;
  if (!role || !nombre || !metric_name) {
    return res.status(400).json({ error: 'payload inválido' });
  }
  const record = createOrUpdateRecord({ role, nombre, metric_name, metric_value });
  return res.status(201).json(record);
});

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, '..', 'web', 'index.html'));
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`Friolam Ionic app en http://0.0.0.0:${PORT}`);
  console.log(`DB archivo: ${DB_PATH}`);
});
