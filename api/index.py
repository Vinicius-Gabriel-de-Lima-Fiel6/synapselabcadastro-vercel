from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = FastAPI()

# Configurações via Variáveis de Ambiente (Vercel Dashboard)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class CheckoutData(BaseModel):
    nome: str
    email: str
    cpf_cnpj: str
    whatsapp: str
    empresa: str
    senha: str
    plano: str
    metodo: str

def enviar_email(email_destino, nome_usuario, nome_empresa):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = email_destino
    msg['Subject'] = f"Bem-vindo ao SynapseLab - Acesso Liberado: {nome_empresa}"
    
    corpo_html = f"""
    <html>
        <body style="font-family: sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                <h1 style="color: #0d9488;">🧪 SynapseLab</h1>
                <h2>Sua licença foi ativada, {nome_usuario}!</h2>
                <p>O <strong>{nome_empresa}</strong> agora faz parte do futuro.</p>
                <div style="background: #f0fdfa; padding: 15px; border-radius: 10px;">
                    <p><strong>Login:</strong> {email_destino}</p>
                    <p><strong>Acesse aqui:</strong> <a href="#">Link do Sistema</a></p>
                </div>
                <p>Suporte WhatsApp: (61) 9331-4870</p>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(corpo_html, 'html'))
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

@app.post("/api/checkout")
async def checkout(data: CheckoutData):
    try:
        # Check Unicidade
        check = supabase.table("organizations").select("id").eq("name", data.empresa).execute()
        if check.data:
            raise HTTPException(status_code=400, detail="Empresa já cadastrada")

        # Hash Senha
        pwd_hash = bcrypt.hashpw(data.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert Org
        res_org = supabase.table("organizations").insert({
            "name": data.empresa, "plano_ativo": data.plano, 
            "metodo_pagto": data.metodo, "status_assinatura": "ativo"
        }).execute()
        org_id = res_org.data[0]['id']

        # Insert User
        supabase.table("users").insert({
            "username": data.nome, "email": data.email, "password_hash": pwd_hash,
            "org_name": data.empresa, "org_id": org_id, "role": "ADM",
            "cpf_cnpj": data.cpf_cnpj, "whatsapp": data.whatsapp
        }).execute()

        enviar_email(data.email, data.nome, data.empresa)
        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
