from flask import Flask, render_template, request
# Importa las funciones de tu script financiero aquí, por ejemplo:
from financial_script import obtener_datos, calcular_metricas, cumple_criterios_inversion, consultar_openai
 # Cambia esto al símbolo de la empresa que deseas analizar
 
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symbol = request.form["symbol"]
        tipo_inversionista = request.form["inversionista"]
        #symbol = "AMZN"
        # Llama a las funciones de tu script financiero aquí y pasa el símbolo
        datos = obtener_datos(symbol)
        
        if not datos:
            return render_template("error.html", symbol=symbol)
        
        metricas = calcular_metricas(datos)
        cumple_criterios = cumple_criterios_inversion(metricas, tipo_inversionista)
        nombre_empresa = datos["nombre_empresa"]
        
        analisis_openai = consultar_openai(nombre_empresa, metricas)
        
        return render_template("result.html", symbol=symbol, nombre_empresa=nombre_empresa, metricas=metricas, cumple_criterios=cumple_criterios,analisis_openai=analisis_openai)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
