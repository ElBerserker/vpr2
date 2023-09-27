from flask import Flask, render_template, request, jsonify
import math
from operator import itemgetter

app = Flask(__name__)

coord = {}
pedidos = {}
almacen = None
max_carga = None

def distancia(coord1, coord2):#Calcula la distancia eucladiana entre dos conjuntos de cooredenadas.
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]

    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def en_ruta(rutas, c):#Determina si un cliente ya tiene asignado una ruta.
    ruta = None
    for r in rutas:
        if c in r:
            ruta = r 
    return ruta

def peso_ruta(ruta):#Calcula la demanda total de los clientes en la ruta.
    total = 0
    for c in ruta:
        total = total + pedidos[c]
    return total

# Calcular los ahorros

def vrp_voraz():
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2:
                if not (c2, c1) in s:
                    d_c1_c2 = distancia(coord[c1], coord[c2])
                    d_c1_almacen = distancia(coord[c1], almacen)
                    d_c2_almacen = distancia(coord[c2], almacen)
                    s[c1, c2] = d_c1_almacen + d_c2_almacen - d_c1_c2
    # Ordenar Ahorros
    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    # Construir las rutas
    rutas = []
    for k, v in s:
        rc1 = en_ruta(rutas, k[0])
        rc2 = en_ruta(rutas, k[1])
        if rc1 == None and rc2 == None:
            # No están en ninguna ruta. Crear la ruta
            if peso_ruta([k[0], k[1]]) <= max_carga:
                rutas.append([k[0], k[1]])
        elif rc1 != None and rc2 == None:
            # Ciudad 1 ya está en ruta. Agregar la ciudad 2
            if rc1[0] == k[0]:
                if peso_ruta(rc1) + peso_ruta([k[1]]) <= max_carga:
                    rutas[rutas.index(rc1)].insert(0, k[1])
            elif rc1[len(rc1) - 1] == k[0]:
                if peso_ruta(rc1) + peso_ruta([k[1]]) <= max_carga:
                    rutas[rutas.index(rc1)].append(k[1])
        elif rc1 == None and rc2 != None:
            if rc2[0] == k[1]:
                if peso_ruta(rc2) + peso_ruta([k[0]]) <= max_carga:
                    rutas[rutas.index(rc2)].insert(0, k[0])
            elif rc2[len(rc2) - 1] == k[1]:
                if peso_ruta(rc2) + peso_ruta([k[0]]) <= max_carga:
                    rutas[rutas.index(rc2)].append(k[0])
        elif rc1 != None and rc2 != None and rc1 != rc2:
            # Ciudad 1 y 2 ya están en una ruta. Unir las rutas
            if rc1 == k[0] and rc2[len(rc2) - 1] == k[1]:
                if peso_ruta(rc1) + peso_ruta(rc2) <= max_carga:
                    rutas[rutas.index(rc2)].extend(rc1)
                    rutas.remove(rc1)
            elif rc1[len(rc1) - 1] == k[0] and rc2[0] == k[1]:
                if peso_ruta(rc1) + peso_ruta(rc2) <= max_carga:
                    rutas[rutas.index(rc1)].extend(rc2)
                    rutas.remove(rc2)
    return rutas

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/registrar_ciudad', methods=['POST'])
def registrar_ciudad():
    try:
        # Obtener los valores de latitud y longitud desde el formulario
        ciudad = str(request.form['ciudad'])
        latitud = float(request.form['latitud'])
        longitud = float(request.form['longitud'])   

        #return render_template('resultado.html',nombre=nombre, latitud=latitud, longitud=longitud)
        coord[ciudad] = (latitud, longitud)
        return jsonify({"mensaje": f"Coordenadas de {ciudad} configuradas correctamente"})
    except ValueError:
        error_msg = "Por favor, ingresa todos los valores"
        return render_template('index.html', error_msg=error_msg)

@app.route('/registrar_pedido', methods=['POST'])
def registrar_pedido():
    try:
        # Obtener los valores de latitud y longitud desde el formulario
        ciudad = str(request.form['ciudad'])
        numero = int(request.form['numero'])

        #return render_template('resultado.html',nombre=nombre, latitud=latitud, longitud=longitud)
        pedidos[ciudad] = numero
        return jsonify({"mensaje": f"Pedido para {ciudad} configurado correctamente"})

    except ValueError:
        error_msg = "Por favor, ingresa todos los valores"
        return render_template('index.html', error_msg=error_msg)
    
@app.route('/registrar_almacen', methods=['POST'])
def registrar_almacen():
    try:
        # Obtener los valores de latitud y longitud desde el formulario
        latitud = float(request.form['latitud'])
        longitud = float(request.form['longitud'])

        global almacen
        almacen = (latitud, longitud)
        return jsonify({"mensaje": "Almacén configurado correctamente"})
        #return render_template('resultado.html',nombre=nombre, latitud=latitud, longitud=longitud)
        #pedidos[ciudad] = numero
        #return jsonify({"mensaje": f"Pedido para {ciudad} configurado correctamente"})

    except ValueError:
        error_msg = "Por favor, ingresa todos los valores"
        return render_template('index.html', error_msg=error_msg)

@app.route('/configurar_maxima_carga', methods=['POST'])
def registrar_maxima_carga():
    try:
        global max_carga
        # Obtener los valores de latitud y longitud desde el formulario
        max_carga = int(request.form['max_carga'])        

        return jsonify({"mensaje": f"Carga máxima configurada: {max_carga}"})

        #return render_template('resultado.html',nombre=nombre, latitud=latitud, longitud=longitud)
        #pedidos[ciudad] = numero
        #return jsonify({"mensaje": f"Pedido para {ciudad} configurado correctamente"})

    except ValueError:
        error_msg = "Por favor, ingresa todos los valores"
        return render_template('index.html', error_msg=error_msg)

@app.route('/calcular_ruta', methods=['GET'])
def calcular_ruta():
    try:
        if coord and pedidos and almacen and max_carga:
            return jsonify(vrp_voraz())
            
    except ValueError:
        error_msg = "Por favor, ingresa valores válidos de latitud y longitud."
        return render_template('index.html', error_msg=error_msg)

if __name__ == '__main__':
    app.run(debug=True)
