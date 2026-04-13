const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const { ensureDb, listRecords, createOrUpdateRecord, dashboardSummary, DB_PATH } = require('../server/store');

test('db exists and seeds', () => {
  ensureDb();
  assert.equal(fs.existsSync(DB_PATH), true);
  const items = listRecords();
  assert.ok(items.length >= 3);
});

test('create or update works', () => {
  const rec = createOrUpdateRecord({
    role: 'tecnico',
    nombre: 'Pedro',
    metric_name: 'tickets_abiertos',
    metric_value: 9
  });
  assert.equal(rec.nombre, 'Pedro');
  const summary = dashboardSummary();
  assert.ok(summary.tecnico >= 1);
});
