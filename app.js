const form = document.getElementById('persona-form');
const btnAgregarRepresentante = document.getElementById('agregar-representante');
const representantesLista = document.getElementById('representantes-lista');
const representanteTemplate = document.getElementById('representante-template');
const resultado = document.getElementById('resultado');

function crearRepresentante() {
  const fragment = representanteTemplate.content.cloneNode(true);
  const item = fragment.querySelector('.representante-item');
  item.querySelector('.eliminar-representante').addEventListener('click', () => {
    item.remove();
  });
  representantesLista.appendChild(fragment);
}

btnAgregarRepresentante.addEventListener('click', crearRepresentante);

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const data = {
    nombre: form.nombre.value.trim(),
    esImputado: form.esImputado.value,
    representantes: Array.from(
      representantesLista.querySelectorAll('.representante-item')
    ).map((item) => ({
      nombre: item.querySelector('[name="representanteNombre"]').value.trim(),
      tipo: item.querySelector('[name="representanteTipo"]').value.trim(),
      modulo: item.querySelector('[name="representanteModulo"]').value.trim(),
    })),
  };

  resultado.textContent = JSON.stringify(data, null, 2);
});

crearRepresentante();
