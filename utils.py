import json
import os
import random

# ---------------VAR GLOBALI-------------------#

# per impostaizoni da json
settings_path = "settings.json"

sec_config = "config"
# -------------------#


config: dict = {}
settings_path_domande_selezionato = ""


# ----------------------------------------------#


def randomizza_lista(list_inp):
    new_list = []
    lista = list_inp.copy()

    while len(lista) > 0:
        rand = random.randrange(len(lista))
        new_list.append(lista.pop(rand))

    return new_list


def elenca_file_json(cartella="./"):
    files_json = []

    try:
        tutti_i_file = os.listdir(cartella)

        for file in tutti_i_file:
            if file.lower().endswith(".json"):
                files_json.append(f"{cartella}{file}")

    except FileNotFoundError:
        print(f"Errore: La cartella '{cartella}' non esiste.")
        return []

    return files_json


def get_settings(section):
    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            settings = json.load(file)
    except FileNotFoundError:
        print("Errore", f"File {settings_path} non trovato!")
        return None
    except json.JSONDecodeError:
        print("Errore", f"Il file {settings_path} non è formattato correttamente.")
        return None

    if section not in settings:
        print(f"Sezione {section} non presente nel file {settings_path}")
        return None

    return settings[section]


def init_config():
    global config
    config = get_settings(sec_config) or {}
