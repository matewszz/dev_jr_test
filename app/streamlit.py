import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Previsão do Tempo", page_icon="⛅", layout="wide")

# URL da sua API FastAPI (altere conforme necessário)
API_BASE_URL = "http://localhost:8000"  # Assumindo que está rodando localmente

# Título e descrição
st.title("🌦️ Sistema de Previsão do Tempo")
st.markdown("""
Consulte previsões meteorológicas de cidades ao redor do mundo utilizando nossa API.
""")

# Sidebar com informações
with st.sidebar:
    st.header("Sobre")
    st.markdown("""
    Esta aplicação consome dados da API WeatherAPI através do nosso servidor FastAPI.
    
    - Busque previsões por cidade
    - Visualize histórico de consultas
    - Acesse dados detalhados
    """)

# Seção principal
tab1, tab2, tab3 = st.tabs(["Buscar Previsão", "Consultar Histórico", "Dados Detalhados"])

with tab1:
    st.header("Buscar Previsão do Tempo")
    
    # Formulário para buscar nova previsão
    with st.form("buscar_previsao"):
        cidade = st.text_input("Digite o nome da cidade:", placeholder="Ex: São Paulo, New York, Tóquio")
        buscar = st.form_submit_button("Buscar Previsão")
    
    if buscar and cidade:
        try:
            # Chamada à API FastAPI
            response = requests.post(f"{API_BASE_URL}/criar_previsao/{cidade}")

            if response.status_code == 200:
                data = response.json()
                st.success(data["message"])
                
                # Busca os registros mais recentes da cidade
                registros = requests.get(f"{API_BASE_URL}/previsao/cidade/{cidade}").json()
                
                if registros:
                    # Pega o registro mais recente
                    ultimo_registro = registros[0]
                    
                    # Exibe os dados principais
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Temperatura", f"{ultimo_registro['temperatura_c']}°C", f"{ultimo_registro['temperatura_f']}°F")
                    with col2:
                        st.metric("Sensação Térmica", f"{ultimo_registro['sensacao_termica_c']}°C", f"{ultimo_registro['sensacao_termica_f']}°F")
                    with col3:
                        st.metric("Umidade", f"{ultimo_registro['umidade']}%")
                    
                    # Exibe informações adicionais
                    st.subheader("Condições Atuais")
                    st.write(f"**Descrição:** {ultimo_registro['descricao_clima']}")
                    st.write(f"**Vento:** {ultimo_registro['vento_kph']} km/h ({ultimo_registro['vento_direcao']})")
                    st.write(f"**Pressão:** {ultimo_registro['pressao_mb']} mb")
                    st.write(f"**Precipitação:** {ultimo_registro['precipitacao_mm']} mm")
                    st.write(f"**Nuvens:** {ultimo_registro['nuvens']}%")
                    st.write(f"**Última atualização:** {ultimo_registro['data_previsao']}")
                    
            elif response.status_code == 400:
                st.error("Erro ao buscar dados da cidade. Verifique o nome e tente novamente.")
            else:
                st.error(f"Erro na API: {response.json().get('detail', 'Erro desconhecido')}")
                
        except Exception as e:
            st.error(f"Erro ao conectar com a API: {str(e)}")

with tab2:
    st.header("Consultar Histórico")
    
    # Opções de consulta
    consulta_tipo = st.radio("Consultar por:", ["Todas as cidades", "Cidade específica", "Cidade e data"])
    
    if consulta_tipo == "Todas as cidades":
        if st.button("Buscar todos os registros"):
            try:
                registros = requests.get(f"{API_BASE_URL}/previsao").json()
                if registros:
                    df = pd.DataFrame(registros)
                    st.dataframe(df)
                else:
                    st.warning("Nenhum registro encontrado.")
            except Exception as e:
                st.error(f"Erro ao buscar registros: {str(e)}")
    
    elif consulta_tipo == "Cidade específica":
        cidade_hist = st.text_input("Digite o nome da cidade para histórico:")
        if st.button("Buscar histórico da cidade") and cidade_hist:
            try:
                registros = requests.get(f"{API_BASE_URL}/previsao/cidade/{cidade_hist}").json()
                if registros:
                    df = pd.DataFrame(registros)
                    st.dataframe(df)
                    
                    # Gráfico de temperatura ao longo do tempo
                    if len(registros) > 1:
                        df['data_previsao'] = pd.to_datetime(df['data_previsao'])
                        st.line_chart(df.set_index('data_previsao')['temperatura_c'])
                else:
                    st.warning(f"Nenhum registro encontrado para {cidade_hist}.")
            except Exception as e:
                st.error(f"Erro ao buscar registros: {str(e)}")
    
    elif consulta_tipo == "Cidade e data":
        col1, col2 = st.columns(2)
        with col1:
            cidade_data = st.text_input("Nome da cidade:")
        with col2:
            data_consulta = st.date_input("Data da previsão:")
        
        if st.button("Buscar por cidade e data") and cidade_data and data_consulta:
            try:
                data_formatada = data_consulta.strftime("%Y-%m-%d")
                registros = requests.get(
                    f"{API_BASE_URL}/previsao?cidade={cidade_data}&data/{data_formatada}"
                ).json()
                
                if registros:
                    df = pd.DataFrame(registros)
                    st.dataframe(df)
                else:
                    st.warning(f"Nenhum registro encontrado para {cidade_data} em {data_formatada}.")
            except Exception as e:
                st.error(f"Erro ao buscar registros: {str(e)}")

with tab3:
    st.header("Dados Detalhados por ID")
    
    registro_id = st.number_input("Digite o ID do registro:", min_value=1, step=1)
    if st.button("Buscar registro por ID"):
        try:
            registro = requests.get(f"{API_BASE_URL}/previsao/{registro_id}").json()
            if registro:
                st.json(registro)
            else:
                st.warning(f"Nenhum registro encontrado com ID {registro_id}.")
        except Exception as e:
            st.error(f"Erro ao buscar registro: {str(e)}")
    
    if st.button("Deletar registro por ID", type="primary"):
        try:
            response = requests.delete(f"{API_BASE_URL}/previsao/{registro_id}")
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json().get("detail", "Erro ao deletar registro"))
        except Exception as e:
            st.error(f"Erro ao conectar com a API: {str(e)}")

# Rodapé
st.markdown("---")
st.markdown("© 2023 Sistema de Previsão do Tempo - Todos os direitos reservados MM")