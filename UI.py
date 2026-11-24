import utils
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

# VAR GLOBALI

# per settings json
sec_principale = "UI"
sec_pagina = "pagina"
sec_img = "immagini"
sec_testo = "testo"
# --------------#


root = None     # finestra principale
larghezza_max_contenuto = 980   # larghezza massima della colonna centrale

dati_pagina = {}
dati_img = {}
dati_testo = {}

# ---------------- TEMI ---------------- #

TEMI = {
    "chiaro": {
        "sfondo": "#eef1f6",
        "card": "#ffffff",
        "bordo": "#dde2ea",
        "hover": "#f3f5fa",
        "testo": "#1f2937",
        "testo_secondario": "#6b7280",
        "primario": "#4f46e5",
        "primario_hover": "#4338ca",
        "testo_primario": "#ffffff",
        "secondario": "#e5e8ef",
        "secondario_hover": "#d6dbe5",
        "successo": "#16a34a",
        "successo_bg": "#dcfce7",
        "errore": "#dc2626",
        "errore_bg": "#fee2e2",
        "avviso": "#d97706",
        "avviso_bg": "#fef3c7",
        "marcata": "#c026d3",
        "progresso_bg": "#dde2ea",
        "input_bg": "#ffffff",
    },
    "scuro": {
        "sfondo": "#111827",
        "card": "#1f2937",
        "bordo": "#374151",
        "hover": "#273244",
        "testo": "#f3f4f6",
        "testo_secondario": "#9ca3af",
        "primario": "#6366f1",
        "primario_hover": "#818cf8",
        "testo_primario": "#ffffff",
        "secondario": "#374151",
        "secondario_hover": "#4b5563",
        "successo": "#4ade80",
        "successo_bg": "#14532d",
        "errore": "#f87171",
        "errore_bg": "#7f1d1d",
        "avviso": "#fbbf24",
        "avviso_bg": "#78350f",
        "marcata": "#e879f9",
        "progresso_bg": "#374151",
        "input_bg": "#111827",
    },
}

nome_tema = "chiaro"
C = dict(TEMI[nome_tema])   # colori del tema attivo


def init_settings_UI():
    global dati_pagina, dati_img, dati_testo

    dati = utils.get_settings(sec_principale) or {}

    dati_pagina = dati.get(sec_pagina, {})
    dati_img = dati.get(sec_img, {})
    dati_testo = dati.get(sec_testo, {})

    # valori di default se mancano nel settings.json
    dati_img.setdefault("larghezza", 800)
    dati_img.setdefault("altezza", 600)
    dati_img.setdefault("incremento_dimensione", 100)
    dati_testo.setdefault("font_titoli", "Arial")
    dati_testo.setdefault("font_testo", "Arial")
    dati_testo.setdefault("dimensione_base", 14)
    dati_testo.setdefault("diff_titoli", 2)
    dati_testo.setdefault("diff_info", 4)
    dati_testo.setdefault("diff_sett", 6)

    imposta_tema(dati_pagina.get("tema", "chiaro"))


def imposta_tema(nome):
    global nome_tema
    if nome not in TEMI:
        nome = "chiaro"
    nome_tema = nome
    C.clear()
    C.update(TEMI[nome])


def cambia_tema():
    imposta_tema("scuro" if nome_tema == "chiaro" else "chiaro")


# ---------------- FONT ---------------- #

def _dim(delta=0):
    return max(6, dati_testo["dimensione_base"] + delta)


def font_titolo(delta=0):
    return (dati_testo["font_titoli"], _dim(dati_testo["diff_titoli"] + delta), "bold")


def font_testo(delta=0, stile=""):
    if stile:
        return (dati_testo["font_testo"], _dim(delta), stile)
    return (dati_testo["font_testo"], _dim(delta))


def font_info(stile=""):
    return font_testo(-dati_testo["diff_info"], stile)


def font_piccolo(stile="bold"):
    return font_testo(-dati_testo["diff_sett"], stile)


# ---------------- WIDGET ---------------- #

def pulisci_finestra(finestra):
    for widget in finestra.winfo_children():
        widget.destroy()


def bottone(contenitore, testo, comando, stile="primario", font=None, padx=18, pady=8):
    """Bottone piatto con effetto hover. stile: primario, secondario, successo, errore"""
    colori = {
        "primario": (C["primario"], C["primario_hover"], C["testo_primario"]),
        "secondario": (C["secondario"], C["secondario_hover"], C["testo"]),
        "successo": (C["successo"], C["successo"], C["testo_primario"]),
        "errore": (C["errore"], C["errore"], C["testo_primario"]),
    }
    bg, bg_hover, fg = colori.get(stile, colori["primario"])

    btn = tk.Label(
        contenitore, text=testo, bg=bg, fg=fg,
        font=font or font_testo(0, "bold"),
        padx=padx, pady=pady, cursor="hand2",
    )
    btn._abilitato = True

    def on_enter(_):
        if btn._abilitato:
            btn.config(bg=bg_hover)

    def on_leave(_):
        if btn._abilitato:
            btn.config(bg=bg)

    def on_click(_):
        if btn._abilitato and comando:
            comando()

    def set_abilitato(stato):
        btn._abilitato = stato
        if stato:
            btn.config(bg=bg, fg=fg, cursor="hand2")
        else:
            btn.config(bg=C["secondario"], fg=C["testo_secondario"], cursor="arrow")

    btn.set_abilitato = set_abilitato
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<ButtonRelease-1>", on_click)
    return btn


def card(contenitore, padx=24, pady=20):
    """Pannello bianco (o scuro) con bordo sottile. Ritorna (esterno, interno)."""
    esterno = tk.Frame(contenitore, bg=C["bordo"])
    interno = tk.Frame(esterno, bg=C["card"], padx=padx, pady=pady)
    interno.pack(fill="both", expand=True, padx=1, pady=1)
    return esterno, interno


def barra_progresso(contenitore, frazione, altezza=6):
    cv = tk.Canvas(contenitore, height=altezza, bg=C["progresso_bg"], highlightthickness=0, bd=0)

    def ridisegna(_=None):
        cv.delete("all")
        w = cv.winfo_width()
        cv.create_rectangle(0, 0, int(w * max(0.0, min(1.0, frazione))), altezza,
                            fill=C["primario"], width=0)

    cv.bind("<Configure>", ridisegna)
    return cv


class Opzione(tk.Frame):
    """Riga cliccabile per una risposta (checkbox o radio disegnati a mano)."""

    def __init__(self, contenitore, testo, variabile, valore=None, multipla=True, comando=None, nota=None):
        super().__init__(contenitore, bg=C["bordo"], cursor="hand2")
        self.testo = testo
        self.var = variabile
        self.valore = valore
        self.multipla = multipla
        self.comando = comando
        self.bloccata = False
        self.stato = None   # None, "corretta", "errata", "mancata"

        self.interno = tk.Frame(self, bg=C["card"], padx=14, pady=10)
        self.interno.pack(fill="both", expand=True, padx=1, pady=1)

        self.indicatore = tk.Label(self.interno, bg=C["card"], fg=C["testo_secondario"],
                                   font=font_testo(2), width=2)
        self.indicatore.pack(side="left", anchor="n")

        self.etichetta = tk.Label(self.interno, text=testo, bg=C["card"], fg=C["testo"],
                                  font=font_testo(), justify="left", anchor="w")
        self.etichetta.pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.esito = tk.Label(self.interno, bg=C["card"], font=font_testo(0, "bold"))
        self.esito.pack(side="right", anchor="n", padx=(8, 0))

        widgets = [self, self.interno, self.indicatore, self.etichetta, self.esito]
        self.nota = None
        if nota:
            self.nota = tk.Label(self.interno, text=nota, bg=C["card"], fg=C["testo_secondario"],
                                 font=font_info())
            self.nota.pack(side="right", padx=(8, 0))
            widgets.append(self.nota)

        for w in widgets:
            w.bind("<ButtonRelease-1>", self._click)
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

        self.var.trace_add("write", lambda *_: self.aggiorna())
        self.aggiorna()

    def selezionata(self):
        if self.multipla:
            return bool(self.var.get())
        return self.var.get() == self.valore

    def _click(self, _):
        if self.bloccata:
            return
        if self.multipla:
            self.var.set(not self.var.get())
        else:
            self.var.set(self.valore)
        if self.comando:
            self.comando()

    def _enter(self, _):
        if not self.bloccata and self.stato is None:
            self._sfondo(C["hover"])

    def _leave(self, _):
        if self.stato is None:
            self._sfondo(C["card"])

    def _sfondo(self, colore):
        for w in (self.interno, self.indicatore, self.etichetta, self.esito, self.nota):
            if w is not None:
                w.config(bg=colore)

    def set_wrap(self, larghezza):
        self.etichetta.config(wraplength=max(150, larghezza))

    def segna(self, stato):
        """stato: 'corretta', 'errata', 'mancata' (corretta ma non selezionata) o None"""
        self.stato = stato
        self.bloccata = stato is not None
        self.config(cursor="arrow" if self.bloccata else "hand2")
        self.aggiorna()

    def aggiorna(self):
        sel = self.selezionata()
        if self.multipla:
            simbolo = "☑" if sel else "☐"
        else:
            simbolo = "◉" if sel else "○"

        bordo = C["primario"] if sel else C["bordo"]
        sfondo = C["card"]
        colore_ind = C["primario"] if sel else C["testo_secondario"]
        esito = ""
        colore_esito = C["testo"]

        if self.stato == "corretta":
            bordo, sfondo, colore_ind = C["successo"], C["successo_bg"], C["successo"]
            esito, colore_esito = "✓", C["successo"]
        elif self.stato == "mancata":
            bordo, sfondo, colore_ind = C["successo"], C["successo_bg"], C["successo"]
            esito, colore_esito = "✓", C["successo"]
        elif self.stato == "errata":
            bordo, sfondo, colore_ind = C["errore"], C["errore_bg"], C["errore"]
            esito, colore_esito = "✗", C["errore"]

        self.config(bg=bordo)
        self._sfondo(sfondo)
        self.indicatore.config(text=simbolo, fg=colore_ind)
        self.esito.config(text=esito, fg=colore_esito)


def crea_widget_immagine(contenitore, percorso_file, larghezza_max=300, altezza_max=200):
    if not os.path.exists(percorso_file):
        print(f"Errore: Immagine '{percorso_file}' non trovata.")
        return tk.Label(contenitore, text="(Immagine mancante)", bg=C["card"],
                        fg=C["testo_secondario"], font=font_info("italic"))

    try:
        img_originale = Image.open(percorso_file)

        # Calcolo Proporzioni
        img_originale.thumbnail((larghezza_max, altezza_max), Image.Resampling.LANCZOS)

        foto_tk = ImageTk.PhotoImage(img_originale)

        lbl_img = tk.Label(contenitore, image=foto_tk, bg=C["card"], bd=0)

        lbl_img.image = foto_tk
        return lbl_img

    except Exception as e:
        print(f"Errore caricamento: {e}")
        return tk.Label(contenitore, text="Errore Immagine", bg=C["card"], fg=C["errore"])


# Rubata da stack overflow (e poi sistemata):
_scrollabili = []   # tutte le ScrollableFrame create (per smistare la rotella del mouse)


def _rotella_globale(event):
    """Scorre la ScrollableFrame che si trova sotto al puntatore (o la prima, se nessuna)."""
    for s in list(_scrollabili):
        if not s.winfo_exists():
            _scrollabili.remove(s)
    if not _scrollabili:
        return
    try:
        w = event.widget.winfo_containing(event.x_root, event.y_root)
    except Exception:
        w = None
    while w is not None:
        if w in _scrollabili:
            w._on_mousewheel(event)
            return
        w = w.master
    _scrollabili[0]._on_mousewheel(event)


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, sfondo="sfondo", **kwargs):
        super().__init__(container, *args, **kwargs)
        self.on_resize = None   # funzione(larghezza) chiamata quando cambia la larghezza
        self.sfondo = sfondo    # chiave del colore di sfondo nel tema

        # 1. Canvas e Scrollbar
        # highlightthickness=0 rimuove i bordi brutti
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                      relief="flat", bd=0, width=12, elementborderwidth=0)

        # frame interno (Contenuto)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # scrollbar automatica
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)

        # fix testo tagliato, larghezza automatica
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # collegamento tra canvas e scroll coso
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.applica_tema()

        # Mousewheel (su tutta la finestra)
        self._bind_mouse_scroll()

    def applica_tema(self):
        sfondo = C[self.sfondo]
        self.config(bg=sfondo)
        self.canvas.config(bg=sfondo)
        self.scrollable_frame.config(bg=sfondo)
        self.scrollbar.config(bg=C["secondario"], troughcolor=sfondo,
                              activebackground=C["secondario_hover"])

    def _on_frame_configure(self, event):
        """Aggiorna la scrollbar quando il contenuto interno cambia dimensione"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Allarga il frame interno per riempire la larghezza della finestra"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        if self.on_resize:
            self.on_resize(event.width)

    def force_scroll_update(self):
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def torna_in_cima(self):
        self.canvas.yview_moveto(0)

    def _bind_mouse_scroll(self):
        primo = not _scrollabili
        _scrollabili.append(self)
        if not primo:
            return
        top = self.winfo_toplevel()
        if sys.platform.startswith('linux'):
            top.bind_all("<Button-4>", _rotella_globale)
            top.bind_all("<Button-5>", _rotella_globale)
        else:
            top.bind_all("<MouseWheel>", _rotella_globale)

    def _on_mousewheel(self, event):
        # non scrollare se il contenuto sta tutto nella finestra
        if self.canvas.yview() == (0.0, 1.0):
            return
        if sys.platform.startswith('linux'):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class PannelloDomande(tk.Frame):
    """Barra laterale con i numeri di tutte le domande, colorati in base all'esito.
    on_click(i): chiamata col click sinistro, on_marca(i): col click destro."""

    colonne = 5

    def __init__(self, contenitore, on_click=None, on_marca=None):
        super().__init__(contenitore)
        self.on_click = on_click
        self.on_marca = on_marca
        self.caselle = []

        self.separatore = tk.Frame(self, width=1)
        self.separatore.pack(side="right", fill="y")

        # intestazione con i conteggi
        self.header = tk.Frame(self, padx=14, pady=14)
        self.header.pack(side="top", fill="x")
        self.lbl_titolo = tk.Label(self.header, text="DOMANDE", anchor="w")
        self.lbl_titolo.pack(fill="x")
        self.lbl_fatte = tk.Label(self.header, anchor="w")
        self.lbl_fatte.pack(fill="x", pady=(6, 0))
        self.riga_stats = tk.Frame(self.header)
        self.riga_stats.pack(fill="x", pady=(2, 0))
        self.lbl_stats = {}
        for n, chiave in enumerate(("corretta", "parziale", "errata", "marcata")):
            lbl = tk.Label(self.riga_stats, anchor="w")
            lbl.grid(row=n // 2, column=n % 2, sticky="w", padx=(0, 12))
            self.lbl_stats[chiave] = lbl

        self.lbl_aiuto = tk.Label(self, text="Click: vai alla domanda\nClick destro / M: marca",
                                  justify="left", anchor="w", padx=14, pady=10)
        self.lbl_aiuto.pack(side="bottom", fill="x")

        # griglia scorrevole dei numeri
        self.scroll = ScrollableFrame(self, sfondo="card")
        self.scroll.pack(side="top", fill="both", expand=True)
        self.griglia = tk.Frame(self.scroll.scrollable_frame, padx=11, pady=4)
        self.griglia.pack(anchor="nw")

    def _crea_caselle(self, n):
        for c in self.caselle:
            c["bordo"].destroy()
        self.caselle = []

        tasto_destro = ["<Button-3>"] + (["<Button-2>"] if sys.platform == "darwin" else [])
        for i in range(n):
            bordo = tk.Frame(self.griglia, cursor="hand2")
            bordo.grid(row=i // self.colonne, column=i % self.colonne, padx=3, pady=3)
            numero = tk.Label(bordo, text=str(i + 1), width=4, pady=4)
            numero.pack(padx=2, pady=2)
            flag = tk.Label(numero, text="⚑", bd=0, padx=0, pady=0)
            casella = {"bordo": bordo, "numero": numero, "flag": flag, "colore_bordo": None}

            for w in (bordo, numero, flag):
                w.bind("<ButtonRelease-1>", lambda _, i=i: self.on_click and self.on_click(i))
                for seq in tasto_destro:
                    w.bind(seq, lambda _, i=i: self.on_marca and self.on_marca(i))
                w.bind("<Enter>", lambda _, c=casella: c["bordo"].config(bg=C["testo_secondario"]))
                w.bind("<Leave>", lambda _, c=casella: c["bordo"].config(bg=c["colore_bordo"]))
            self.caselle.append(casella)

    def _applica_tema(self):
        for w in (self, self.header, self.riga_stats, self.griglia):
            w.config(bg=C["card"])
        self.separatore.config(bg=C["bordo"])
        self.scroll.applica_tema()
        self.lbl_titolo.config(bg=C["card"], fg=C["testo_secondario"], font=font_piccolo("bold"))
        self.lbl_fatte.config(bg=C["card"], fg=C["testo"], font=font_info())
        self.lbl_aiuto.config(bg=C["card"], fg=C["testo_secondario"], font=font_piccolo(""))
        colori = {"corretta": C["successo"], "parziale": C["avviso"],
                  "errata": C["errore"], "marcata": C["marcata"]}
        for chiave, lbl in self.lbl_stats.items():
            lbl.config(bg=C["card"], fg=colori[chiave], font=font_info("bold"))

    def aggiorna(self, stati, corrente=None):
        """stati: lista di (esito, marcata) con esito in None, 'corretta', 'parziale', 'errata'.
        corrente: indice della domanda attuale (o None)."""
        if len(stati) != len(self.caselle):
            self._crea_caselle(len(stati))
        self._applica_tema()

        stili = {
            None: (C["sfondo"], C["testo_secondario"]),
            "corretta": (C["successo_bg"], C["successo"]),
            "parziale": (C["avviso_bg"], C["avviso"]),
            "errata": (C["errore_bg"], C["errore"]),
        }
        conteggi = {"corretta": 0, "parziale": 0, "errata": 0, "marcata": 0}

        for i, (esito, marcata) in enumerate(stati):
            c = self.caselle[i]
            bg, fg = stili.get(esito, stili[None])
            if i == corrente:
                c["colore_bordo"] = C["primario"]
            elif marcata:
                c["colore_bordo"] = C["marcata"]
            else:
                c["colore_bordo"] = bg
            c["bordo"].config(bg=c["colore_bordo"])
            c["numero"].config(bg=bg, fg=fg, font=font_info("bold"))
            c["flag"].config(bg=bg, fg=C["marcata"], font=font_piccolo(""))
            if marcata:
                c["flag"].place(relx=1.0, rely=0.0, anchor="ne")
                conteggi["marcata"] += 1
            else:
                c["flag"].place_forget()
            if esito in conteggi:
                conteggi[esito] += 1

        n_fatte = conteggi["corretta"] + conteggi["parziale"] + conteggi["errata"]
        self.lbl_fatte.config(text=f"Fatte {n_fatte} / {len(stati)}")
        nomi = {"corretta": "Corrette", "parziale": "Parziali", "errata": "Errate", "marcata": "Marcate"}
        for chiave, lbl in self.lbl_stats.items():
            lbl.config(text=f"{nomi[chiave]} {conteggi[chiave]}")

        self.after_idle(lambda: self._dopo_aggiornamento(corrente))

    def _dopo_aggiornamento(self, corrente):
        if not self.winfo_exists():
            return
        self.update_idletasks()
        # il pannello è largo quanto la griglia
        larghezza = max(self.griglia.winfo_reqwidth(), self.header.winfo_reqwidth())
        if self.scroll.canvas.winfo_pixels(self.scroll.canvas.cget("width")) != larghezza:
            self.scroll.canvas.config(width=larghezza)
            self.update_idletasks()
        if corrente is not None and 0 <= corrente < len(self.caselle):
            self._mostra(corrente)

    def _mostra(self, i):
        """Scorre la griglia in modo che la casella i sia visibile."""
        sf = self.scroll.scrollable_frame
        totale = sf.winfo_height()
        if totale <= 1:
            return
        b = self.caselle[i]["bordo"]
        y = b.winfo_rooty() - sf.winfo_rooty()
        h = b.winfo_height()
        alto, basso = self.scroll.canvas.yview()
        if y < alto * totale or y + h > basso * totale:
            vista = self.scroll.canvas.winfo_height()
            self.scroll.canvas.yview_moveto(max(0.0, (y + h / 2 - vista / 2) / totale))
