from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class RegistroClimatico(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    cidade = Column(String, index=True, nullable=True)
    pais = Column(String, nullable=True)
    
    # Temperaturas
    temperatura_c = Column(Float, nullable=True)
    temperatura_f = Column(Float, nullable=True)
    sensacao_termica_c = Column(Float, nullable=True)
    sensacao_termica_f = Column(Float, nullable=True)

    # Clima
    descricao_clima = Column(String, nullable=True)  # Condição climática geral
    registrado_em = Column(DateTime, default=datetime.utcnow, nullable=True)
    data_previsao = Column(DateTime, nullable=True)

    # Vento
    vento_mph = Column(Float, nullable=True)  # Velocidade do vento em milhas por hora
    vento_kph = Column(Float, nullable=True)  # Velocidade do vento em km/h
    vento_grau = Column(Integer, nullable=True)  # Direção do vento em graus
    vento_direcao = Column(String, nullable=True)  # Direção do vento (N, S, L, O)

    # Pressão Atmosférica
    pressao_mb = Column(Float, nullable=True)  # Pressão em milibares
    pressao_in = Column(Float, nullable=True)  # Pressão em polegadas de mercúrio

    # Precipitação e Umidade
    precipitacao_mm = Column(Float, nullable=True)  # Chuva em mm
    umidade = Column(Integer, nullable=True)  # Umidade relativa do ar (%)
    nuvens = Column(Integer, nullable=True)  # Cobertura de nuvens (%)

    def __repr__(self):
        return f"(cidade={self.cidade}, temperatura={self.temperatura})"
