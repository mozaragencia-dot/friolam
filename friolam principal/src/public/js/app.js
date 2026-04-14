if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}

async function postForm(url, formId) {
  const form = document.getElementById(formId);
  const data = Object.fromEntries(new FormData(form).entries());
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) {
    const payload = await response.json();
    throw new Error(payload.error || 'error');
  }
  return response.json();
}

window.saveTechnical = async function saveTechnical() {
  try {
    await postForm('/api/services/update-technical', 'tech-form');
    alert('Formulario guardado correctamente');
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
};

window.saveMachine = async function saveMachine() {
  try {
    await postForm('/api/services/machines', 'machine-form');
    alert('Máquina registrada');
    location.reload();
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
};

window.updateStatus = async function updateStatus() {
  try {
    await postForm('/api/services/status', 'status-form');
    alert('Estado actualizado');
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
};
