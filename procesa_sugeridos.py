#!/usr/bin/python
from datetime import datetime
import sqlite3
import re
import html
import urllib.request
import requests
import os
import token_bot
import constantes
import path
import token_bot

os.chdir(path.actual)

######### Conecta con la base de datos
def conecta_db():
    conn = sqlite3.connect(constantes.db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    return conn

def procesa():
    print(f"Sitio: {sitio_nom}")
    print(f'URL: {constantes.sitio_URL[sitio_nom]}{sitio_id}')
    resp = input("¿Agregar? (M/S/N): ")
    if resp == "M":
        id_n = input("Ingrese la nueva id: ")
        conn.execute ('INSERT INTO juegos (BGG_id,nombre,sitio,sitio_ID,fecha_agregado) VALUES (?,?,?,?,?)',(int(BGG_id),nombre,sitio_nom,id_n,fecha))
        conn.commit()
        conn.execute ('DELETE FROM juegos_sugeridos WHERE id_juego_sugerido = ?',[id_juego_sugerido])
        conn.commit()
        send_text = f'https://api.telegram.org/bot{token_bot.token}/sendMessage?chat_id={str(usuario_id)}&parse_mode=Markdown&text=El juego {nombre} que sugeriste fue agregado al monitoreo. Muchas gracias.'
        response = requests.get(send_text)
    elif resp == "S":
        conn.execute ('INSERT INTO juegos (BGG_id,nombre,sitio,sitio_ID,fecha_agregado) VALUES (?,?,?,?,?)',(int(BGG_id),nombre,sitio_nom,sitio_id,fecha))
        conn.commit()
        conn.execute ('DELETE FROM juegos_sugeridos WHERE id_juego_sugerido = ?',[id_juego_sugerido])
        conn.commit()
        send_text = f'https://api.telegram.org/bot{token_bot.token}/sendMessage?chat_id={str(usuario_id)}&parse_mode=Markdown&text=El juego {nombre} que sugeriste fue agregado al monitoreo. Muchas gracias.'
        response = requests.get(send_text)
    else:
        razon = input("Razón: ")
        conn.execute ('DELETE FROM juegos_sugeridos WHERE id_juego_sugerido = ?',[id_juego_sugerido])
        conn.commit()
        send_text = f'https://api.telegram.org/bot{token_bot.token}/sendMessage?chat_id={str(usuario_id)}&parse_mode=Markdown&text=El juego {nombre} que sugeriste *NO* fue agregado al monitoreo.\n{razon}\nMuchas gracias.'
        response = requests.get(send_text)
    return

conn = conecta_db()
cursor = conn.cursor()
cursor.execute('SELECT * FROM juegos_sugeridos')
juegos = cursor.fetchall()
for j in juegos:
    id_juego_sugerido,usuario_nom,usuario_id,BGG_URL,sitio_url,fecha = j
    # print(f"\n{usuario_nom} - {usuario_id} - {BGG_URL} - {sitio_url} - {fecha}\n")
    fecha = datetime.now()

    print(f"\n\nUsuario: {usuario_nom}")
    print(f"BGG_URL: {BGG_URL}")
    print(f"sitio_url: {sitio_url}")

    BGG_id = re.search('boardgamegeek\.com/boardgame.*?/(.*?)($|/)',BGG_URL)[1]

    print(f"BGG_id: {BGG_id}")

    url = 'https://api.geekdo.com/xmlapi2/thing?id='+BGG_id
    req = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}) 
    data = urllib.request.urlopen(req).read()
    data = data.decode('utf-8')

    nombre = html.unescape(re.search('<name type="primary" sortindex=".*?" value="(.*?)"',data)[1])

    print("Nombre: ",nombre)

    cursor.execute ('SELECT sitio,sitio_ID FROM juegos WHERE BGG_id = ?',[int(BGG_id)])
    moni = cursor.fetchall()
    for m in moni:
        sitio, sitio_ID = m
        print (f"*** Ya está siendo monitoreado desde {sitio}: {sitio_ID}")

    sitio_id = re.search('buscalibre\.com\.ar\/amazon\?url=(.*?)(\s|$|\/|\?|&)',sitio_url)
    if sitio_id:
        sitio_nom = "BLAM"
        sitio_id = sitio_id[1]
        procesa()
        continue

    sitio_id = re.search('buscalibre\.com\.ar\/(.*?)$',sitio_url)
    if sitio_id:
        sitio_nom = "BLIB"
        sitio_id = sitio_id[1]
        procesa()
        continue

    sitio_id = re.search('bookdepository.com\/es\/.*?\/(.*?)(\s|$|\/|\?|&)',sitio_url)
    if sitio_id:
        sitio_nom = "BOOK"
        sitio_id = sitio_id[1]
        procesa()
        continue

    sitio_id = re.search('tiendamia\.com(\/|.)ar\/producto\?amz=(.*?)(\s|$|\/|\?|&)',sitio_url)
    if sitio_id:
        sitio_nom = "TMAM"
        sitio_id = sitio_id[2]
        procesa()
        continue

    sitio_id = re.search('tiendamia\.com(\/|.)ar\/productow\?wrt=(.*?)(\s|$|\/|\?|&)',sitio_url)
    if sitio_id:
        sitio_nom = "TMWM"
        sitio_id = sitio_id[2]
        procesa()
        continue

    sitio_id = re.search('tiendamia\.com(\/|.)ar\/e-product\?ebay=(.*?)(\s|$|\/|\?|&)',sitio_url)
    if sitio_id:
        sitio_nom = "TMEB"
        sitio_id = sitio_id[2]
        procesa()
        continue

    sitio_id = re.search('365games\.co\.uk\/(.*?)$',sitio_url)
    if sitio_id:
        sitio_nom = "365"
        sitio_id = sitio_id[1]
        procesa()
        continue

    sitio_id = re.search('shop4es\.com\/(.*?)$',sitio_url)
    if sitio_id:
        sitio_nom = "shop4es"
        sitio_id = sitio_id[1]
        procesa()
        continue

    sitio_id = re.search('shop4world\.com\/(.*?)$',sitio_url)
    if sitio_id:
        sitio_nom = "shop4world"
        sitio_id = sitio_id[1]
        procesa()
        continue

cursor.close()

# DELETE FROM juegos_sugeridos WHERE id_juego_sugerido = 8;
# UPDATE juegos_sugeridos SET URL = "https://www.buscalibre.com.ar/amazon?url=0994487606" WHERE id_juego_sugerido = 8;