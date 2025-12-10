# ⚙️ Proyek flask_sparepart
Deskripsi Proyek
flask_sparepart adalah sebuah aplikasi web manajemen inventaris suku cadang (sparepart) yang dikembangkan menggunakan framework Flask dengan bahasa pemrograman Python. Proyek ini dirancang untuk memudahkan pencatatan, pemantauan, dan pengelolaan stok suku cadang, menjadikannya solusi ideal untuk bisnis atau gudang kecil hingga menengah.
Aplikasi ini menggunakan basis data MySQL atau PostgreSQL (tergantung konfigurasi deployment) untuk menyimpan data, serta menerapkan arsitektur modular dan best practices pengembangan web.
🚀 Fitur Utama
Autentikasi Pengguna: Sistem login dan logout yang aman.
Manajemen Inventaris:
Menambahkan suku cadang baru.
Melihat detail dan daftar semua suku cadang.
Mengedit informasi suku cadang yang sudah ada.
Menghapus suku cadang dari stok.
Pencatatan Stok: Pelacakan jumlah stok masuk dan keluar.
Pencarian & Filter: Fungsi pencarian data yang cepat dan kemampuan untuk memfilter daftar suku cadang berdasarkan kategori atau kriteria lain.
Antarmuka Responsif: Desain antarmuka yang nyaman diakses dari berbagai perangkat (desktop dan mobile).
🛠️ Teknologi yang Digunakan
Kategori
Teknologi
Deskripsi
Backend
Python
Bahasa pemrograman utama.
Web Framework
Flask
Micro-framework Python yang ringan.
Database
SQLAlchemy / MySQL / PostgreSQL
Digunakan sebagai ORM dan sistem manajemen basis data.
Frontend
HTML5, CSS3, JavaScript
Dasar-dasar antarmuka pengguna.
Styling
Bootstrap (atau sejenisnya)
Framework CSS untuk desain responsif.

⬇️ Instalasi dan Konfigurasi Lokal
Ikuti langkah-langkah berikut untuk menjalankan proyek ini di lingkungan lokal Anda.
Prasyarat
Pastikan Anda telah menginstal:
Python 3.x
pip (Pengelola paket Python)
Basis Data (MySQL atau PostgreSQL) dan kredensial akses yang valid.
Langkah-langkah
Kloning Repositori:
Bash
git clone https://github.com/fajarfaps/flask_sparepart.git
cd flask_sparepart


Buat dan Aktifkan Virtual Environment:
Linux/macOS:
Bash
python3 -m venv venv
source venv/bin/activate


Windows:
Bash
python -m venv venv
venv\Scripts\activate


Instal Dependensi:
Bash
pip install -r requirements.txt


Konfigurasi Variabel Lingkungan:
Buat file .env di direktori utama dan isi dengan konfigurasi database Anda. (Contoh: DATABASE_URL = "mysql+pymysql://user:password@host/dbname")
Pastikan Anda juga telah membuat skema basis data.
Migrasi Basis Data (jika menggunakan Flask-Migrate):
Bash
flask db upgrade

(Jika proyek Anda tidak menggunakan Flask-Migrate, buat skema basis data secara manual sesuai kebutuhan aplikasi).
Jalankan Aplikasi:
Bash
flask run

Aplikasi akan tersedia di http://127.0.0.1:5000/
🤝 Kontribusi
Kami sangat menyambut kontribusi dari Anda! Untuk berkontribusi, silakan ikuti alur Git Flow standar:
Fork repositori ini.
Buat branch baru untuk fitur atau perbaikan Anda (git checkout -b feature/nama-fitur-anda).
Lakukan commit perubahan Anda (git commit -m 'feat: Tambahkan fitur baru X').
Push ke branch Anda (git push origin feature/nama-fitur-anda).
Buat Pull Request (PR) baru ke branch main repositori ini.
📄 Lisensi
Proyek ini dilisensikan di bawah Lisensi MIT. Lihat berkas LICENSE untuk detail selengkapnya.
📧 Kontak
Jika Anda memiliki pertanyaan atau masukan, silakan hubungi pengelola proyek:
Fajar Faps
GitHub: fajarfaps
