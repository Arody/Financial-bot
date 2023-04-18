import requests
import json
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]


def obtener_datos(symbol):
    
    # Reemplaza YOUR_API_KEY con la clave de API que obtuviste de Alpha Vantage
    apikey = os.environ["ALPHAVANTAGE_API_KEY"]
        # Obtiene la descripción general
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={apikey}"
    overview_response = requests.get(overview_url)
    overview_data = json.loads(overview_response.text)

    # Obtiene la hoja de balance
    balance_sheet_url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={apikey}"
    balance_sheet_response = requests.get(balance_sheet_url)
    balance_sheet_data = json.loads(balance_sheet_response.text)


    # Obtiene la cuenta de resultados
    income_statement_url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={apikey}"
    income_statement_response = requests.get(income_statement_url)
    income_statement_data = json.loads(income_statement_response.text)


    # Extrae las métricas financieras clave
    precio_accion = float(overview_data["MarketCapitalization"]) / float(overview_data["SharesOutstanding"])
    ganancias_por_accion = float(overview_data["EPS"])
    ventas_por_accion = float(overview_data["RevenueTTM"]) / float(overview_data["SharesOutstanding"])
    total_shareholder_equity = float(balance_sheet_data["annualReports"][0]["totalShareholderEquity"])
    valor_contable_por_accion = total_shareholder_equity / float(overview_data["SharesOutstanding"])
    beneficio_neto = float(income_statement_data["annualReports"][0]["netIncome"])
    ingresos_totales = float(overview_data["RevenueTTM"])
    patrimonio_neto = total_shareholder_equity
    deuda_total = float(balance_sheet_data["annualReports"][0]["longTermDebt"])
    dividend_yield = float(overview_data["DividendYield"])
    beta = float(overview_data["Beta"])
    nombre_empresa = overview_data["Name"]
    
    if "annualReports" not in balance_sheet_data or "annualReports" not in income_statement_data or not balance_sheet_data["annualReports"] or not income_statement_data["annualReports"]:
        return {}


    return {
        "precio_accion": precio_accion,
        "ganancias_por_accion": ganancias_por_accion,
        "ventas_por_accion": ventas_por_accion,
        "valor_contable_por_accion": valor_contable_por_accion,
        "beneficio_neto": beneficio_neto,
        "ingresos_totales": ingresos_totales,
        "patrimonio_neto": patrimonio_neto,
        "deuda_total": deuda_total,
        "dividend_yield": dividend_yield,
        "beta": beta,
        "nombre_empresa": nombre_empresa
    }

# Calcula las métricas financieras
def calcular_metricas(datos):
    
    print(datos)
    pe_ratio = datos["precio_accion"] / datos["ganancias_por_accion"]
    ps_ratio = datos["precio_accion"] / datos["ventas_por_accion"]
    pb_ratio = datos["precio_accion"] / datos["valor_contable_por_accion"]
    margen_beneficio_neto = datos["beneficio_neto"] / datos["ingresos_totales"]
    roe = datos["beneficio_neto"] / datos["patrimonio_neto"]
    deuda_patrimonio = datos["deuda_total"] / datos["patrimonio_neto"]
    dividend_yield = datos["dividend_yield"]
    beta = datos["beta"]

    return {
        "P/E Ratio": pe_ratio,
        "P/S Ratio": ps_ratio,
        "P/B Ratio": pb_ratio,
        "Margen de beneficio neto": margen_beneficio_neto,
        "ROE": roe,
        "Deuda/Patrimonio": deuda_patrimonio,
        "Dividend Yield": dividend_yield,
        "Beta": beta
    }

# Establece criterios de inversión
def cumple_criterios_inversion(metricas, tipo_inversionista):
    criterios = {
        "conservador": {"pe": 15, "ps": 1.5, "roe": 0.2},
        "moderado": {"pe": 20, "ps": 2, "roe": 0.15},
        "arriesgado": {"pe": 25, "ps": 2.5, "roe": 0.1}
    }

    criterio = criterios[tipo_inversionista]

    if (
        metricas["P/E Ratio"] < criterio["pe"] and
        metricas["P/S Ratio"] < criterio["ps"] and
        metricas["ROE"] > criterio["roe"]
    ):
        return True
    else:
        return False

def consultar_openai(empresa, metricas):
    prompt = f"Analiza las métricas financieras de la empresa {empresa}:\n\n"
    
    for nombre_metrica, valor_metrica in metricas.items():
        prompt += f"{nombre_metrica}: {valor_metrica}\n"
    
    prompt += "\nProporciona un breve análisis de la situación financiera de la empresa."

    response = openai.Completion.create(
        
    model="text-davinci-003",
    prompt=prompt,
    max_tokens=500,
    temperature=0.7
    
    )

    return response.choices[0].text