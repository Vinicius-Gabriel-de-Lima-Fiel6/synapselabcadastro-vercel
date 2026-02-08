document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-submit');
    btn.disabled = true;
    btn.innerText = "PROCESSANDO...";

    const data = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        cpf_cnpj: document.getElementById('cpf_cnpj').value,
        whatsapp: document.getElementById('whatsapp').value,
        empresa: document.getElementById('empresa').value,
        senha: document.getElementById('senha').value,
        plano: document.getElementById('plano').value,
        metodo: document.querySelector('input[name="metodo"]:checked').value
    };

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert("✨ Licença ativada! Bem-vindo ao SynapseLab.");
            window.location.reload();
        } else {
            const error = await response.json();
            alert("Erro: " + error.detail);
        }
    } catch (err) {
        alert("Erro na conexão.");
    } finally {
        btn.disabled = false;
        btn.innerText = "FINALIZAR E ATIVAR AGORA";
    }
});
