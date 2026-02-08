const { createClient } = require('@supabase/supabase-js');
const bcrypt = require('bcryptjs');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Método não permitido' });

    const { nome, email, senha, empresa, cpf, whatsapp, plano, metodo } = req.body;

    try {
        // 1. Verificar se empresa existe
        const { data: existingOrg } = await supabase.from('organizations').select('id').eq('name', empresa).single();
        if (existingOrg) return res.status(400).json({ error: 'Empresa já cadastrada.' });

        // 2. Hash da senha
        const salt = bcrypt.genSaltSync(10);
        const passwordHash = bcrypt.hashSync(senha, salt);

        // 3. Criar Organização
        const { data: org, error: orgError } = await supabase
            .from('organizations')
            .insert([{ name: empresa, plano_ativo: plano, metodo_pagto: metodo, status_assinatura: 'ativo' }])
            .select();

        if (orgError) throw orgError;

        // 4. Criar Usuário
        const { error: userError } = await supabase
            .from('users')
            .insert([{
                username: nome,
                email,
                password_hash: passwordHash,
                org_name: empresa,
                org_id: org[0].id,
                role: 'ADM',
                cpf_cnpj: cpf,
                whatsapp
            }]);

        if (userError) throw userError;

        // Aqui você chamaria sua lógica de e-mail (email_utils)
        // Por ser Vercel, recomendo usar o serviço Resend ou SendGrid via API aqui.

        return res.status(200).json({ message: 'Sucesso' });

    } catch (e) {
        return res.status(500).json({ error: e.message });
    }
}
