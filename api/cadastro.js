const { createClient } = require('@supabase/supabase-js');
const bcrypt = require('bcryptjs');
const nodemailer = require('nodemailer');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Apenas POST' });

    const { nome, email, senha, empresa, cpf, whatsapp, plano, metodo } = req.body;

    try {
        // 1. Lógica do auth_db: Checar se empresa já existe
        const { data: orgExiste } = await supabase.from('organizations').select('id').eq('name', empresa).single();
        if (orgExiste) return res.status(400).json({ error: 'Esta instituição já está cadastrada.' });

        // 2. Hash da Senha
        const salt = bcrypt.genSaltSync(10);
        const hash = bcrypt.hashSync(senha, salt);

        // 3. Criar Organização
        const { data: org, error: orgErr } = await supabase
            .from('organizations')
            .insert([{ name: empresa, plano_ativo: plano, metodo_pagto: metodo, status_assinatura: 'ativo' }])
            .select();
        if (orgErr) throw orgErr;

        // 4. Criar Usuário ADM
        const { error: userErr } = await supabase
            .from('users')
            .insert([{
                username: nome, email, password_hash: hash,
                org_name: empresa, org_id: org[0].id,
                role: 'ADM', cpf_cnpj: cpf, whatsapp
            }]);
        if (userErr) throw userErr;

        // 5. Lógica do email_utils: Enviar Boas-vindas via SMTP
        const transporter = nodemailer.createTransport({
            host: "smtp.gmail.com",
            port: 587,
            secure: false,
            auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
        });

        const htmlCorpo = `
            <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #00ff88; padding: 20px; border-radius: 10px; background: #000; color: #fff;">
                <h2 style="color: #00ff88;">🧪 LabSmartAI: Licença Ativada!</h2>
                <p>Olá <strong>${nome}</strong>, seu acesso ao <strong>${empresa}</strong> está liberado.</p>
                <div style="background: #111; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Login:</strong> ${email}</p>
                    <p><strong>Plano:</strong> ${plano}</p>
                    <p><strong>Link:</strong> <a href="https://labsmartai.vercel.app" style="color:#00ff88;">Acessar Portal</a></p>
                </div>
                <p style="font-size: 12px; color: #666;">© 2026 LabSmartAI Tech</p>
            </div>`;

        await transporter.sendMail({
            from: `"LabSmartAI" <${process.env.EMAIL_USER}>`,
            to: email,
            subject: `Bem-vindo ao LabSmartAI - ${empresa}`,
            html: htmlCorpo
        });

        return res.status(200).json({ success: true });

    } catch (e) {
        return res.status(500).json({ error: e.message });
    }
}
