import { createClient } from '@supabase/supabase-js';
import bcrypt from 'bcryptjs';
import nodemailer from 'nodemailer';

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Apenas POST' });

    const { nome, email, senha, empresa, cpf, whatsapp, plano, metodo } = req.body;

    try {
        // 1. Checar se empresa já existe (Removido o .single() para evitar erro se não existir)
        const { data: orgExiste, error: checkErr } = await supabase
            .from('organizations')
            .select('id')
            .eq('name', empresa);
        
        if (orgExiste && orgExiste.length > 0) {
            return res.status(400).json({ error: 'Esta instituição já está cadastrada.' });
        }

        // 2. Hash da Senha (Sync está ok, mas Async é melhor para performance em APIs)
        const salt = await bcrypt.genSalt(10);
        const hash = await bcrypt.hash(senha, salt);

        // 3. Criar Organização
        const { data: org, error: orgErr } = await supabase
            .from('organizations')
            .insert([{ 
                name: empresa, 
                plano_ativo: plano, 
                metodo_pagto: metodo, 
                status_assinatura: 'ativo' 
            }])
            .select()
            .single(); // Agora usamos single aqui porque queremos o objeto criado

        if (orgErr) throw new Error(`Erro ao criar organização: ${orgErr.message}`);

        // 4. Criar Usuário ADM
        const { error: userErr } = await supabase
            .from('users')
            .insert([{
                username: nome, 
                email, 
                password_hash: hash,
                org_name: empresa, 
                org_id: org.id, // org agora é um objeto por causa do .single()
                role: 'ADM', 
                cpf_cnpj: cpf, 
                whatsapp
            }]);

        if (userErr) throw new Error(`Erro ao criar usuário: ${userErr.message}`);

        // 5. Enviar Boas-vindas via SMTP
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
        console.error("Erro interno:", e.message);
        return res.status(500).json({ error: e.message });
    }
}
