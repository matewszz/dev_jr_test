from datetime import datetime

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import RegistroClimatico

client = TestClient(app)

def setUp():
    db = SessionLocal()
    try:
        dado = db.query(RegistroClimatico).filter_by(id=999999999999).first()

        if not dado:
            data_previsao = datetime.strptime("2025-03-24 17:45:00.000000", "%Y-%m-%d %H:%M:%S.%f")

            dado = RegistroClimatico(
                id=999999999999,
                cidade="Goiania",
                data_previsao=data_previsao,
            )
            db.add(dado)
            db.commit()
            db.refresh(dado)

        return dado

    except Exception as e:
        print(f"Erro ao criar previsão: {e}")
        raise
    finally:
        db.close()

dado = setUp()


def test_obter_todos_registros():
    response = client.get("/previsao")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


def test_obter_registro_por_id():
    response = client.get(f"/previsao/{dado.id}")
    assert response.status_code == 200


def test_obter_registro_por_cidade():
    response = client.get(f"/previsao/cidade/{dado.cidade}")
    assert response.status_code == 200

def test_obter_registro_por_cidade_data():
    response = client.get(f"/previsao?cidade={dado.cidade}&data/{dado.data_previsao}")
    assert response.status_code == 200

def test_deletar_registro():
    dado = setUp()
    response = client.delete(f"/previsao/{dado.id}")
    assert response.status_code == 200

    db = SessionLocal()
    deleted_dado = db.query(RegistroClimatico).filter_by(id=dado.id).first()
    db.close()
    
    assert deleted_dado is None