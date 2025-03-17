from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import paramiko
import databutton as db
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

router = APIRouter(prefix="/ssh")

# Modelos de dados para requisições e respostas
class SSHConnectionRequest(BaseModel):
    hostname: str = "147.93.32.27"
    port: int = 22
    username: str = "root"
    password: str = "XDJ8cnWtyyiU@YScB2-j"

class SSHCommandRequest(BaseModel):
    command: str
    hostname: str = "147.93.32.27"
    port: int = 22
    username: str = "root"
    password: str = "XDJ8cnWtyyiU@YScB2-j"

class SSHResponse(BaseModel):
    success: bool
    message: str
    output: str = ""

# Função auxiliar para criar uma conexão SSH
def create_ssh_client(hostname, port, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password)
        return client, None
    except Exception as e:
        return None, str(e)

# Endpoint para testar conexão SSH
@router.post("/connect")
def test_ssh_connection(request: SSHConnectionRequest) -> SSHResponse:
    try:
        client, error = create_ssh_client(
            request.hostname, 
            request.port, 
            request.username, 
            request.password
        )
        
        if error:
            return SSHResponse(success=False, message=f"Erro ao conectar: {error}", output="")
        
        client.close()
        return SSHResponse(
            success=True, 
            message="Conexão SSH estabelecida com sucesso",
            output=""
        )
    except Exception as e:
        return SSHResponse(
            success=False, 
            message=f"Erro ao estabelecer conexão SSH: {str(e)}",
            output=""
        )

# Endpoint para executar comandos via SSH
@router.post("/execute")
def execute_ssh_command(request: SSHCommandRequest) -> SSHResponse:
    try:
        client, error = create_ssh_client(
            request.hostname, 
            request.port, 
            request.username, 
            request.password
        )
        
        if error:
            return SSHResponse(success=False, message=f"Erro ao conectar: {error}", output="")
            
        stdin, stdout, stderr = client.exec_command(request.command)
        output = stdout.read().decode()
        error_output = stderr.read().decode()
        
        client.close()
        
        if error_output:
            return SSHResponse(
                success=False, 
                message="Comando executado com erros", 
                output=error_output
            )
            
        return SSHResponse(
            success=True, 
            message="Comando executado com sucesso", 
            output=output
        )
    except Exception as e:
        return SSHResponse(
            success=False, 
            message=f"Erro ao executar comando: {str(e)}",
            output=""
        )
