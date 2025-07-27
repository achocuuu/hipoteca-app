from flask import Flask, request, jsonify, render_template_string
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

@app.route('/', methods=['GET', 'POST'])
def home():
    html = """
    <h2>Simulador de Crédito Hipotecario</h2>
    <form method="post">
        Fecha (YYYY-MM-DD): <input name="fecha" value="2025-07-25"><br>
        Valor Propiedad UF: <input name="valor" value="5500"><br>
        Tasa Interés Anual (%): <input name="tasa" value="4.5"><br>
        Spread CAE (%): <input name="spread" value="0"><br>
        Pie (% del valor): <input name="pie" value="0"><br>
        Plazo (años): <input name="plazo" value="30"><br><br>
        <input type="submit" value="Calcular">
    </form>
    {% if resultado %}
        <h3>Resultado:</h3>
        <p>UF al día: {{ resultado.uf }}</p>
        <p>Pie (CLP): ${{ resultado.pie_clp }}</p>
        <p>Cuota mensual (CLP): ${{ resultado.cuota_clp }}</p>
    {% endif %}
    """
    
    if request.method == 'POST':
        fecha = request.form['fecha']
        valor = float(request.form['valor'])
        tasa = float(request.form['tasa']) / 100
        spread = float(request.form['spread']) / 100
        pie = float(request.form['pie']) / 100
        plazo = int(request.form['plazo'])

        fecha_t = dt.datetime.strptime(fecha, "%Y-%m-%d")
        resultado = MortageLoan(fecha_t, valor, tasa, pie, plazo, spread)
        return render_template_string(html, resultado=resultado)

    return render_template_string(html, resultado=None)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
