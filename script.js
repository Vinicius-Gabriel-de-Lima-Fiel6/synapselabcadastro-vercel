document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('btn-submit');
    const originalText = btn.innerText;
    btn.innerText = "ATIVANDO LICENÇA...";
    btn.disabled = true;

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

        const result = await response.json();

        if (response.ok) {
            alert("✨ Perfeito! Sua conta SynapseLab foi criada. Verifique seu e-mail.");
            window.location.reload();
        } else {
            alert("⚠️ Erro: " + result.detail);
        }
    } catch (err) {
        alert("Erro ao conectar com o servidor.");
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
});
