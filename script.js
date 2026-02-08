// Modal
const modal = document.getElementById("modal");
document.getElementById("open-terms").onclick = () => modal.style.display = "block";
document.getElementById("close-modal").onclick = () => modal.style.display = "none";
window.onclick = (e) => { if(e.target == modal) modal.style.display = "none"; }

// Form Submit
document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-submit');
    btn.disabled = true; btn.innerText = "ATIVANDO...";

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
        const res = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("✨ SUCESSO! Verifique seu WhatsApp e E-mail.");
            
        } else {
            const err = await res.json();
            alert("ERRO: " + err.detail);
        }
    } catch (err) { alert("Falha na conexão."); }
    finally { btn.disabled = false; btn.innerText = "FINALIZAR E ATIVAR AGORA"; }
});
