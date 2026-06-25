import requests
import os
from datetime import datetime
import time
import sys

def descargar_reportes_txt(
    usuario,
    password,
    reporte,
    reportJob,
    fecha_inicio, 
    fecha_fin, 
    nombre_base_salida, 
    ruta_destino,
    range_pages,
    format="TXT"
    ):
    """
    Función parametrizada que descarga reportes en su formato original de texto (TXT).
    """
    url_login = "https://controldweb.liverpool.com.mx/api/v1/login"
    url_docs = "https://controldweb.liverpool.com.mx/api/v1/documents"
    url_download = "https://controldweb.liverpool.com.mx/api/v1/documents/file"

    try:
        valid_format = ["XLSX", "TXT"]
        if format not in valid_format:
            print("Formato no válido.", format, "VALID FORMATS XLSX TXT")
            return ValueError("EL formato no es valido solo XLSX o TXT")
        
        # Aseguramos que la carpeta de destino exista
        if not os.path.exists(ruta_destino): 
            os.makedirs(ruta_destino)

        # 1. Login
        print(">> Autenticando...")
        res_login = requests.post(url_login, json={"username": usuario, "password": password})
        token = res_login.json().get("data", {}).get("authorization")
        
        if not token:
            return print("Error: No se obtuvo token. Verifica las credenciales.")
        headers = {"Authorization": token}

        # 2. Búsqueda de documentos
        print(f">> Buscando reportes del {fecha_inicio} al {fecha_fin}...")
        payload = {
            "reportName": reporte,
            "nameJob": reportJob,
            "initDate": fecha_inicio, 
            "endDate": fecha_fin, 
            "active": True, 
            "historical": True, 
            "migrated": True, 
            "businessSelected": "QUERY_LIVERPOOL_CREDIT"
        }
        res_docs = requests.post(url_docs, json=payload, headers=headers)
        docs = res_docs.json().get("data", {}).get("documents", [])

        if not docs:
            return print(f"No se encontraron documentos para '{reporte}' en las fechas indicadas.")

        print(f">> Se encontraron {len(docs)} documento(s). Iniciando descarga...\n")
        # total_descargados = 0
        # names = ["SUBURBIA", "LIVERPOOL"]
        # 3. Descarga y guardado físico
        for doc in docs:
            f_orig = doc["date"] # Ej: "03/03/2026"
            
            # Formatear la fecha a YYYYMMDD para el nombre del archivo
            # fecha_formateada = datetime.strptime(f_orig, "%d/%m/%Y").strftime("%Y%m%d")
            
            # Nombre final del archivo: PREFIJO_yyyymmdd.txt
            nombre_archivo = f"{nombre_base_salida}.{format.lower()}"
            ruta_final = os.path.join(ruta_destino, nombre_archivo)

            print(f"Procesando fecha {f_orig} -> Creando {nombre_archivo}...")
            
            params = {
                "documentId": doc["documentId"], 
                "transactionId": res_docs.json()["data"]["transactionId"], 
                "format": format,
                "pageRanges": range_pages,
                "isDownload": "false"
            }
            res = requests.get(url_download, headers=headers, params=params)
            
            if res.status_code == 200:
                try:
                    # Validar si el servidor devuelve JSON de "en preparación"
                    info = res.json()
                    final_id = info.get("data", {}).get("downloadTransactionId") or info.get("data", {}).get("finishedDownloadId")
                    if final_id:
                        time.sleep(1.5) # Pausa técnica para que Control-D prepare el reporte
                        res = requests.get(url_download, headers=headers, params={"transactionId": final_id, "isDownload": "false"})
                except ValueError:
                    # Si falla el .json(), significa que la respuesta ya es el texto del TXT
                    pass

                # Guardado binario (wb) para mantener la codificación original del reporte
                with open(ruta_final, "wb") as f:
                    f.write(res.content)
                
                # Calcular el peso en KB para validar que no bajó vacío
                peso_kb = os.path.getsize(ruta_final) / 1024
                print(f"   -> OK: Guardado con éxito ({peso_kb:.2f} KB).")
                # total_descargados += 1
            else:
                print(f"   -> ERROR HTTP {res.status_code} al intentar descargar el ID {doc['documentId']}.")

        print(f"\n--- PROCESO COMPLETADO ---")
        # print(f"Total de archivos descargados en la ruta: {total_descargados}")

    except Exception as e:
        print(f"Falla crítica en el proceso: {str(e)}")


# ---------------------------------------------------------
# BLOQUE DE EJECUCIÓN 
# ---------------------------------------------------------
def main(report, reporJob, init_date, end_date, prefix, path, formato, range_pages):
#if __name__ == "__main__":
    try:
        expected_file = os.path.join(path, prefix+"."+formato.lower())
        
        max_intentos = 150
        segundos_espera = 2
        for intento in range(1, max_intentos + 1):
            try:
                # Variables de entrada listas para ser parametrizadas
                mi_usuario = "LJMEDRANOG"
                mi_password = "TDE1NDI5Njc1Iw==" # [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("CONTRASEÑA"))

                
                # Llamamos a la función inyectando las variables
                descargar_reportes_txt(
                    usuario=mi_usuario,
                    password=mi_password,
                    reporte=report,
                    reportJob=reporJob,
                    fecha_inicio=init_date,
                    fecha_fin=end_date,
                    nombre_base_salida=prefix,
                    ruta_destino=path,
                    format=formato,
                    range_pages=range_pages
                )
            except Exception as ErrorPython:
                print('Error on Line '+str(format(sys.exc_info()[-1].tb_lineno))+' <'+str(ErrorPython)+'>')
            
            if os.path.exists(expected_file):
                print(f"¡Exito! El archivo fue encontrado en el intento {intento}.")
                return "OK"
            
            print(f"Intento {intento}/{max_intentos}: El archivo aun no existe. Esperando...")
            time.sleep(segundos_espera)
        else:
            print(f"El archivo no aparecio despues de {max_intentos} intentos.")
            return f"El archivo no aparecio despues de {max_intentos} intentos."
    except Exception as ErrorPython:
        print('Error on Line '+str(format(sys.exc_info()[-1].tb_lineno))+' <'+str(ErrorPython)+'>')
        return f'Error on Line '+str(format(sys.exc_info()[-1].tb_lineno))+' <'+str(ErrorPython)+'>'

if __name__ == "__main__":
    # Variables de entrada listas para ser parametrizadas
    mi_usuario = "LJMEDRANOG"
    mi_password = "TDE1NDI5Njc1Iw==" # [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("CONTRASEÑA"))
    mi_reporte = "O42 FREQUENT SHOPPER TRANS JOURNAL"
    mi_fecha_inicio = "05/06/2026"
    mi_fecha_fin = "05/06/2026"
    mi_prefijo = "PLCRD093_2"
    mi_ruta = r"C:\Users\FDCOLIN\Downloads"
    mi_format = "TXT"
    mi_range_pages = ""

    main(
        report=mi_reporte,
        reporJob=mi_prefijo,
        init_date=mi_fecha_inicio,
        end_date=mi_fecha_fin,
        prefix=mi_prefijo,
        path=mi_ruta,
        range_pages=mi_range_pages,
        formato="TXT"
    )