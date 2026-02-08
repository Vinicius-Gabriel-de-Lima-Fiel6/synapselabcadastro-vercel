document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-submit');
    btn.disabled = true;
    btn.innerText = "PROCESSANDO...";

    const formData = {
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert("✨ CONTA SINAPSESLAB ATIVADA COM SUCESSO!");
            window.location.reload();
        } else {
            const err = await response.json();
            alert("ERRO NO CADASTRO: " + err.detail);
        }
    } catch (f) {
        alert("FALHA DE CONEXÃO COM O SERVIDOR.");
    } finally {
        btn.disabled = false;
        btn.innerText = "FINALIZAR E ATIVAR AGORA";
    }
});
