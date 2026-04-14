const path = require('path');
const express = require('express');
const cookieParser = require('cookie-parser');
const { initDb } = require('./db/database');
const { attachUser } = require('./middleware/auth');
const authRoutes = require('./routes/authRoutes');
const adminRoutes = require('./routes/adminRoutes');
const techRoutes = require('./routes/techRoutes');
const apiRoutes = require('./routes/apiRoutes');

initDb();

const app = express();
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.urlencoded({ extended: true }));
app.use(express.json({ limit: '10mb' }));
app.use(cookieParser());
app.use(attachUser);
app.use('/static', express.static(path.join(__dirname, 'public')));

app.use(authRoutes);
app.use(adminRoutes);
app.use(techRoutes);
app.use(apiRoutes);

app.get('/', (req, res) => {
  if (!req.user) return res.redirect('/login');
  if (req.user.role === 'technician') return res.redirect('/tech');
  return res.redirect('/admin');
});

app.get('/manifest.webmanifest', (_req, res) => {
  res.json({
    name: 'FRIOLAM Técnico',
    short_name: 'FRIOLAM',
    start_url: '/tech',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#0d6efd',
    icons: []
  });
});

app.get('/sw.js', (_req, res) => {
  res.type('application/javascript').send(`
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open('friolam-v1').then((cache) => cache.addAll(['/tech','/tech/services','/static/css/app.css'])));
});
self.addEventListener('fetch', (event) => {
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});`);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`FRIOLAM app running on http://localhost:${PORT}`);
});
