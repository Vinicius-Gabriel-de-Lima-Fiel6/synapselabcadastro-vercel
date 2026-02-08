document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    btn.innerText = "PROCESSANDO...";
    btn.disabled = true;

    const payload = {
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
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("✨ Conta ativada com sucesso! Verifique seu e-mail.");
            window.location.reload();
        } else {
            const err = await response.json();
            alert("Erro: " + err.detail);
        }
    } catch (error) {
        alert("Erro na conexão com o servidor.");
    } finally {
        btn.innerText = "FINALIZAR E ATIVAR AGORA";
        btn.disabled = false;
    }
});
