# 📄 Plataforma de Carga de Archivos a Google Drive

Aplicación en Streamlit para cargar documentos organizados por proyecto, con control de versiones y eliminación de archivos erróneos.

## ⚙️ Requisitos

- Cuenta de servicio de Google con acceso a Drive
- Archivo secreto configurado como `GOOGLE_SERVICE_ACCOUNT_JSON` en Streamlit Cloud
- Archivo `estructura_final_189_proyectos.xlsx` en la raíz

## ▶️ Despliegue en Streamlit

1. Sube este repositorio a GitHub.
2. Ingresa a [https://streamlit.io/cloud](https://streamlit.io/cloud) y crea una nueva app.
3. En el formulario:
   - **Repository**: `tu_usuario/app-carga-drive`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. En la sección `Secrets`, agrega tu cuenta de servicio:

```toml
GOOGLE_SERVICE_ACCOUNT_JSON = """
{ ... el contenido completo del service_account.json ... }
"""
