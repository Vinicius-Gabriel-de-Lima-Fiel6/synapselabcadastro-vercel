from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from supabase import create_client, Client
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = FastAPI()

# --- HANDLER DE ERROS GLOBAL ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log do erro no console da Vercel para você depurar
    print(f"ERRO IDENTIFICADO: {str(exc)}")
    
    # Tratamento para erros específicos do Supabase (ex: violação de unicidade)
    if "duplicate key" in str(exc).lower():
        return JSONResponse(
            status_code=400,
            content={"detail": "Os dados informados (E-mail ou CNPJ) já estão em uso."}
        )
    
    # Tratamento para erros de conexão SMTP
    if "smtp" in str(exc).lower():
        return JSONResponse(
            status_code=201, # Criamos a conta, mas o e-mail falhou
            content={"detail": "Conta criada, mas houve uma falha ao enviar o e-mail de boas-vindas."}
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno no servidor. Tente novamente em instantes."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Dados inválidos. Verifique se todos os campos foram preenchidos corretamente."}
    )

# --- CONFIGURAÇÕES ---
url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

class CadastroSchema(BaseModel):
    nome: str; email: str; cpf_cnpj: str; whatsapp: str
    empresa: str; senha: str; plano: str; metodo: str

def enviar_email_welcome(email_dest, nome, empresa):
    remetente = os.getenv("EMAIL_USER")
    senha_email = os.getenv("EMAIL_PASS")
    
    if not remetente or not senha_email:
        print("Aviso: Variáveis de e-mail não configuradas.")
        return

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = email_dest
    msg['Subject'] = f"🚀 Bem-vindo ao SynapseLab: {empresa}"

    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
        <h2 style="color: #10b981;">🧪 SynapseLab Ativado!</h2>
        <p>Olá <b>{nome}</b>,</p>
        <p>A licença para a empresa <b>{empresa}</b> foi processada com sucesso.</p>
        <div style="background: #f0fdfa; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
            <p><b>Acesso:</b> {email_dest}</p>
            <p><b>Senha:</b> A que você definiu no cadastro.</p>
        </div>
        <p style="font-size: 12px; color: #666;">Suporte Oficial SynapseLab</p>
    </div>
    """
    msg.attach(MIMEText(html, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(remetente, senha_email)
        server.send_message(msg)

@app.post("/api/checkout")
async def process_checkout(data: CadastroSchema):
    # O try/except global do exception_handler vai pegar erros inesperados aqui
    
    # 1. Validação Manual de Segurança
    if len(data.senha) < 6:
        raise HTTPException(status_code=400, detail="A senha deve ter pelo menos 6 caracteres.")

    # 2. Verificar se empresa existe
    check = supabase.table("organizations").select("id").eq("name", data.empresa).execute()
    if check.data:
        raise HTTPException(status_code=400, detail="Esta empresa já possui cadastro.")

    # 3. Hash e Inserção
    pw_hash = bcrypt.hashpw(data.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    org_res = supabase.table("organizations").insert({
        "name": data.empresa, "plano_ativo": data.plano, 
        "metodo_pagto": data.metodo, "status_assinatura": "ativo"
    }).execute()
    
    if not org_res.data:
        raise Exception("Erro ao processar organização no banco de dados.")

    org_id = org_res.data[0]['id']

    supabase.table("users").insert({
        "username": data.nome, "email": data.email, "password_hash": pw_hash,
        "org_name": data.empresa, "org_id": org_id, "role": "ADM",
        "cpf_cnpj": data.cpf_cnpj, "whatsapp": data.whatsapp
    }).execute()

    # 4. E-mail
    enviar_email_welcome(data.email, data.nome, data.empresa)

    return {"message": "Sucesso"}
