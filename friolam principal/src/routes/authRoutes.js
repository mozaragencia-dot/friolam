const express = require('express');
const bcrypt = require('bcryptjs');
const { db } = require('../db/database');
const { createToken } = require('../middleware/auth');

const router = express.Router();

router.get('/login', (_req, res) => res.render('auth/login'));

router.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ? AND active = 1').get(email);
  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).render('auth/login', { error: 'Credenciales inválidas' });
  }
  const token = createToken(user);
  res.cookie('token', token, { httpOnly: true, sameSite: 'lax' });
  if (user.role === 'technician') return res.redirect('/tech');
  return res.redirect('/admin');
});

router.get('/logout', (_req, res) => {
  res.clearCookie('token');
  return res.redirect('/login');
});

module.exports = router;
