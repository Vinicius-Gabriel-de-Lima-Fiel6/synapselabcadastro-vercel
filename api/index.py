from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client as TwilioClient
import os
from datetime import datetime

app = FastAPI()

# --- Configurações Supabase ---
url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

# --- Configurações Twilio ---
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_NUMBER") # Ex: 'whatsapp:+14155238886'

class CadastroSchema(BaseModel):
    nome: str
    email: str
    cpf_cnpj: str
    whatsapp: str
    empresa: str
    senha: str
    plano: str
    metodo: str

def enviar_whatsapp_welcome(numero_destino, nome, empresa):
    """Envia notificação via WhatsApp usando Twilio"""
    try:
        client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
        
        # Formata o número (garantindo que tenha o prefixo do país +55)
        # Se o usuário não digitar +55, o código adiciona
        num = numero_destino.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not num.startswith("+"):
            num = f"+55{num}"
            
        mensagem = (
            f"🧪 *SynapseLab* \n\n"
            f"Olá *{nome}*! 🎉\n"
            f"A licença para o laboratório *{empresa}* foi ativada com sucesso.\n\n"
            f"Seu acesso já está liberado. Verifique seu e-mail para mais detalhes."
        )

        client.messages.create(
            from_=TWILIO_FROM,
            body=mensagem,
            to=f"whatsapp:{num}"
        )
        return True
    except Exception as e:
        print(f"Erro WhatsApp: {e}")
        return False

def enviar_email_welcome(email_dest, nome, empresa):
    remetente = os.getenv("EMAIL_USER")
    senha_email = os.getenv("EMAIL_PASS")
    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = email_dest
    msg['Subject'] = f"🚀 Bem-vindo ao SynapseLab: {empresa}"

    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
        <h2 style="color: #10b981;">🧪 SynapseLab Ativado!</h2>
        <p>Olá <b>{nome}</b>,</p>
        <p>A empresa <b>{empresa}</b> agora faz parte da nossa rede de laboratórios inteligentes.</p>
        <div style="background: #f0fdfa; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
            <p><b>Login:</b> {email_dest}</p>
            <p><b>Senha:</b> A senha criada no cadastro.</p>
        </div>
        <p style="font-size: 12px; color: #666;">Suporte: (61) 9331-4870</p>
    </div>
    """
    msg.attach(MIMEText(html, 'html'))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha_email)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro e-mail: {e}")

@app.post("/api/checkout")
async def process_checkout(data: CadastroSchema):
    try:
        # 1. Verificar se empresa existe
        check = supabase.table("organizations").select("id").eq("name", data.empresa).execute()
        if check.data:
            raise HTTPException(status_code=400, detail="Esta empresa já possui cadastro.")

        # 2. Hash da senha
        pw_hash = bcrypt.hashpw(data.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 3. Criar Organização
        org_res = supabase.table("organizations").insert({
            "name": data.empresa, "plano_ativo": data.plano, 
            "metodo_pagto": data.metodo, "status_assinatura": "ativo"
        }).execute()
        org_id = org_res.data[0]['id']

        # 4. Criar Usuário
        supabase.table("users").insert({
            "username": data.nome, "email": data.email, "password_hash": pw_hash,
            "org_name": data.empresa, "org_id": org_id, "role": "ADM",
            "cpf_cnpj": data.cpf_cnpj, "whatsapp": data.whatsapp
        }).execute()

        # 5. Notificações Multicanal
        enviar_email_welcome(data.email, data.nome, data.empresa)
        enviar_whatsapp_welcome(data.whatsapp, data.nome, data.empresa)

        return {"message": "Sucesso"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
