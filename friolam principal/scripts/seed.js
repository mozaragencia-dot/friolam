const bcrypt = require('bcryptjs');
const { initDb, db } = require('../src/db/database');

initDb();

function upsertUser(name, email, pass, role) {
  const existing = db.prepare('SELECT id FROM users WHERE email=?').get(email);
  if (existing) return;
  db.prepare('INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)')
    .run(name, email, bcrypt.hashSync(pass, 10), role);
}

upsertUser('Admin Friolam', 'admin@friolam.cl', 'Admin123*', 'admin');
upsertUser('Tec Uno', 'tec1@friolam.cl', 'Tec123*', 'technician');
upsertUser('Supervisor', 'super@friolam.cl', 'Super123*', 'supervisor');

const client = db.prepare('INSERT INTO clients(name,tax_id,contact_email,contact_phone,observations) VALUES (?,?,?,?,?)')
  .run('Embotelladora Demo', '76.111.222-3', 'demo@cliente.cl', '+56 9 1111 1111', 'Cliente de prueba');

const sub = db.prepare(`INSERT INTO subclients(client_id,local_name,fantasy_name,address,commune,city,phone,email,channel,observations)
VALUES (?,?,?,?,?,?,?,?,?,?)`).run(client.lastInsertRowid, 'Local Centro', 'Fantasia Centro', 'Av. Principal 123', 'Santiago', 'Santiago', '+56 9 2222 2222', 'local@cliente.cl', 'Retail', 'Sin observaciones');

const tec = db.prepare("SELECT id FROM users WHERE role='technician' LIMIT 1").get();
db.prepare(`INSERT INTO services(service_name,ticket,invoice,client_id,subclient_id,technician_id,status,service_type,scheduled_date,scheduled_time,observations,client_phone,fantasy_name)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`).run('Mantención Postmix', 'TK-001', 'FC-001', client.lastInsertRowid, sub.lastInsertRowid, tec.id, 1, 'postmix', '2026-04-14', '10:00', 'Servicio inicial de demostración', '+56 9 2222 2222', 'Fantasia Centro');

console.log('Datos de prueba cargados. Usuario admin: admin@friolam.cl / Admin123*');
