from flask import Flask, request, jsonify
import random
import datetime
from fpdf import FPDF
from email.message import EmailMessage
from email.utils import formatdate
import os
import smtplib

# ========= CONFIGURACIÓN ==========
TU_CORREO = "pamicasashop43@gmail.com"  # <- reemplaza por el nuevo correo
APP_PASSWORD = os.getenv("APP_PASSWORD")    # <- la clave estará como variable secreta
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ==================================

app = Flask(__name__)

def generar_factura(telefono, monto, estado):
    pdf = FPDF()
    pdf.add_page()
    pdf.image("logo_fullmegas.png", x=10, y=8, w=40)
    
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(34, 139, 34) if estado == "Pagada" else pdf.set_text_color(255, 140, 0)
    pdf.cell(200, 40, f"Factura {estado}", ln=True, align='C')

    pdf.set_text_color(0)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, "Servicio: Recarga celular", ln=True)
    pdf.cell(200, 10, f"Nro. de operación: {random.randint(100000000, 999999999)}", ln=True)
    pdf.cell(200, 10, f"Teléfono del cliente: {telefono}", ln=True)
    pdf.cell(200, 10, f"Acreditado: {monto}", ln=True)
    pdf.cell(200, 10, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    nombre_archivo = f"factura_{telefono}_{estado}.pdf"
    pdf.output(nombre_archivo)
    return nombre_archivo

def enviar_factura(pdf_filename, destinatarios):
    msg = EmailMessage()
    msg['Subject'] = 'Factura - FullMegas'
    msg['From'] = TU_CORREO
    msg['To'] = ", ".join(destinatarios)
    msg['Date'] = formatdate(localtime=True)
    msg.set_content("Adjunto encontrará su factura de recarga celular.\n\nGracias por confiar en FullMegas.")

    with open(pdf_filename, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=pdf_filename)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(TU_CORREO, APP_PASSWORD)
        smtp.send_message(msg)

    os.remove(pdf_filename)

@app.route("/generar", methods=["POST"])
def generar():
    data = request.get_json()
    telefono = data["telefono"]
    monto = data["monto"]
    estado = data["estado"]
    
    archivo = generar_factura(telefono, monto, estado)
    enviar_factura(archivo, [TU_CORREO])  # Siempre a tu correo
    return jsonify({"status": "Factura enviada"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
