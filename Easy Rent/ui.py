import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date, timedelta
from config import RENKLER
from database import verileri_yukle, verileri_kaydet, gecmis_kaydet
import os
import json
import re

def plaka_gecerli_mi(plaka):
    regex = r'^(0[1-9]|[1-7][0-9]|8[0-1])[A-Z]{2,3}\d{2,3}$'
    return re.fullmatch(regex, plaka) is not None

class EasyRentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyRent")
        self.mevcut_kullanici = None
        self.rol = None
        self.araclar = verileri_yukle()
        self.sadece_musait_goster = tk.BooleanVar()
        self.sadece_musait_goster.set(False)
        self.stil_ayarla()
        self.giris_ekrani()
        self.sadece_kirada_goster = tk.BooleanVar()
        self.sadece_kirada_goster.set(False)

    def stil_ayarla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background=RENKLER["secondary"], foreground="white", font=("Segoe UI", 10, "bold"), relief="flat")
        style.configure("Treeview", background="white", fieldbackground="white", rowheight=35, font=("Segoe UI", 10))
        style.map("Treeview", background=[('selected', RENKLER["primary"])])

    def center_window(self, w, h):
        self.root.geometry(f"{w}x{h}")
        self.root.update_idletasks()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry(f'+{int(x)}+{int(y)}')

    def temizle(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pencere_ac(self, baslik, h=400):
        top = tk.Toplevel(self.root)
        top.title(baslik)
        w = 350
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        top.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
        top.configure(bg="white")
        return top

    def giris_ekrani(self):
        self.temizle()
        self.center_window(350, 320)
        self.root.configure(bg=RENKLER["bg"])
        main_frame = tk.Frame(self.root, bg="white", padx=20, pady=20, relief="raised", bd=1)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=280)
        tk.Label(main_frame, text="EasyRent", font=("Segoe UI", 18, "bold"), bg="white", fg=RENKLER["primary"]).pack(pady=(10, 20))
        tk.Label(main_frame, text="Kullanıcı Adı", font=("Segoe UI", 9, "bold"), bg="white", fg=RENKLER["text_dark"], anchor="w").pack(fill="x")
        self.ent_isim = ttk.Entry(main_frame, font=("Segoe UI", 11))
        self.ent_isim.pack(fill="x", pady=(5, 20))
        tk.Button(main_frame, text="Giriş Yap", bg=RENKLER["success"], fg="white", font=("Segoe UI", 10, "bold"), relief="flat", pady=8, command=lambda: self.login("user")).pack(fill="x", pady=5)
        tk.Button(main_frame, text="Admin Paneli", bg=RENKLER["secondary"], fg="white", font=("Segoe UI", 9), relief="flat", pady=5, command=self.admin_giris).pack(fill="x", pady=5)

    def login(self, rol):
        ham_isim = self.ent_isim.get().strip()
        if not ham_isim:
            messagebox.showwarning("Uyarı", "Lütfen isminizi giriniz.")
            return
        self.mevcut_kullanici = ham_isim.title()
        self.rol = rol
        self.araclar = verileri_yukle()
        self.sadece_musait_goster.set(False)
        self.ana_panel()

    def admin_giris(self):
        ham_isim = self.ent_isim.get().strip()
        if not ham_isim:
            messagebox.showwarning("Uyarı", "Lütfen isminizi giriniz.")
            return

        # Şifre sor
        def sifre_kontrol(top, ent_sifre):
            sifre = ent_sifre.get().strip()
            ORTAK_ADMIN_SIFRE = "1234"  # tüm adminler için ortak şifre
            if sifre == ORTAK_ADMIN_SIFRE:
                self.mevcut_kullanici = ham_isim.title()
                self.rol = "admin"
                self.araclar = verileri_yukle()
                self.sadece_musait_goster.set(False)
                top.destroy()
                self.ana_panel()
            else:
                messagebox.showerror("Hata", "Şifre yanlış!")

        top = tk.Toplevel(self.root)
        top.title("Admin Girişi")
        top.geometry("300x150")
        tk.Label(top, text="Admin Şifre", font=("Segoe UI", 10, "bold")).pack(pady=10)
        ent_sifre = tk.Entry(top, show="*", font=("Segoe UI", 11))
        ent_sifre.pack(pady=5)
        tk.Button(top, text="Giriş", bg=RENKLER["success"], fg="white", command=lambda: sifre_kontrol(top, ent_sifre)).pack(pady=10)

    def ana_panel(self):
        self.temizle()
        self.center_window(1150, 650)
        self.root.configure(bg=RENKLER["bg"])
        sidebar = tk.Frame(self.root, bg=RENKLER["secondary"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="EasyRent", bg=RENKLER["secondary"], fg="white", font=("Segoe UI", 22, "bold")).pack(pady=40)
        tk.Label(sidebar, text=f"Hoş geldin,\n{self.mevcut_kullanici}", bg=RENKLER["secondary"], fg="#BDC3C7", font=("Segoe UI", 11)).pack(pady=(0, 30))

        def menu_btn(text, cmd, bg_color=RENKLER["primary"]):
            tk.Button(sidebar, text=text, bg=bg_color, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", anchor="center", justify="center", padx=0, pady=12, command=cmd).pack(fill="x", pady=2)

        if self.rol == "admin":
            menu_btn("Araç Ekle", self.arac_ekle_penceresi)
            menu_btn("Düzenle", self.arac_duzenle_penceresi, RENKLER["warning"])
            menu_btn("Araç Sil", self.arac_sil, "#D35400")
            menu_btn("İade Al", self.admin_iade_al, "#16A085")
            menu_btn("Günlük Rapor", self.gunluk_rapor, "#8E44AD")
            menu_btn("Kiralama Geçmişi", self.kiralama_gecmisi_penceresi, "#8E44AD")
        else:
            menu_btn("Araç Kirala", self.kira_baslat_penceresi, RENKLER["success"])
            menu_btn("İade Et", self.kullanici_iade_penceresi, "#C0392B")

        tk.Button(sidebar, text="Çıkış Yap", bg=RENKLER["danger"], fg="white", font=("Segoe UI", 10, "bold"), relief="flat", command=self.cikis_yap).pack(side="bottom", fill="x", pady=20, padx=20)
        content = tk.Frame(self.root, bg=RENKLER["bg"])
        content.pack(side="right", fill="both", expand=True, padx=25, pady=25)
        self.istatistik_paneli(content)
        header_frame = tk.Frame(content, bg=RENKLER["bg"])
        header_frame.pack(fill="x", pady=(20, 10))
        tk.Label(header_frame, text="Araç Listesi", font=("Segoe UI", 14, "bold"), bg=RENKLER["bg"], fg=RENKLER["text_dark"]).pack(side="left")
        # Sadece admin için kirada filtre checkbox
        if self.rol == "admin":
            filter_chk_admin = tk.Checkbutton(header_frame, text="Sadece Kirada Olanları Göster", variable=self.sadece_kirada_goster, bg=RENKLER["bg"], font=("Segoe UI", 10), command=self.liste_guncelle)
            filter_chk_admin.pack(side="right")
        # Kullanıcı için mevcut filtre
        if self.rol != "admin":
             filter_chk = tk.Checkbutton(header_frame, text="Sadece Müsait Olanları Göster", variable=self.sadece_musait_goster, bg=RENKLER["bg"], font=("Segoe UI", 10), command=self.liste_guncelle)
             filter_chk.pack(side="right")
        table_frame = tk.Frame(content, bg="white", bd=0, relief="flat")
        table_frame.pack(fill="both", expand=True)
        self.cols = ["plaka", "marka", "model", "ucret", "durum", "baslangic", "bitis"]
        self.headers = [
            ("plaka", "Plaka", 100),
            ("marka", "Marka", 120),
            ("model", "Model", 120),
            ("ucret", "Günlük (TL)", 100),
            ("durum", "Durum", 100),
            ("baslangic", "Başlangıç Tarihi", 120),
            ("bitis", "Bitiş Tarihi", 120)
        ]
        if self.rol == "admin":
            self.cols.append("kiralayan")
            self.headers.append(("kiralayan", "Kiralayan Müşteri", 150))
        self.cols.append("tarih")
        self.headers.append(("tarih", "Dönüş Tarihi", 120))
        self.tree = ttk.Treeview(table_frame, columns=self.cols, show="headings")
        for col_id, text, width in self.headers:
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor="center")
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.liste_guncelle()

    def istatistik_paneli(self, parent):
        stats_frame = tk.Frame(parent, bg=RENKLER["bg"])
        stats_frame.pack(fill="x")
        toplam = len(self.araclar)
        musaits = len([a for a in self.araclar if a["durum"] == "müsait"])
        self.kart_olustur(stats_frame, "TOPLAM ARAÇ", str(toplam), RENKLER["secondary"], 0)
        self.kart_olustur(stats_frame, "MÜSAİT", str(musaits), RENKLER["success"], 1)
        self.kart_olustur(stats_frame, "KİRADA", str(toplam - musaits), RENKLER["danger"], 2)

    def kart_olustur(self, parent, title, value, color, col):
        card = tk.Frame(parent, bg="white", padx=20, pady=15, relief="flat")
        card.grid(row=0, column=col, padx=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Frame(card, bg=color, width=5).pack(side="left", fill="y", padx=(0, 10))
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg=RENKLER["text_grey"], bg="white").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), fg=color, bg="white").pack(anchor="w")

    def liste_guncelle(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for arac in self.araclar:
            # Admin filtre
            if self.rol == "admin" and self.sadece_kirada_goster.get() and arac["durum"] != "kirada":
                continue
            # Kullanıcı filtre
            if self.rol != "admin" and self.sadece_musait_goster.get() and arac["durum"] != "müsait":
                continue
            if arac["durum"] == "müsait":
                durum_text = "MÜSAİT"
                tag = "musait"
            elif arac["durum"] == "kirada":
                durum_text = "KİRADA"
                tag = "kirada"
            elif arac["durum"] == "bakımda":
                durum_text = "BAKIMDA"
                tag = "bakim"
            self.tree.tag_configure("bakim", foreground="#7F8C8D", font=("Segoe UI", 10, "italic"))
            row_values = [
                arac["plaka"],
                arac["marka"].title(),
                arac["model"].title(),
                f"{arac['ucret']} ₺",
                durum_text,
                arac.get("baslangic_tarihi") or "-",
                arac.get("bitis_tarihi") or "-"
            ]
            if self.rol == "admin":
                kiralayan_kisi = arac.get("kiralayan", "")
                if arac["durum"] == "kirada" and not kiralayan_kisi:
                    kiralayan_kisi = "Bilinmiyor"
                elif arac["durum"] == "müsait":
                    kiralayan_kisi = "-"
                row_values.append(kiralayan_kisi)
            row_values.append(arac.get("bitis_tarihi") or "-")
            self.tree.insert("", "end", values=tuple(row_values), tags=(tag,))
        self.tree.tag_configure("musait", foreground=RENKLER["success"], font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure("kirada", foreground=RENKLER["danger"], font=("Segoe UI", 10, "bold"))

    def cikis_yap(self):
        if messagebox.askyesno("Çıkış", "Oturumu kapatmak istiyor musunuz?"):
            self.mevcut_kullanici = None
            self.rol = None
            self.giris_ekrani()

    def kullanici_iade_penceresi(self):
        benim_araclar = [a for a in self.araclar if a.get("kiralayan") == self.mevcut_kullanici]
        if not benim_araclar:
            messagebox.showinfo("Bilgi", "İade edilecek aktif bir kiralamanız bulunmamaktadır.")
            return
        p = self.pencere_ac("İade İşlemi", 400)
        p.geometry("600x450")
        tk.Label(p, text="İade Etmek İstediğiniz Aracı Seçin", font=("Segoe UI", 12, "bold"), bg="white", fg=RENKLER["danger"]).pack(pady=10)
        btn_frame = tk.Frame(p, bg="white", pady=10)
        btn_frame.pack(side="bottom", fill="x")
        list_frame = tk.Frame(p, bg="white")
        list_frame.pack(side="top", fill="both", expand=True, padx=20)
        cols = ("plaka", "marka", "model", "tarih", "ucret")
        tree_sub = ttk.Treeview(list_frame, columns=cols, show="headings")
        tree_sub.heading("plaka", text="Plaka")
        tree_sub.heading("marka", text="Marka")
        tree_sub.heading("model", text="Model")
        tree_sub.heading("tarih", text="Dönüş Tarihi")
        tree_sub.heading("ucret", text="Ücret")
        tree_sub.column("plaka", width=90, anchor="center")
        tree_sub.column("marka", width=100, anchor="center")
        tree_sub.column("model", width=100, anchor="center")
        tree_sub.column("tarih", width=100, anchor="center")
        tree_sub.column("ucret", width=80, anchor="center")
        tree_sub.pack(fill="both", expand=True)
        for arac in benim_araclar:
            tree_sub.insert("", "end", values=(arac["plaka"], arac["marka"].title(), arac["model"].title(), arac["bitis_tarihi"], f"{arac['ucret']} ₺"))
        def iade_et():
            secili = tree_sub.selection()
            if not secili: 
                messagebox.showwarning("Seçim", "Lütfen listeden bir araç seçin.")
                return
            plaka = tree_sub.item(secili)["values"][0]
            arac = next(a for a in self.araclar if a["plaka"] == plaka)
            if messagebox.askyesno("İade Onayı", f"{plaka} plakalı aracı iade ediyor musunuz?"):
                gecmis_kaydet({
                    "plaka": arac["plaka"],
                    "musteri": arac["kiralayan"],
                    "baslangic": arac["baslangic_tarihi"],
                    "bitis": date.today().isoformat()
                })
                arac.update({"durum": "müsait", "kiralayan": "", "baslangic_tarihi": "", "bitis_tarihi": ""})
                verileri_kaydet(self.araclar)
                self.ana_panel() 
                p.destroy()      
                messagebox.showinfo("Başarılı", "İade işleminiz başarıyla tamamlandı.")
        tk.Button(btn_frame, text="SEÇİLİ ARACI TESLİM ET", bg=RENKLER["danger"], fg="white", font=("Segoe UI", 10, "bold"), pady=10, relief="flat", command=iade_et).pack(fill="x", padx=20)

    def admin_iade_al(self):
        secili = self.tree.selection()
        if not secili: return messagebox.showwarning("Uyarı", "Ana listeden iade alınacak aracı seçin.")
        plaka = self.tree.item(secili)["values"][0]
        self.araclar = verileri_yukle()
        arac = next((a for a in self.araclar if a["plaka"] == plaka), None)
        if arac["durum"] == "müsait":
            return messagebox.showerror("Hata", "Bu araç zaten müsait.")
        if messagebox.askyesno("İade Onayı", f"{plaka} plakalı araç teslim alınsın mı?"):
            gecmis_kaydet({
                "plaka": arac["plaka"],
                "musteri": arac["kiralayan"],
                "baslangic": arac["baslangic_tarihi"],
                "bitis": date.today().isoformat(),
                "admin_iade": True
            })
            arac.update({"durum": "müsait", "kiralayan": "", "baslangic_tarihi": "", "bitis_tarihi": ""})
            verileri_kaydet(self.araclar)
            self.ana_panel()
            messagebox.showinfo("Başarılı", "Araç teslim alındı.")

    def arac_ekle_penceresi(self):
        p = self.pencere_ac("Araç Ekle", 420)
        entries = {}
        labels = ["Plaka", "Marka", "Model", "Günlük Ücret"]
        for text in labels:
            tk.Label(p, text=text, bg="white", font=("Segoe UI", 9, "bold")).pack(pady=(10,0))
            e = tk.Entry(p, font=("Segoe UI", 11), bd=1, relief="solid")
            e.pack(pady=5, padx=20, fill="x")
            entries[text] = e
        def kaydet():
            try:
                veriler = {k: v.get().strip() for k, v in entries.items()}
                if not all(veriler.values()):
                    return messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurunuz.")
                plaka = veriler["Plaka"].upper().replace(" ", "")
                if not plaka_gecerli_mi(plaka):
                    return messagebox.showerror(
                        "Hatalı Plaka",
                        "Plaka formatı geçersiz.\nLütfen standartlara uygun bir plaka girişi gerçekleştiriniz."
                    )
                try:
                    ucret = float(veriler["Günlük Ücret"])
                except ValueError:
                    return messagebox.showerror("Format Hatası", "Ücret sayı olmalıdır.")
                if any(a['plaka'] == veriler["Plaka"].upper() for a in self.araclar):
                    return messagebox.showerror("Hata", "Bu plaka zaten kayıtlı.")
                self.araclar.append({
                    "plaka": plaka,
                    "marka": veriler["Marka"],
                    "model": veriler["Model"],
                    "ucret": ucret,
                    "durum": "müsait",
                    "kiralayan": "",
                    "baslangic_tarihi": "",
                    "bitis_tarihi": ""
                })
                verileri_kaydet(self.araclar)
                self.ana_panel()
                messagebox.showinfo("Başarılı", "Eklendi.")
                p.destroy()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(p, text="KAYDET", bg=RENKLER["primary"], fg="white", font=("Segoe UI", 10, "bold"), pady=10, command=kaydet, relief="flat").pack(fill="x", padx=20, pady=20)

    def arac_duzenle_penceresi(self):
        secili = self.tree.selection()
        if not secili: return messagebox.showwarning("Seçim", "Araç seçiniz.")
        plaka = self.tree.item(secili)["values"][0]
        arac = next(a for a in self.araclar if a["plaka"] == plaka)
        p = self.pencere_ac("Araç Düzenle", 420)
        tk.Label(p, text=f"PLAKA: {arac['plaka']}", bg="white", fg=RENKLER["primary"], font=("Segoe UI", 12, "bold")).pack(pady=15)
        entries = {}
        fields = [("Marka", arac["marka"]), ("Model", arac["model"]), ("Günlük Ücret", arac["ucret"]), ("Durum", arac["durum"])]
        for lbl, val in fields:
            tk.Label(p, text=lbl, bg="white", font=("Segoe UI", 9, "bold")).pack(pady=(5,0))
            e = tk.Entry(p, font=("Segoe UI", 11), bd=1, relief="solid")
            e.insert(0, str(val))
            e.pack(pady=5, padx=20, fill="x")
            entries[lbl] = e
        def guncelle():
            try:
                yeni_ucret = float(entries["Günlük Ücret"].get())
                yeni_durum = entries["Durum"].get().lower()
                if yeni_durum == "kirada":
                    self.admin_kiralama_penceresi(arac)
                    p.destroy()
                    return
                if yeni_durum not in ["müsait", "kirada", "bakımda"]:
                    return messagebox.showerror(
                        "Hata",
                        "Durum sadece: müsait / kirada / bakımda olabilir"
                    )

                arac.update({
                    "marka": entries["Marka"].get(),
                    "model": entries["Model"].get(),
                    "ucret": yeni_ucret,
                    "durum": yeni_durum
                })
                verileri_kaydet(self.araclar)
                self.ana_panel()
                messagebox.showinfo("Başarılı", "Güncellendi.")
                p.destroy()
            except ValueError:
                messagebox.showerror("Hata", "Ücret sayı olmalıdır.")
        tk.Button(p, text="GÜNCELLE", bg=RENKLER["warning"], fg="white", font=("Segoe UI", 10, "bold"), pady=10, command=guncelle, relief="flat").pack(fill="x", padx=20, pady=20)

    def arac_sil(self):
        secili = self.tree.selection()
        if not secili: return messagebox.showwarning("Seçim", "Araç seçiniz.")
        plaka = self.tree.item(secili)["values"][0]
        if messagebox.askyesno("Sil", f"{plaka} silinsin mi?"):
            self.araclar = [a for a in self.araclar if a["plaka"] != plaka]
            verileri_kaydet(self.araclar)
            self.ana_panel()

    def kira_baslat_penceresi(self):
        secili = self.tree.selection()
        if not secili: return messagebox.showwarning("Uyarı", "Kiralanacak aracı seçiniz.")
        plaka = self.tree.item(secili)["values"][0]
        arac = next(a for a in self.araclar if a["plaka"] == plaka)
        if arac["durum"] == "bakımda":
            return messagebox.showerror("Hata", "Bu araç bakımda, kiralanamaz.")
        if arac["durum"] != "müsait":
            return messagebox.showerror("Hata", "Araç müsait değil.")
        p = self.pencere_ac("Kirala", 350)
        tk.Label(p, text=f"{arac['marka']} {arac['model']}", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=10)
        # Başlangıç tarihi
        tk.Label(p, text="Başlangıç Tarihi (YYYY-AA-GG):", bg="white").pack(pady=(10, 0))
        ent_baslangic = tk.Entry(p, font=("Segoe UI", 11), justify="center")
        ent_baslangic.insert(0, date.today().strftime("%Y-%m-%d"))
        ent_baslangic.pack(pady=5)

        # Bitiş tarihi
        tk.Label(p, text="Bitiş Tarihi (YYYY-AA-GG):", bg="white").pack(pady=(10, 0))
        ent_bitis = tk.Entry(p, font=("Segoe UI", 11), justify="center")
        ent_bitis.insert(0, (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"))
        ent_bitis.pack(pady=5)

        def onayla():
            try:
                baslangic = datetime.strptime(ent_baslangic.get(), "%Y-%m-%d").date()
                bitis = datetime.strptime(ent_bitis.get(), "%Y-%m-%d").date()
                bugun = date.today()

                if baslangic < bugun:
                    return messagebox.showerror("Hata", "Başlangıç tarihi bugünden önce olamaz.")
                if bitis <= baslangic:
                    return messagebox.showerror("Hata", "Bitiş tarihi başlangıç tarihinden önce olamaz.")

                gun = (bitis - baslangic).days
                tutar = gun * arac["ucret"]

                if messagebox.askyesno("Onay", f"Tutar: {tutar} TL\nOnaylıyor musunuz?"):
                    arac.update({
                        "durum": "kirada",
                        "kiralayan": self.mevcut_kullanici,
                        "baslangic_tarihi": str(baslangic),
                        "bitis_tarihi": str(bitis)
                    })
                    verileri_kaydet(self.araclar)
                    self.ana_panel()
                    messagebox.showinfo("Başarılı", "Kiralama yapıldı.")
                    p.destroy()
            except ValueError:
                messagebox.showerror("Hata", "Tarih formatı hatalı.")
        tk.Button(p, text="KİRALA VE ÖDE", bg=RENKLER["success"], fg="white", font=("Segoe UI", 10, "bold"), pady=10, command=onayla, relief="flat").pack(fill="x", padx=20, pady=20)

    def gunluk_rapor(self):
        # Araçların kiralama geçmişini alıyoruz
        tarihler = {}
        for arac in self.araclar:
            if arac.get("baslangic_tarihi") and arac.get("bitis_tarihi"):
                baslangic = date.fromisoformat(arac["baslangic_tarihi"])
                bitis = date.fromisoformat(arac["bitis_tarihi"])
                gun_sayisi = (bitis - baslangic).days
                for i in range(gun_sayisi):
                    gun = (baslangic + timedelta(days=i)).isoformat()
                    if gun not in tarihler:
                        tarihler[gun] = {"kiralama": 0, "gelir": 0}
                    tarihler[gun]["kiralama"] += 1
                    tarihler[gun]["gelir"] += arac["ucret"]

        # Pencere aç
        p = tk.Toplevel(self.root)
        p.title("Günlük Kiralama Raporu")
        p.geometry("600x400")

        tree = ttk.Treeview(p, columns=("tarih", "kiralama", "gelir"), show="headings")
        tree.heading("tarih", text="Tarih")
        tree.heading("kiralama", text="Kiralanan Araç")
        tree.heading("gelir", text="Toplam Gelir (TL)")
        tree.column("tarih", width=120, anchor="center")
        tree.column("kiralama", width=150, anchor="center")
        tree.column("gelir", width=150, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        if not tarihler:
            messagebox.showinfo("Bilgi", "Henüz kiralama yok.")
            return

        for gun, veri in sorted(tarihler.items()):
            tree.insert("", "end", values=(gun, veri["kiralama"], veri["gelir"]))

    def admin_kiralama_penceresi(self, arac):
        p = self.pencere_ac("Admin Kiralama", 350)

        tk.Label(p, text="Müşteri Adı", bg="white").pack(pady=5)
        ent_musteri = tk.Entry(p)
        ent_musteri.pack(pady=5)

        tk.Label(p, text="Bitiş Tarihi (YYYY-AA-GG)", bg="white").pack(pady=5)
        ent_tarih = tk.Entry(p)
        ent_tarih.pack(pady=5)

        def kaydet():
            try:
                musteri = ent_musteri.get().strip()
                bitis = datetime.strptime(ent_tarih.get(), "%Y-%m-%d").date()
                baslangic = date.today()
                if bitis <= baslangic:
                    return messagebox.showerror("Hata", "Bitiş tarihi bugünden önce olamaz.")
                if not musteri:
                    return messagebox.showerror("Hata", "Müşteri adı giriniz.")

                arac.update({
                    "durum": "kirada",
                    "kiralayan": musteri.title(),
                    "baslangic_tarihi": str(date.today()),
                    "bitis_tarihi": str(bitis)
                })
                verileri_kaydet(self.araclar)
                self.ana_panel()
                p.destroy()
            except:
                messagebox.showerror("Hata", "Bilgiler hatalı.")

        tk.Button(p, text="KAYDET", bg=RENKLER["success"], fg="white", command=kaydet).pack(pady=15)

    def kiralama_gecmisi_penceresi(self):
        p = self.pencere_ac("Kiralama Geçmişi", 500)
        p.geometry("700x400")

        cols = ("plaka", "musteri", "baslangic", "bitis", "admin_iade")
        tree = ttk.Treeview(p, columns=cols, show="headings")
        for col, text in zip(cols, ["Plaka", "Müşteri", "Başlangıç", "Bitiş", "Admin İade"]):
            tree.heading(col, text=text)
            tree.column(col, width=120, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Verileri yükle
        if os.path.exists("kiralama_gecmisi.json"):
            with open("kiralama_gecmisi.json", "r", encoding="utf-8") as f:
                gecmis = json.load(f)
            for kayit in gecmis:
                tree.insert("", "end", values=(
                    kayit.get("plaka"),
                    kayit.get("musteri"),
                    kayit.get("baslangic"),
                    kayit.get("bitis"),
                    "Evet" if kayit.get("admin_iade") else "Hayır"
                ))
