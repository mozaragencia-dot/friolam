const path = require('path');
const Database = require('better-sqlite3');

const dbPath = process.env.DB_PATH || path.join(__dirname, '../../friolam.db');
const db = new Database(dbPath);

db.pragma('journal_mode = WAL');

function initDb() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('admin','technician','supervisor')),
      active INTEGER DEFAULT 1,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS clients (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      tax_id TEXT,
      contact_email TEXT,
      contact_phone TEXT,
      observations TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS subclients (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      client_id INTEGER NOT NULL,
      local_name TEXT NOT NULL,
      fantasy_name TEXT,
      address TEXT,
      commune TEXT,
      city TEXT,
      phone TEXT,
      email TEXT,
      channel TEXT,
      observations TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (client_id) REFERENCES clients(id)
    );

    CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      service_name TEXT NOT NULL,
      ticket TEXT,
      invoice TEXT,
      client_id INTEGER NOT NULL,
      subclient_id INTEGER NOT NULL,
      technician_id INTEGER,
      status INTEGER DEFAULT 0,
      service_type TEXT,
      scheduled_date TEXT,
      scheduled_time TEXT,
      observations TEXT,
      client_phone TEXT,
      fantasy_name TEXT,
      maintenance_data TEXT,
      postmix_data TEXT,
      closing_data TEXT,
      total REAL DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (client_id) REFERENCES clients(id),
      FOREIGN KEY (subclient_id) REFERENCES subclients(id),
      FOREIGN KEY (technician_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS service_machines (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      service_id INTEGER NOT NULL,
      machine_name TEXT,
      model TEXT,
      serial TEXT,
      brand TEXT,
      diagnosis TEXT,
      work_done TEXT,
      spare_parts TEXT,
      observations TEXT,
      machine_status TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (service_id) REFERENCES services(id)
    );

    CREATE TABLE IF NOT EXISTS service_media (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      service_id INTEGER NOT NULL,
      media_type TEXT NOT NULL CHECK(media_type IN ('photo','signature_tech','signature_client')),
      file_path TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (service_id) REFERENCES services(id)
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      action TEXT NOT NULL,
      entity_type TEXT NOT NULL,
      entity_id INTEGER,
      detail TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );
  `);
}

module.exports = { db, initDb };
