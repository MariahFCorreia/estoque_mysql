// scripts.js - Funcionalidades JavaScript para o sistema

document.addEventListener('DOMContentLoaded', function() {
    // Adicionar animação de fade-in aos cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('fade-in');
    });

    // Validação de formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    valid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!valid) {
                e.preventDefault();
                showAlert('Por favor, preencha todos os campos obrigatórios.', 'danger');
            }
        });
    });

    // Validação de senha no formulário de usuário
    const passwordForm = document.querySelector('form[action*="usuario"]');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            const senha = document.getElementById('senha');
            const confirmarSenha = document.getElementById('confirmar_senha');

            if (senha && confirmarSenha && senha.value !== confirmarSenha.value) {
                e.preventDefault();
                confirmarSenha.classList.add('is-invalid');
                showAlert('As senhas não coincidem!', 'danger');
            }
        });
    }

    // Auto-dismiss alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Melhoria nas tabelas - ordenação
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                sortTable(table, index);
            });
        });
    });
});

// Função para mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Função para ordenar tabelas
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isNumeric = !isNaN(parseFloat(rows[0].cells[columnIndex].textContent));

    rows.sort((a, b) => {
        let aValue = a.cells[columnIndex].textContent.trim();
        let bValue = b.cells[columnIndex].textContent.trim();

        if (isNumeric) {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
            return aValue - bValue;
        } else {
            return aValue.localeCompare(bValue, 'pt-BR');
        }
    });

    // Remove todas as linhas
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    // Adiciona as linhas ordenadas
    rows.forEach(row => tbody.appendChild(row));
}

// Função para confirmar exclusões
function confirmDelete(message = 'Tem certeza que deseja excluir este item?') {
    return confirm(message);
}

// Função para formatar moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}