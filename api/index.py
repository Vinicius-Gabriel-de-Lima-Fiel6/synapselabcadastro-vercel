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
    <html>
    <body style="margin: 0; padding: 0; background-color: #050505; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #ffffff;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #050505; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                        
                        <tr>
                            <td align="center" style="padding: 40px 20px; background: linear-gradient(135deg, #064e3b 0%, #0d0d0d 100%);">
                                <div style="width: 60px; height: 60px; border: 2px solid #10b981; border-radius: 50%; line-height: 60px; font-weight: 900; font-size: 24px; color: #10b981; margin-bottom: 15px; text-shadow: 0 0 10px #10b981;">SL</div>
                                <h1 style="margin: 0; font-size: 28px; letter-spacing: -1px;">Synapselab Platform</h1>
                                <p style="margin: 5px 0 0; color: #10b981; font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">Cyber-Physical Intelligent System</p>
                            </td>
                        </tr>

                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #ffffff; font-size: 22px; margin-top: 0;">Bem-vindo à Indústria 4.0, {nome}.</h2>
                                <p style="color: #a1a1aa; line-height: 1.6;">
                                    É um prazer confirmar a ativação da licença para a instituição <b>{empresa}</b>. 
                                    A partir de agora, seu ambiente laboratorial está integrado à nossa malha de inteligência artificial e monitoramento físico em tempo real.
                                </p>
                                
                                <div style="background-color: #141414; border-left: 4px solid #10b981; padding: 20px; margin: 30px 0; border-radius: 4px;">
                                    <p style="margin: 0; font-size: 14px; color: #10b981; font-weight: bold;">Credenciais de Acesso Master:</p>
                                    <p style="margin: 10px 0 0; font-size: 14px; color: #ffffff;"><b>Login:</b> {email_dest}</p>
                                    <p style="margin: 5px 0 0; font-size: 14px; color: #ffffff;"><b>Ambiente:</b> Institucional ADM</p>
                                </div>

                                <h3 style="color: #10b981; font-size: 16px; text-transform: uppercase; letter-spacing: 1px;">Visão Geral do Ecossistema</h3>
                                <ul style="color: #a1a1aa; padding-left: 20px; line-height: 1.8; font-size: 14px;">
                                    <li><b>Núcleo Digital:</b> SaaS Multiempresa com dashboards avançados e integração Power BI.</li>
                                    <li><b>Inteligência Artificial:</b> Arquitetura de múltiplos agentes para análise preditiva e relatórios autônomos.</li>
                                    <li><b>Integração Física:</b> Monitoramento de sensores de temperatura, criogenia, vibração e visão computacional para EPIs.</li>
                                    <li><b>Automação e Segurança:</b> Robôs autônomos e sistemas de contenção de riscos integrados via Edge Functions.</li>
                                </ul>

                                <h3 style="color: #10b981; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; margin-top: 40px;">Termos de Operação e Compliance</h3>
                                <div style="font-size: 12px; color: #666; line-height: 1.5; background: #080808; padding: 15px; border-radius: 8px;">
                                    <p><b>1. Uso Restrito:</b> Esta licença é proprietária e de uso exclusivo da {empresa}.</p>
                                    <p><b>2. Segurança de Dados:</b> Todas as transações são criptografadas e armazenadas via Supabase (AES-256).</p>
                                    <p><b>3. Operação Física:</b> O controle de atuadores e robôs via interface web deve seguir os protocolos de segurança internos da sua instituição.</p>
                                    <p><b>4. Status Beta:</b> Como versão v0.1, o sistema passa por integrações progressivas de IA e simulações físicas constantes.</p>
                                </div>

                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 40px;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://synapselab.streamlit.app/" style="background-color: #10b981; color: #000000; padding: 18px 35px; border-radius: 10px; text-decoration: none; font-weight: 900; font-size: 14px; display: inline-block; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">ACESSAR PAINEL DE CONTROLE</a>
                                            <a href="#" style="background-color: #10b981; color: #000000; padding: 18px 35px; border-radius: 10px; text-decoration: none; font-weight: 900; font-size: 14px; display: inline-block; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">ACESSE NOSSO SITE</a>
                                        </td>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <tr>
                            <td style="padding: 30px; background-color: #080808; border-top: 1px solid #1a1a1a; text-align: center;">
                                <p style="margin: 0; font-size: 12px; color: #444;">&copy; 2026 Synapselab Platform – Tecnologia para Laboratórios do Futuro.</p>
                                <p style="margin: 5px 0 0; font-size: 12px; color: #444;">Suporte Técnico: (92) 99252-7922 | Manaus, AM</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha_email)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao disparar e-mail: {e}")
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
