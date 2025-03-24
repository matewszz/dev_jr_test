import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from unidecode import unidecode

from app.database import SessionLocal, engine
from app.models import RegistroClimatico

from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Cria o registro caso não exista no banco e cso já exista ele simplesmente pula
@app.post("/criar_previsao/{cidade}")
def criar_previsao(cidade: str, db: Session = Depends(get_db)):
    try:
        params = {"q": cidade, "key": API_KEY, "aqi": "no"}
        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Erro ao buscar dados da API")

        data = response.json()

        nome_cidade = data["location"]["name"]
        pais = data["location"]["country"]
        ultima_att = datetime.strptime(
            data["current"]["last_updated"], "%Y-%m-%d %H:%M"
        )
        temp = data["current"]["temp_c"]

        # Verifica se já existe um registro para essa cidade na mesma data
        cidade_existente = (
            db.query(RegistroClimatico)
            .filter_by(cidade=nome_cidade, data_previsao=ultima_att, pais=pais)
            .first()
        )

        if cidade_existente:
            return {
                "message": f"Não há atualização para {nome_cidade} desde a última registrada em {ultima_att}, quando a temperatura estava {temp}°C."
            }

        # Dados da API
        clima_info = RegistroClimatico(
            cidade=nome_cidade,
            pais=pais,
            temperatura_c=data["current"]["temp_c"],
            temperatura_f=data["current"]["temp_f"],
            sensacao_termica_c=data["current"]["feelslike_c"],
            sensacao_termica_f=data["current"]["feelslike_f"],
            descricao_clima=data["current"]["condition"]["text"],
            registrado_em=datetime.utcnow(),
            data_previsao=ultima_att,
            vento_mph=data["current"]["wind_mph"],
            vento_kph=data["current"]["wind_kph"],
            vento_grau=data["current"]["wind_degree"],
            vento_direcao=data["current"]["wind_dir"],
            pressao_mb=data["current"]["pressure_mb"],
            pressao_in=data["current"]["pressure_in"],
            precipitacao_mm=data["current"]["precip_mm"],
            umidade=data["current"]["humidity"],
            nuvens=data["current"]["cloud"],
        )

        db.add(clima_info)
        db.commit()

        return {
            "message": f"Previsão do tempo cadastrada para {nome_cidade} de {ultima_att}"
        }

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Erro interno: {ex}")


# Todos registros
@app.get("/previsao")
def obter_registros(db: Session = Depends(get_db)):
    try:
        registros = db.query(RegistroClimatico).all()

        if not registros:
            raise HTTPException(status_code=404, detail="Nenhum registro encontrado")

        return registros
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar registros: {ex}")


# Busca o registro pelo ID
@app.get("/previsao/{id}")
def obter_registro_por_id(id: int, db: Session = Depends(get_db)):
    try:
        registro = (
            db.query(RegistroClimatico).filter(RegistroClimatico.id == id).first()
        )

        if not registro:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

        return registro
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar registro: {ex}")


# Busca registros pela cidade
@app.get("/previsao/cidade/{cidade}")
def obter_registro_por_cidade(cidade: str, db: Session = Depends(get_db)):
    try:
        cidade = unidecode(cidade).title()
        print(cidade)
        registros = (
            db.query(RegistroClimatico).filter(RegistroClimatico.cidade == cidade).all()
        )

        if not registros:
            raise HTTPException(
                status_code=404, detail="Nenhum registro encontrado para a cidade"
            )

        return registros
    except Exception:
        raise HTTPException(status_code=500, detail="Não existe registros dessa cidade")


# Busca o registro pela cidade e data de previsão
@app.get("/previsao?cidade={cidade}&data/{data_previsao}")
def obter_registro_por_cidade_data(
    cidade: str, data_previsao: str, db: Session = Depends(get_db)
):
    try:
        cidade = unidecode(cidade).title()

        data_obj = datetime.strptime(data_previsao, "%Y-%m-%d").date()

        print(data_obj)
        registro = (
            db.query(RegistroClimatico)
            .filter(
                RegistroClimatico.cidade == cidade,
                func.date(RegistroClimatico.data_previsao) == data_previsao,
            )
            .all()
        )

        if not registro:
            raise HTTPException(
                status_code=404,
                detail="Registro não encontrado para a cidade e data fornecidas",
            )

        return registro
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de data inválido. Use YYYY-MM-DD. Erro: {ve}",
        )
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar registro por cidade e data: {str(ex)}",
        )


# Deletar o registro pelo ID
@app.delete("/previsao/{id}")
def delete_registro_por_id(id: int, db: Session = Depends(get_db)):
    try:
        registro = (
            db.query(RegistroClimatico).filter(RegistroClimatico.id == id).first()
        )

        if not registro:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

        db.delete(registro)
        db.commit()

        return {"message": "Registro deletado com sucesso"}
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar registro: {ex}")
