const jwt = require('jsonwebtoken');

const SECRET = process.env.JWT_SECRET || 'friolam-secret';

function createToken(user) {
  return jwt.sign({ id: user.id, role: user.role, name: user.name }, SECRET, { expiresIn: '1d' });
}

function attachUser(req, res, next) {
  const token = req.cookies?.token || req.headers.authorization?.replace('Bearer ', '');
  if (!token) return next();
  try {
    req.user = jwt.verify(token, SECRET);
  } catch (_err) {}
  return next();
}

function requireAuth(req, res, next) {
  if (!req.user) return res.redirect('/login');
  return next();
}

function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      if (req.path.startsWith('/api')) return res.status(403).json({ error: 'forbidden' });
      return res.status(403).send('No autorizado');
    }
    return next();
  };
}

module.exports = { createToken, attachUser, requireAuth, requireRole };
