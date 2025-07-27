from flask import Flask, request, jsonify
import requests
import datetime as dt

app = Flask(__name__)

def UFValue_MiIndicador(fecha_t):
    fecha_t_str = fecha_t.strftime("%d-%m-%Y")
    url = f'https://mindicador.cl/api/uf/{fecha_t_str}'
    response = requests.get(url)
    uf = response.json()["serie"][0]["valor"]
    return uf

def MortageLoan(fecha_t, valor_propiedad_uf, tasa, financiamiento_porcentual, plazo_anios, spread_cae):
    uf = UFValue_MiIndicador(fecha_t)
    periodos = plazo_anios * 12
    tasa_mensual = (1 + tasa + spread_cae)**(1/12) - 1
    monto_ptmo = valor_propiedad_uf * (1 - financiamiento_porcentual)
    cuota_uf = (monto_ptmo * tasa_mensual * (1 + tasa_mensual)**periodos) / ((1 + tasa_mensual)**periodos - 1)
    cuota_clp = cuota_uf * uf
    return {
        "pie_clp": round(valor_propiedad_uf * financiamiento_porcentual * uf, 0),
        "cuota_clp": round(cuota_clp, 0),
        "uf": round(uf, 2)
    }

@app.route('/calcular', methods=['GET'])
def calcular():
    fecha_str = request.args.get('fecha')  # YYYY-MM-DD
    fecha_t = dt.datetime.strptime(fecha_str, "%Y-%m-%d")
    valor_uf = float(request.args.get('valor_propiedad_uf'))
    tasa = float(request.args.get('tasa'))
    spread = float(request.args.get('spread', 0.0))
    pie = float(request.args.get('pie'))
    plazo = int(request.args.get('plazo'))

    resultado = MortageLoan(fecha_t, valor_uf, tasa, pie, plazo, spread)
    return jsonify(resultado)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
