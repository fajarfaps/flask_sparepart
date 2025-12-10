from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, send_file
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
import io
import base64
import pickle
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import KeepTogether
from reportlab.lib.utils import ImageReader
from flask import send_file
from reportlab.lib.units import cm
from PIL import Image as PILImage
import io

main = Blueprint ('main', __name__)


# Dummy akun
USER_CREDENTIAL = {
    'Admin': 'admin123'
}


@main.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USER_CREDENTIAL and USER_CREDENTIAL[username] == password:
            session['user'] = username
            return redirect(url_for('main.dashboard'))
        flash('Login gagal. Coba lagi!', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main.login'))

@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    df = pd.read_csv("app/penjualan_clean_updated.csv")
    return render_template('dashboard.html', user=session['user'], data=df.to_dict(orient='records'))

@main.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    hasil = None
    error = None
    accuracy = None

    if request.method == 'POST':
        Stok = request.form['Stok']
        Jumlah = request.form['Jumlah']
        Harga = request.form['Harga']
        Kategori = request.form['Kategori']

        try:
            with open("models/decision_tree.pkl", "rb") as f:
                clf, encoders, accuracy = pickle.load(f)  # ✅ Ambil accuracy dari model

            fitur_encoded = [
                encoders['Stok'].transform([Stok])[0],
                encoders['Jumlah'].transform([Jumlah])[0],
                encoders['Harga'].transform([Harga])[0],
                encoders['Kategori'].transform([Kategori])[0],
            ]

            pred = clf.predict([fitur_encoded])[0]
            hasil = encoders['Klasifikasi'].inverse_transform([pred])[0]

            session['prediksi'] = {
                'Stok': Stok,
                'Jumlah': Jumlah,
                'Harga': Harga,
                'Kategori': Kategori,
                'hasil': hasil,
                'accuracy': accuracy  # ✅ Akurasi langsung dari model
            }

        except ValueError as e:
            error = f"❌ Terjadi kesalahan saat prediksi: {e}"

    return render_template('prediksi.html', hasil=hasil, error=error, accuracy=accuracy)

@main.route('/cetak-hasil-prediksi', methods=['POST'])
def cetak_hasil_prediksi():
    if 'user' not in session or 'prediksi' not in session:
        return redirect(url_for('main.login'))

    import tempfile, io, os
    from PIL import Image as PILImage
    from datetime import datetime
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    import locale

    data = session['prediksi']

    # Load model dan akurasi
    with open("models/decision_tree.pkl", "rb") as f:
        clf, encoders, accuracy = pickle.load(f)  # ✅ Ambil akurasi dari model

    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    elements = []

    # === Header ===
    def header(canvas, doc):
        canvas.saveState()
        logo_path = "app/static/logo_app.jpg"
        pil_logo = PILImage.open(logo_path).resize((80, 80))
        logo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        pil_logo.save(logo_temp.name)
        canvas.drawImage(logo_temp.name, 40, A4[1] - 100, width=60, height=60)

        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(110, A4[1] - 40, "PT. NEOTRISTAR PRIMAJAYA")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(110, A4[1] - 55, "Komplek Karang Anyar Permai 55")
        canvas.drawString(110, A4[1] - 70, "Jl. Karang Anyar No.55 Blok A1 No.9 Jakarta 10740")
        canvas.drawString(110, A4[1] - 85, "Telp. (021) 659 1990 - 659 1991 - 628 0462   Fax. (021) 600 6213")
        canvas.drawString(110, A4[1] - 100, "Email: neotristar@yahoo.com")
        canvas.setLineWidth(1)
        canvas.line(40, A4[1] - 110, A4[0] - 40, A4[1] - 110)
        canvas.restoreState()

    # === Konten utama ===
    elements.append(Spacer(1, 50))
    centered_title = Paragraph(
        "<b><u>Laporan Hasil Prediksi Sparepart</u></b>",
        ParagraphStyle('centered', parent=styles['Heading2'], alignment=1)
    )
    elements.append(centered_title)
    elements.append(Paragraph("<i>Data dibawah merupakan hasil prediksi berdasarkan model klasifikasi</i>", styles['Normal']))
    elements.append(Spacer(1, 18))

    isi = [
        ["Stok", data['Stok']],
        ["Jumlah Terjual", data['Jumlah']],
        ["Harga", data['Harga']],
        ["Kategori Sparepart", data['Kategori']],
        ["Hasil Prediksi", data['hasil'].capitalize()],
        ["Skor Akurasi Model", f"{accuracy:.2%}"]  # ✅ Akurasi langsung dari model
    ]

    table = Table(isi, colWidths=[6 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')  # ✅ Rata kiri seluruh isi
    ]))

    elements.append(table)

    # === Signature block (di akhir halaman) ===
    elements.append(Spacer(1, 95))
    locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")  # Linux/macOS
    # locale.setlocale(locale.LC_TIME, "ind")  # Untuk Windows jika perlu

    tanggal = datetime.now().strftime("Jakarta, %A %d %B %Y")
    signature_text = f"""
    <para align=right>
    {tanggal}<br/><br/>
    <b>PT Neotristar Primajaya</b><br/><br/><br/><br/><br/><br/>
    <u>Junus Chandra</u><br/>
    <b>Direktur</b>
    </para>
    """
    elements.append(Paragraph(signature_text, styles['Normal']))

    # === Generate PDF ===
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    doc.build(elements, onFirstPage=header)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=False,
        download_name="hasil_prediksi.pdf",
        mimetype='application/pdf'
    )

    
@main.route('/data-sparepart')
def data_sparepart():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    df = pd.read_csv("app/penjualan_clean_updated.csv")
    return render_template("data_sparepart.html", user=session['user'], data=df.to_dict(orient='records'))

@main.route('/visualisasi')
def visualisasi():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    with open("models/decision_tree.pkl", "rb") as f:
        clf, encoders = pickle.load(f)

    df = pd.read_csv("app/penjualan_clean_updated.csv")

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    fitur = ['Stok', 'Jumlah', 'Harga', 'Kategori']
    plot_tree(clf, feature_names=fitur, class_names=encoders['Klasifikasi'].classes_, filled=True, ax=ax1)
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    tree_url = base64.b64encode(buf1.getvalue()).decode()

    fig2, ax2 = plt.subplots()
    df['Klasifikasi'].value_counts().plot(kind='bar', color='skyblue', ax=ax2)
    ax2.set_title("Distribusi Kelarisan Sparepart")
    ax2.set_ylabel("Jumlah Data")
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    distribusi_url = base64.b64encode(buf2.getvalue()).decode()

    return render_template("visualisasi.html", tree_img=tree_url, distribusi_img=distribusi_url)

@main.route('/report')
def report():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    df = pd.read_csv("app/penjualan_clean_updated.csv")
    return render_template("report.html", data=df.to_dict(orient='records'), now=datetime.now())

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import io, tempfile

@main.route('/cetak-report', methods=['POST'])
def cetak_report():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    import tempfile, io, os
    from datetime import datetime
    import matplotlib.pyplot as plt
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, Image as RLImage
    )
    from reportlab.lib.utils import ImageReader
    from PIL import Image as PILImage

    pilihan = request.form['pilihan_report']
    df = pd.read_csv("app/penjualan_clean_updated.csv")
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    elements = []

    # ==== HEADER ====
    def header(canvas, doc):
        canvas.saveState()
        logo_path = "app/static/logo_app.jpg"
        pil_logo = PILImage.open(logo_path).resize((80, 80))
        logo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        pil_logo.save(logo_temp.name)
        canvas.drawImage(logo_temp.name, 40, A4[1] - 100, width=60, height=60)

        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(110, A4[1] - 40, "PT. NEOTRISTAR PRIMAJAYA")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(110, A4[1] - 55, "Komplek Karang Anyar Permai 55")
        canvas.drawString(110, A4[1] - 70, "Jl. Karang Anyar No.55 Blok A1 No.9 Jakarta 10740")
        canvas.drawString(110, A4[1] - 85, "Telp. (021) 659 1990 - 659 1991 - 628 0462   Fax. (021) 600 6213")
        canvas.drawString(110, A4[1] - 100, "Email: neotristar@yahoo.com")
        canvas.setLineWidth(1)
        canvas.line(40, A4[1] - 110, A4[0] - 40, A4[1] - 110)
        canvas.restoreState()

    show_chart = False

    if pilihan == "keseluruhan":
        judul = "Laporan Data Keseluruhan"
        kolom = ["No", "Sparepart", "Stok", "Jumlah", "Harga", "Kategori"]
        data_rows = df[["Sparepart", "Stok", "Jumlah", "Harga", "Kategori"]].values.tolist()

    elif pilihan == "klasifikasi":
        judul = "Laporan Data Setelah Diklasifikasi"
        kolom = ["No", "Sparepart", "Stok", "Jumlah", "Harga", "Kategori", "Klasifikasi"]
        data_rows = df[["Sparepart", "Stok", "Jumlah", "Harga", "Kategori", "Klasifikasi"]].values.tolist()

    elif pilihan == "laris":
        judul = "Laporan Data Sparepart Klasifikasi Laris"
        kolom = ["No", "Sparepart", "Stok", "Jumlah", "Harga", "Kategori", "Klasifikasi"]
        df = df[df['Klasifikasi'].str.lower() == 'laris']
        data_rows = df[["Sparepart", "Stok", "Jumlah", "Harga", "Kategori", "Klasifikasi"]].values.tolist()

    elif pilihan == "tidak_laris":
        judul = "Laporan Data Sparepart Klasifikasi Tidak Laris"
        kolom = ["No", "Sparepart", "Stok", "Jumlah", "Harga", "Kategori", "Klasifikasi"]
        df = df[df['Klasifikasi'].str.lower() == 'tidak laris']
        data_rows = df[["Sparepart", "Stok", "Jumlah", "Harga", "Kategori", "Klasifikasi"]].values.tolist()

    elif pilihan == "visualisasi":
        show_chart = True
        judul = "Laporan Visualisasi Klasifikasi Sparepart"
        klasifikasi_counts = df["Klasifikasi"].value_counts().to_dict()
        df_vis = pd.DataFrame({
            "Klasifikasi": list(klasifikasi_counts.keys()),
            "Jumlah": list(klasifikasi_counts.values())
        })
        kolom = ["Klasifikasi", "Jumlah"]
        data_rows = df_vis.values.tolist()
    else:
        return "Pilihan tidak valid", 400

    elements.append(Spacer(1, 90))
    elements.append(Paragraph(f"<u><b>{judul}</b></u>", ParagraphStyle(name='Heading2Center', alignment=1, fontSize=14)))
    elements.append(Spacer(1, 16))

    # ==== TABEL ====
    if not show_chart:
        # Penambahan nomor dan pembungkus Sparepart
        table_data = [kolom]
        for i, row in enumerate(data_rows, start=1):
            row_data = [i]
            for j, cell in enumerate(row):
                if kolom[j + 1] == "Sparepart":
                    p = Paragraph(
                        str(cell),
                        ParagraphStyle(name="sparepart_style", fontSize=9, leading=12, alignment=0)
                    )
                    row_data.append(p)
                else:
                    row_data.append(str(cell))
            table_data.append(row_data)

        col_widths = [2.0*cm, 6.0*cm]  # No + Sparepart
        col_count = len(kolom)
        sisa_width = A4[0] - 80 - sum(col_widths)
        for _ in range(col_count - 2):
            col_widths.append(sisa_width / (col_count - 2))

        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#afb1b4")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # ✅ Hanya baris header (baris ke-0) yang rata tengah:
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # ❗ Data mulai dari baris ke-1:
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # No
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Sparepart
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Sisanya

            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ]))
        elements.append(table)

    else:
        elements.append(Paragraph("📊 Grafik Distribusi Klasifikasi Sparepart", styles['Heading3']))
        elements.append(Spacer(1, 10))
        plt.figure(figsize=(6, 4))
        df_vis.set_index("Klasifikasi")["Jumlah"].plot(kind="bar", color="#3498db")
        plt.ylabel("Jumlah")
        plt.xlabel("Klasifikasi")
        plt.title("Distribusi Kelarisan Sparepart")
        plt.tight_layout()

        chart_buf = io.BytesIO()
        plt.savefig(chart_buf, format='png')
        chart_buf.seek(0)
        plt.close()
        img = RLImage(chart_buf, width=400, height=300)
        elements.append(img)

    # ==== SIGNATURE ====
    elements.append(Spacer(1, 80))
    import locale
    locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")

    tanggal = datetime.now().strftime("Jakarta, %A %d %B %Y")
    signature_text = f"""
    <para align=right>
    {tanggal}<br/><br/>
    <b>PT Neotristar Primajaya</b><br/><br/><br/><br/><br/><br/>
    <u>Junus Chandra</u><br/>
    <b>Direktur</b>
    </para>
    """
    elements.append(Paragraph(signature_text, styles['Normal']))

    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    doc.build(elements, onFirstPage=header)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=False,
        download_name="laporan_sparepart.pdf",
        mimetype='application/pdf'
    )
