document.addEventListener('DOMContentLoaded', () => {
    
    const filterButtons = document.querySelectorAll('.btn-filter');
    const tableRows = document.querySelectorAll('#tabla-prestamos tbody tr');

    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {

                filterButtons.forEach(btn => btn.classList.remove('active'));
                
              
                button.classList.add('active');

                const filterValue = button.getAttribute('data-filter');

               
                tableRows.forEach(row => {
                    const rowStatus = row.getAttribute('data-status');

                    if (filterValue === 'todos' || rowStatus === filterValue) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }

    const deleteForms = document.querySelectorAll('.form-eliminar');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmado = confirm('¿Estás seguro/a de que querés realizar esta acción?');
            if (!confirmado) {
                e.preventDefault();
            }
        });
    });

});