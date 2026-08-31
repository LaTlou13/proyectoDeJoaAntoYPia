document.addEventListener('DOMContentLoaded', () => {

    // --- Buscador genérico en tiempo real para Tablas ---
    function activarBuscadorTabla(inputId, tableId) {
        const input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('keyup', () => {
            const query = input.value.toLowerCase().trim();
            const tableRows = document.querySelectorAll(`#${tableId} tbody tr`);

            tableRows.forEach(row => {
                const rowText = row.textContent.toLowerCase();
                row.style.display = rowText.includes(query) ? '' : 'none';
            });
        });
    }

    // Inicialización de buscadores
    activarBuscadorTabla('buscarEquipo', 'tablaEquipos');
    activarBuscadorTabla('buscarComponente', 'tablaComponentes');
    activarBuscadorTabla('buscarPrestamo', 'tablaPrestamos');

    // --- Filtrado dinámico de Préstamos (Todos / Pendientes / Devueltos) ---
    const filterButtons = document.querySelectorAll('.btn-filter');
    const prestamosRows = document.querySelectorAll('#tablaPrestamos tbody tr');

    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                const filterValue = button.textContent.trim().toLowerCase();

                prestamosRows.forEach(row => {
                    const rowStatus = row.getAttribute('data-estado');

                    if (filterValue === 'todos') {
                        row.style.display = '';
                    } else if (filterValue === 'pendientes' && rowStatus === 'pendiente') {
                        row.style.display = '';
                    } else if (filterValue === 'devueltos' && rowStatus === 'devuelto') {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }

    // --- Buscador dinámico para la lista de componentes en Nuevo Préstamo ---
    const inputComp = document.getElementById('buscar-comp-prestamo');
    const compItems = document.querySelectorAll('.components-list .component-item');

    if (inputComp && compItems.length > 0) {
        inputComp.addEventListener('input', function() {
            const busqueda = this.value.toLowerCase().trim();

            compItems.forEach(item => {
                const infoNode = item.querySelector('.component-info strong');
                const nombreComp = infoNode ? infoNode.textContent.toLowerCase() : '';
                item.style.display = nombreComp.includes(busqueda) ? '' : 'none';
            });
        });
    }

    // --- Buscador dinámico para el selector <select> de Equipos en Nuevo Préstamo ---
    const inputEquipo = document.getElementById('buscar-equipo-prestamo');
    const selectEquipo = document.getElementById('id_equipo');

    if (inputEquipo && selectEquipo) {
        inputEquipo.addEventListener('input', function() {
            const busqueda = this.value.toLowerCase().trim();
            const opciones = selectEquipo.querySelectorAll('option');

            opciones.forEach(opcion => {
                if (opcion.value === '') {
                    opcion.hidden = false;
                    return;
                }
                const textoOp = opcion.textContent.toLowerCase();
                opcion.hidden = !textoOp.includes(busqueda);
            });
        });
    }

    // --- Autocompletar la fecha de retiro con la fecha de hoy ---
    const fechaRetiroInput = document.getElementById('fecha_retiro');
    if (fechaRetiroInput && !fechaRetiroInput.value) {
        const hoy = new Date().toISOString().split('T')[0];
        fechaRetiroInput.value = hoy;
    }
});

// =========================================================================
// FUNCIONES GLOBALES
// =========================================================================

function mostrarQR(texto) {
    const modal = document.getElementById('modal-qr');
    const img = document.getElementById('img-qr');
    const titulo = document.getElementById('qr-titulo');

    if (!modal || !img || !titulo) return;

    titulo.textContent = 'Código QR';

    // Se reemplazan saltos de línea por un separador seguro en URL
    const textoLimpio = texto.replace(/\n/g, ' | ');
    img.src = '/qr/' + encodeURIComponent(textoLimpio);

    // Apertura nativa de etiquetas HTML <dialog>
    if (typeof modal.showModal === 'function') {
        modal.showModal();
    } else {
        modal.style.display = 'flex';
    }
}

function cerrarQR() {
    const modal = document.getElementById('modal-qr');
    if (!modal) return;

    if (typeof modal.close === 'function') {
        modal.close();
    } else {
        modal.style.display = 'none';
    }
}

function mostrarQREquipo(btn) {
    const codigo = btn.dataset.codigo || '';
    const sn = btn.dataset.sn || 'N/A';
    const tipo = btn.dataset.tipo || '';
    const ubicacion = btn.dataset.ubicacion || 'Sin Ubicación';

    const texto = `EQUIPO\nCódigo: ${codigo}\nN° Serie: ${sn}\nTipo: ${tipo}\nUbicación: ${ubicacion}`;
    mostrarQR(texto);
}

function mostrarQRComponente(btn) {
    const nombre = btn.dataset.nombre || '';
    const tipo = btn.dataset.tipo || 'N/A';
    const sn = btn.dataset.sn || 'N/A';
    const desc = btn.dataset.descripcion || 'Sin descripción';
    const stock = btn.dataset.stock || '0';

    const texto = `COMPONENTE / INSUMO\nNombre: ${nombre}\nTipo: ${tipo}\nN° Serie: ${sn}\nDescripción: ${desc}\nStock: ${stock}`;
    mostrarQR(texto);
}

function pedirClave(event, form) {
    if (event) event.preventDefault();
    
    const password = prompt('Ingresá la contraseña para autorizar la acción:');
    
    if (password !== null && password.trim() !== '') {
        let passInput = form.querySelector('input[name="clave"]');
        if (!passInput) {
            passInput = document.createElement('input');
            passInput.type = 'hidden';
            passInput.name = 'clave';
            form.appendChild(passInput);
        }
        passInput.value = password.trim();
        form.submit();
        return true;
    }
    return false;
}

function editarComponente(btn) {
    const idComponente = btn.dataset.id;
    const nombreActual = btn.dataset.nombre || '';
    const tipoActual = btn.dataset.tipo || 'Otro';
    const snActual = btn.dataset.sn || '';
    const descActual = btn.dataset.descripcion || '';
    const stockActual = btn.dataset.stock || '1';

    const nuevoNombre = prompt('Editar Nombre del componente:', nombreActual);
    if (nuevoNombre === null || nuevoNombre.trim() === '') return;

    const nuevoTipo = prompt('Editar Tipo / Categoría:', tipoActual);
    if (nuevoTipo === null || nuevoTipo.trim() === '') return;

    const nuevoSN = prompt('Editar N° de Serie (dejar vacío si no tiene):', snActual !== 'None' && snActual !== 's/n' ? snActual : '');
    if (nuevoSN === null) return;

    const nuevaDesc = prompt('Editar Descripción:', descActual);
    if (nuevaDesc === null) return;

    const nuevoStock = prompt('Editar Stock actual:', stockActual);
    if (nuevoStock === null || nuevoStock.trim() === '') return;

    const password = prompt('Ingresá la contraseña para autorizar los cambios:');
    if (password !== null && password.trim() !== '') {
        const form = document.getElementById('form-editar-componente');
        if (form) {
            form.action = '/editar_componente/' + idComponente;
            
            document.getElementById('edit-comp-nombre').value = nuevoNombre.trim();
            if (document.getElementById('edit-comp-tipo')) {
                document.getElementById('edit-comp-tipo').value = nuevoTipo.trim();
            }
            document.getElementById('edit-comp-sn').value = nuevoSN.trim();
            document.getElementById('edit-comp-desc').value = nuevaDesc.trim();
            document.getElementById('edit-comp-stock').value = nuevoStock.trim();
            document.getElementById('edit-comp-pass').value = password.trim();

            form.submit();
        }
    }
}

function editarEquipo(btn) {
    const idEquipo = btn.dataset.id;
    const codigoActual = btn.dataset.codigo || '';
    const snActual = btn.dataset.sn || '';
    const tipoActual = btn.dataset.tipo || '';
    const ubicacionActual = btn.dataset.ubicacion || '';

    const nuevoCodigo = prompt('Editar Código Identificador:', codigoActual);
    if (nuevoCodigo === null || nuevoCodigo.trim() === '') return;

    const nuevoSN = prompt('Editar N° de Serie (dejar vacío si no tiene):', snActual !== 'None' && snActual !== 's/n' ? snActual : '');
    if (nuevoSN === null) return;

    const nuevoTipo = prompt('Editar Tipo (ej: Notebook, PC escritorio):', tipoActual);
    if (nuevoTipo === null || nuevoTipo.trim() === '') return;

    const nuevaUbicacion = prompt('Editar Ubicación (ej: Lab Informática, Lab Robótica):', ubicacionActual);
    if (nuevaUbicacion === null) return;

    const password = prompt('Ingresá la contraseña para autorizar los cambios:');
    if (password !== null && password.trim() !== '') {
        const form = document.getElementById('form-editar-equipo');
        if (form) {
            form.action = '/editar_equipo/' + idEquipo;

            document.getElementById('edit-eq-codigo').value = nuevoCodigo.trim();
            document.getElementById('edit-eq-sn').value = nuevoSN.trim();
            document.getElementById('edit-eq-tipo').value = nuevoTipo.trim();
            if (document.getElementById('edit-eq-ubicacion')) {
                document.getElementById('edit-eq-ubicacion').value = nuevaUbicacion.trim();
            }
            document.getElementById('edit-eq-pass').value = password.trim();

            form.submit();
        }
    }
}