import streamlit as st
import pandas as pd
import datetime
import csv
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# CONFIGURACIÓN
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_BASE_ID = '1rByjj9IzT6nhUyvnZVJSUMprOWU0axKD'

@st.cache_resource
def conectar_drive():
    service_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(
        service_info, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

service = conectar_drive()

# Funciones auxiliares
def buscar_id_carpeta(nombre, padre_id):
    query = f"name='{nombre}' and '{padre_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    resultados = service.files().list(
        q=query,
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    archivos = resultados.get('files', [])
    return archivos[0]['id'] if archivos else None

def subir_a_drive(nombre_archivo, archivo_stream, tipo_mime, carpeta_id):
    media = MediaIoBaseUpload(archivo_stream, mimetype=tipo_mime, resumable=True)
    metadata = {'name': nombre_archivo, 'parents': [carpeta_id]}
    archivo = service.files().create(
        body=metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()
    return archivo.get('id')

def listar_archivos(carpeta_id):
    query = f"'{carpeta_id}' in parents and trashed=false"
    archivos = service.files().list(
        q=query,
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute().get('files', [])
    return archivos

def eliminar_archivo(archivo_id):
    service.files().delete(fileId=archivo_id, supportsAllDrives=True).execute()

# CARGA ESTRUCTURA
df = pd.read_excel("estructura_final_189_proyectos.xlsx")
df.fillna("", inplace=True)

st.title("📄 Plataforma de Carga de Archivos")

usuario = st.text_input("Nombre de quien sube el archivo:")
proyecto = st.selectbox("Selecciona un proyecto:", sorted(df["Nombre del proyecto"].unique()))
df_proyecto = df[df["Nombre del proyecto"] == proyecto]

sub1 = st.selectbox("Selecciona subcarpeta 1:", sorted(df_proyecto["Subcarpeta 1"].unique()))
df_sub1 = df_proyecto[df_proyecto["Subcarpeta 1"] == sub1]

sub2 = st.selectbox("Selecciona subcarpeta 2:", sorted(df_sub1["Subcarpeta 2"].unique())) if any(df_sub1["Subcarpeta 2"]) else ""

archivo = st.file_uploader("Selecciona archivo a subir", type=["pdf", "docx", "xlsx", "csv", "jpg", "png", "txt", "dwg", "kmz", "zip"])

if archivo and st.button("Subir archivo"):
    if not usuario.strip():
        st.warning("Debes ingresar tu nombre antes de subir.")
        st.stop()

    id_proyecto = buscar_id_carpeta(proyecto, FOLDER_BASE_ID)
    if not id_proyecto:
        st.error(f"No se encontró la carpeta del proyecto: {proyecto}")
        st.stop()

    id_sub1 = buscar_id_carpeta(sub1, id_proyecto)
    if not id_sub1:
        st.error(f"No se encontró la subcarpeta 1: {sub1}")
        st.stop()

    destino = buscar_id_carpeta(sub2, id_sub1) if sub2 else id_sub1
    if sub2 and not destino:
        st.error(f"No se encontró la subcarpeta 2: {sub2}")
        st.stop()

    subir_a_drive(archivo.name, archivo, archivo.type, destino)
    st.success("✅ Archivo subido correctamente.")

    with open("registro_subidas.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        writer.writerow([timestamp, usuario, proyecto, sub1, sub2, archivo.name])

st.divider()
st.subheader("🔍 Eliminar archivos erróneos")

if st.checkbox("Mostrar archivos cargados para eliminar"):
    if not proyecto or not sub1:
        st.warning("Debes seleccionar un proyecto y subcarpetas antes de listar.")
    else:
        id_proyecto = buscar_id_carpeta(proyecto, FOLDER_BASE_ID)
        id_sub1 = buscar_id_carpeta(sub1, id_proyecto)
        destino = buscar_id_carpeta(sub2, id_sub1) if sub2 else id_sub1

        archivos = listar_archivos(destino)
        nombres = {f["name"]: f["id"] for f in archivos}
        if nombres:
            seleccion = st.selectbox("Selecciona archivo a eliminar:", list(nombres.keys()))
            if st.button("❌ Eliminar archivo"):
                eliminar_archivo(nombres[seleccion])
                st.success("✅ Archivo eliminado correctamente.")
        else:
            st.info("No hay archivos disponibles para eliminar en esta ruta.")
