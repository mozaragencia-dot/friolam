CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','technician','supervisor') NOT NULL,
  active TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE clients (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  tax_id VARCHAR(40),
  contact_email VARCHAR(150),
  contact_phone VARCHAR(50),
  observations TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE subclients (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  client_id BIGINT NOT NULL,
  local_name VARCHAR(150) NOT NULL,
  fantasy_name VARCHAR(150),
  address VARCHAR(255),
  commune VARCHAR(120),
  city VARCHAR(120),
  phone VARCHAR(50),
  email VARCHAR(150),
  channel VARCHAR(80),
  observations TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_subclient_client FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE services (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  service_name VARCHAR(180) NOT NULL,
  ticket VARCHAR(50),
  invoice VARCHAR(50),
  client_id BIGINT NOT NULL,
  subclient_id BIGINT NOT NULL,
  technician_id BIGINT,
  status TINYINT NOT NULL DEFAULT 0,
  service_type VARCHAR(80),
  scheduled_date DATE,
  scheduled_time TIME,
  observations TEXT,
  client_phone VARCHAR(50),
  fantasy_name VARCHAR(150),
  maintenance_data JSON,
  postmix_data JSON,
  closing_data JSON,
  total DECIMAL(12,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_service_client FOREIGN KEY (client_id) REFERENCES clients(id),
  CONSTRAINT fk_service_subclient FOREIGN KEY (subclient_id) REFERENCES subclients(id),
  CONSTRAINT fk_service_technician FOREIGN KEY (technician_id) REFERENCES users(id)
);

CREATE TABLE service_machines (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  service_id BIGINT NOT NULL,
  machine_name VARCHAR(150),
  model VARCHAR(120),
  serial VARCHAR(120),
  brand VARCHAR(120),
  diagnosis TEXT,
  work_done TEXT,
  spare_parts TEXT,
  observations TEXT,
  machine_status VARCHAR(80),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_machine_service FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE service_media (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  service_id BIGINT NOT NULL,
  media_type ENUM('photo','signature_tech','signature_client') NOT NULL,
  file_path VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_media_service FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE audit_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT,
  action VARCHAR(80) NOT NULL,
  entity_type VARCHAR(80) NOT NULL,
  entity_id BIGINT,
  detail TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id)
);
