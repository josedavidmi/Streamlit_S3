import streamlit as st
import pandas as pd
import boto3
from streamlit_autorefresh import st_autorefresh
from io import BytesIO

st.set_page_config(page_title="Dashboard S3 en tiempo real", layout="wide")

# Refresca la app cada 5 segundos (5000 ms)
st.autorefresh(interval=5000, key="refresh")

BUCKET = "s3-examen-bda-2025121-iabd00"
KEY = "streamlit/log_streamlit.log"   # por ejemplo: "streamlit/log_streamlit"
#REGION = "us-east-1"          # ajusta si aplica

@st.cache_data(ttl=5)  # evita recalcular más de lo necesario entre refreshes
def read_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    # Credenciales desde st.secrets (Streamlit Cloud)
    session = boto3.session.Session(
        # Credenciales referenciadas por nombre, NO el valor real
    session = boto3.session.Session(
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        aws_session_token=st.secrets.get("AWS_SESSION_TOKEN"),
    )
    )
    s3 = session.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read()
    return pd.read_csv(BytesIO(data))

st.title("Dashboard en streaming (S3 -> Streamlit Cloud)")

try:
    df = read_csv_from_s3(BUCKET, KEY)

    st.subheader("Últimas filas")
    st.dataframe(df.tail(15), use_container_width=True)

    # Ejemplo: si existe una columna numérica "valor"
    if "valor" in df.columns:
        st.metric("Último valor", df["valor"].iloc[-1])
        st.line_chart(df["valor"])

except Exception as e:
    st.error("No se pudo leer el fichero desde S3.")
    st.exception(e)
