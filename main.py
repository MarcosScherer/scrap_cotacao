from fastapi import FastAPI
from pydantic import BaseModel
from scraper2 import run_scraper

app = FastAPI()


class ScraperInput(BaseModel):
    cpf_cnpj_login: str
    senha: str
    valor_imovel: str | None = None
    tipo_imovel: str
    tipo_residencia: str
    casa_em_condominio: str | None = None
    tipo_apartamento: str | None = None
    sucursal: str
    codigo_cpd: str
    nome_contato: str
    telefone_celular: str
    email: str
    cpf_cnpj_proponente: str
    cep: str
    numero: str
    tipo_cliente: str
    tipo_seguro: str
    construcao_alvenaria_imovel: str
    objeto_seguro: str
    assistencia_24h_inicial: str
    assistencia_24h_recalculo: str | None = None
    assistencia_24h_recalculo_2: str | None = None
    resid_home_office: str
    resid_atividade_comercial: str
    comissao: float


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/run-scraper")
def run_scraper_endpoint(data: ScraperInput):
    resultado = run_scraper(data)

    return {
        "success": True,
        "entrada": data.model_dump(),
        "saida": resultado
    }