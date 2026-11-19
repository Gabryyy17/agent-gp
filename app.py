import streamlit as st
from groq import Groq
from ddgs import DDGS
from datetime import datetime
from pypdf import PdfReader
import docx
from PIL import Image
import base64
from gtts import gTTS
import io
import json
import os
import subprocess
import webbrowser
import urllib.parse
import uuid

CARTELLA_BASE = os.path.dirname(os.path.abspath(__file__))
FILE_CONFIG = os.path.join(CARTELLA_BASE, "config_agent_gp.json")
FILE_MEMORIA = os.path.join(CARTELLA_BASE, "memoria_chat_multiuso.json")

def carica_api_key():
    if os.path.exists(FILE_CONFIG):
        try:
            with open(FILE_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f).get("api_key", "")
        except Exception:
            return ""
    return ""

def salva_api_key(chiave):
    try:
        with open(FILE_CONFIG, "w", encoding="utf-8") as f:
            json.dump({"api_key": chiave}, f)
    except Exception:
        pass

def carica_tutte_le_chat():
    if os.path.exists(FILE_MEMORIA):
        try:
            with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
                dati = json.load(f)
                if isinstance(dati, dict) and dati:
                    return dati
        except Exception:
            pass
    
    chat_id_iniziale = str(uuid.uuid4())[:8]
    return {
        chat_id_iniziale: {
            "titolo": "Nuova Chat",
            "messaggi": [
                {"role": "assistant", "content": "### Sistema Operativo Online\nAgent GP online al 100%, Comandante. Pronto per l'analisi visiva e testuale."}
            ]
        }
    }

def salva_tutte_le_chat(chat_dict):
    try:
        with open(FILE_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(chat_dict, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def esegui_azione_pc(comando):
    cmd = comando.lower().strip()
    
    if "invia una mail a " in cmd or "scrivi una mail a " in cmd or "manda una mail a " in cmd or "spedisci una mail a " in cmd:
        try:
            dopo_a = comando.split(" a ")[1].strip()
            destinatario = dopo_a.split(" ")[0].strip()
            
            oggetto = "Messaggio da Agent GP"
            corpo = ""
            
            if " con oggetto " in comando:
                parte_ogg = comando.split(" con oggetto ")[1]
                if " e testo " in parte_ogg:
                    oggetto = parte_ogg.split(" e testo ")[0].strip()
                    corpo = parte_ogg.split(" e testo ")[1].strip()
                else:
                    oggetto = parte_ogg.strip()
            elif " e testo " in comando:
                corpo = comando.split(" e testo ")[1].strip()

            url_gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(destinatario)}&su={urllib.parse.quote(oggetto)}&body={urllib.parse.quote(corpo)}"
            webbrowser.open(url_gmail)
            return f"### Email Precompilata\n🌐 Ho aperto Gmail con la bozza per **{destinatario}** (Oggetto: *{oggetto}*)."
        except Exception as e:
            webbrowser.open("https://mail.google.com/mail/?view=cm&fs=1")
            return f"### Apertura Gmail\nHo aperto Gmail per la composizione ({e})."

    trigger = (
        "apri ", "avvia ", "lancia ", 
        "cerca su youtube ", "cerca su google ", "cerca su spotify ", 
        "blocca il pc", "blocca lo schermo"
    )
    if not cmd.startswith(trigger):
        return None

    try:
        if cmd.startswith("cerca su youtube "):
            q = urllib.parse.quote(cmd.replace("cerca su youtube ", "", 1))
            webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
            return "### Ricerca YouTube Avviata\nRicerca avviata su YouTube."

        if cmd.startswith("cerca su spotify "):
            q = urllib.parse.quote(cmd.replace("cerca su spotify ", "", 1))
            webbrowser.open(f"https://open.spotify.com/search/{q}")
            return "### Ricerca Spotify Avviata\nRicerca avviata su Spotify."

        if cmd.startswith("cerca su google "):
            q = urllib.parse.quote(cmd.replace("cerca su google ", "", 1))
            webbrowser.open(f"https://www.google.com/search?q={q}")
            return "### Ricerca Google Avviata\nRicerca avviata su Google."

        if "blocca" in cmd and ("pc" in cmd or "schermo" in cmd or "computer" in cmd):
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "### Sistema Bloccato\nSchermo del PC bloccato."

        if "spotify" in cmd:
            try:
                os.startfile("spotify:")
            except Exception:
                webbrowser.open("https://open.spotify.com")
            return "### Avvio Spotify\nHo avviato **Spotify**, Comandante."

        if "netflix" in cmd:
            try:
                app_id = r"shell:AppsFolder\4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App"
                subprocess.Popen(["explorer.exe", app_id])
            except Exception:
                webbrowser.open("https://www.netflix.com")
            return "### Avvio Netflix\n🎬 Ho avviato **Netflix**, Comandante."

        if "fotocamera" in cmd or "camera" in cmd:
            os.startfile("microsoft.windows.camera:")
            return "### Attivazione Fotocamera\n📷 Ho attivato la **Fotocamera**."

        siti = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "instagram": "https://www.instagram.com",
            "chatgpt": "https://chatgpt.com",
            "github": "https://github.com",
            "wikipedia": "https://it.wikipedia.org"
        }
        for k, url in siti.items():
            if k in cmd:
                webbrowser.open(url)
                return f"### Apertura {k.capitalize()}\n🌐 Ho aperto **{k.capitalize()}** nel tuo browser."

        if "download" in cmd:
            os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))
            return "### Apertura Cartella Download\n📂 Ho aperto la cartella **Download**."
        if "desktop" in cmd:
            os.startfile(os.path.join(os.path.expanduser("~"), "Desktop"))
            return "### Apertura Cartella Desktop\n📂 Ho aperto la cartella **Desktop**."
        if "cartella assistente" in cmd or "cartella progetto" in cmd:
            os.startfile(CARTELLA_BASE)
            return "### Apertura Cartella Progetto\n📂 Ho aperto la cartella di **Agent GP**."

        programmi = {
            "calcolatrice": "calc.exe",
            "blocco note": "notepad.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "terminale": "cmd.exe",
            "prompt": "cmd.exe",
            "gestione attività": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            "impostazioni": "ms-settings:",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "esplora file": "explorer.exe"
        }
        for nome_app, eseguibile in programmi.items():
            if nome_app in cmd:
                if eseguibile.startswith("ms-"):
                    os.startfile(eseguibile)
                else:
                    subprocess.Popen(eseguibile, shell=True)
                return f"### Avvio {nome_app.capitalize()}\n🚀 Ho avviato **{nome_app.capitalize()}** sul tuo PC."

        return None
    except Exception as e:
        return f"### Errore PC\n⚠️ {e}"

st.set_page_config(page_title="Agent GP - Cyber Terminal", page_icon="🔴", layout="centered")

stile_css = """
<style>
.stApp { background-color: #070709; color: #ffffff; }
[data-testid='stSidebar'] { background-color: #0f0f13; border-right: 1px solid #ff1e38; }
h1, h2, h3, h4, [data-testid='stChatMessage'] h1, [data-testid='stChatMessage'] h2, [data-testid='stChatMessage'] h3, [data-testid='stChatMessage'] h4 {
    color: #ff1e38 !important; font-family: 'Courier New', Courier, monospace; letter-spacing: 1px;
}
[data-testid='stChatMessage'] p, [data-testid='stChatMessage'] li, [data-testid='stChatMessage'] span, [data-testid='stChatMessage'] div {
    color: #ffffff !important;
}
[data-testid='stChatMessage'] strong { color: #ffffff !important; font-weight: bold; }
.stChatInput input { background-color: #121218 !important; color: #ffffff !important; border: 1px solid #ff1e38 !important; }
.stChatInput input:focus { border-color: #ff334b !important; box-shadow: 0 0 10px rgba(255, 30, 56, 0.5); }
.stButton button { background-color: #ff1e38 !important; color: #ffffff !important; border: none; font-weight: bold; transition: 0.3s; }
.stButton button:hover { background-color: #cc0020 !important; box-shadow: 0 0 15px #ff1e38; }
a { color: #ff1e38 !important; }
</style>
"""
st.markdown(stile_css, unsafe_allow_html=True)

st.title("🔴 AGENT GP // CORE")
st.caption("Sistema di Intelligenza Artificiale Avanzato — Controllo PC, Visione Immagini & Voce")

def estrai_testo_documento(file_caricato):
    testo = ""
    nome = file_caricato.name.lower()
    try:
        if nome.endswith(".pdf"):
            lettore = PdfReader(file_caricato)
            for pagina in lettore.pages:
                testo += (pagina.extract_text() or "") + "\n"
        elif nome.endswith(".docx"):
            doc = docx.Document(file_caricato)
            for paragrafo in doc.paragraphs:
                testo += paragrafo.text + "\n"
        elif nome.endswith(".txt"):
            testo = file_caricato.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Errore durante la lettura del file: {e}"
    return testo[:25000]

def cerca_sul_web(query):
    testo_risultati = ""
    parole_inutili = ["allora", "voglio sapere", "dimmi", "cercami", "quali sono", "per favore", "agent gp"]
    query_pulita = query.lower()
    for p in parole_inutili:
        query_pulita = query_pulita.replace(p, "")
    query_pulita = query_pulita.strip() or query

    try:
        with DDGS(timeout=10) as ddgs:
            try:
                notizie = list(ddgs.news(query_pulita, region="it-it", max_results=4))
                if notizie:
                    testo_risultati += "### ULTIME NOTIZIE TROVATE:\n"
                    for n in notizie:
                        testo_risultati += f"- [{n.get('date', 'Recente')}] **{n.get('title', '')}**: {n.get('body', '')}\n"
            except Exception:
                pass

            try:
                pagine = list(ddgs.text(query_pulita, region="it-it", max_results=4))
                if pagine:
                    testo_risultati += "\n### PAGINE WEB TROVATE:\n"
                    for p in pagine:
                        testo_risultati += f"- **{p.get('title', '')}**: {p.get('body', '')}\n"
            except Exception:
                pass

        return testo_risultati if testo_risultati else "Nessun risultato trovato dal web."
    except Exception as e:
        return f"Connessione web non disponibile ({e})."

def genera_audio_risposta(testo):
    try:
        testo_pulito = testo.replace("*", "").replace("#", "").replace("`", "")
        tts = gTTS(text=testo_pulito[:1500], lang="it", slow=False)
        buffer_audio = io.BytesIO()
        tts.write_to_fp(buffer_audio)
        buffer_audio.seek(0)
        return buffer_audio
    except Exception:
        return None

if "tutte_le_chat" not in st.session_state:
    st.session_state.tutte_le_chat = carica_tutte_le_chat()

if "chat_attiva_id" not in st.session_state:
    st.session_state.chat_attiva_id = list(st.session_state.tutte_le_chat.keys())[0]

with st.sidebar:
    st.header("💬 CRONOLOGIA CHAT")
    
    if st.button("➕ Nuova Chat", use_container_width=True):
        nuovo_id = str(uuid.uuid4())[:8]
        st.session_state.tutte_le_chat[nuovo_id] = {
            "titolo": "Nuova Chat",
            "messaggi": [{"role": "assistant", "content": "### Nuova Sessione\nPronto, Comandante. Come posso aiutarti?"}]
        }
        st.session_state.chat_attiva_id = nuovo_id
        salva_tutte_le_chat(st.session_state.tutte_le_chat)
        st.rerun()

    st.markdown("---")
    
    chat_ids = list(st.session_state.tutte_le_chat.keys())
    for cid in chat_ids:
        info_chat = st.session_state.tutte_le_chat[cid]
        titolo_mostrato = info_chat["titolo"]
        if len(titolo_mostrato) > 22:
            titolo_mostrato = titolo_mostrato[:20] + "..."
            
        col_seleziona, col_elimina = st.columns([0.75, 0.25])
        with col_seleziona:
            is_active = (cid == st.session_state.chat_attiva_id)
            etichetta = f"📍 {titolo_mostrato}" if is_active else titolo_mostrato
            if st.button(etichetta, key=f"btn_chat_{cid}", use_container_width=True):
                st.session_state.chat_attiva_id = cid
                st.rerun()
        with col_elimina:
            if st.button("🗑️", key=f"del_chat_{cid}", use_container_width=True):
                if len(st.session_state.tutte_le_chat) > 1:
                    del st.session_state.tutte_le_chat[cid]
                    st.session_state.chat_attiva_id = list(st.session_state.tutte_le_chat.keys())[0]
                    salva_tutte_le_chat(st.session_state.tutte_le_chat)
                    st.rerun()
                else:
                    st.toast("Non puoi eliminare l'ultima chat attiva!", icon="⚠️")

    st.markdown("---")
    st.header("⚙️ CONFIGURAZIONE")
    
    chiave_salvata = carica_api_key()
    api_key_input = st.text_input("Chiave API di Groq", value=chiave_salvata, type="password")
    
    if api_key_input and api_key_input != chiave_salvata:
        salva_api_key(api_key_input)
        st.toast("Chiave API salvata!", icon="💾")
    
    modello_scelto = None
    if api_key_input:
        try:
            client = Groq(api_key=api_key_input)
            
            # Elenco aggiornato con i modelli Llama attivi e supportati su Groq
            modelli_chat = [
                "llama-3.2-90b-vision-preview",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "openai/gpt-oss-120b"
            ]
            
            modello_scelto = st.selectbox("🧠 Motore AI attivo:", modelli_chat, key="selettore_modello_persistente")
        except Exception as e:
            st.error(f"Errore API: {e}")

    st.markdown("---")
    st.subheader("💻 CONTROLLO PC")
    controllo_pc_attivo = st.toggle("⚡ Comandi di sistema attivi", value=True)
    with st.expander("📋 Lista comandi rapidi"):
        st.markdown(
            "- *Invia una mail a [email] con oggetto [ogg] e testo [testo]*\n"
            "- *Apri spotify / netflix / fotocamera*\n"
            "- *Cerca su spotify [canzone]*\n"
            "- *Apri calcolatrice / blocco note / word*\n"
            "- *Apri youtube / gmail / whatsapp*\n"
            "- *Cerca su youtube [argomento]*\n"
            "- *Apri download / desktop*\n"
            "- *Blocca lo schermo*"
        )

    st.markdown("---")
    st.subheader("🎙️ MODULO VOCALE")
    risposta_vocale = st.toggle("🔊 Risposta vocale attiva", value=True)
    audio_registrato = st.audio_input("Registra comando vocale")

    st.markdown("---")
    st.subheader("📄 ANALISI FILE & IMMAGINI")
    file_utente = st.file_uploader("Carica PDF, Word, TXT o JPG/PNG", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"])
    
    testo_documento = ""
    immagine_base64 = None
    
    if file_utente:
        if file_utente.name.lower().endswith((".jpg", ".jpeg", ".png")):
            st.image(file_utente, caption="Immagine caricata", use_container_width=True)
            bytes_img = file_utente.read()
            immagine_base64 = base64.b64encode(bytes_img).decode("utf-8")
        else:
            with st.spinner("Elaborazione file..."):
                testo_documento = estrai_testo_documento(file_utente)
                st.success(f"File caricato: **{file_utente.name}**")

    st.markdown("---")
    usa_web = st.toggle("🌐 Ricerca Web & News in tempo reale", value=True)

if not api_key_input or not modello_scelto:
    st.warning("⚠️ ACCESSO NEGATO: Inserisci una **Groq API Key** nella barra laterale.")
else:
    chat_corrente = st.session_state.tutte_le_chat[st.session_state.chat_attiva_id]
    messages = chat_corrente["messaggi"]

    if "ultimo_audio_processato" not in st.session_state:
        st.session_state.ultimo_audio_processato = None

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt_testo = st.chat_input("Invia un comando o chiedi di risolvere l'esercizio...")
    prompt_finale = None

    if prompt_testo:
        prompt_finale = prompt_testo
    elif audio_registrato is not None and audio_registrato != st.session_state.ultimo_audio_processato:
        st.session_state.ultimo_audio_processato = audio_registrato
        with st.spinner("🎙️ Decodifica vocale..."):
            try:
                trascrizione = client.audio.transcriptions.create(
                    file=("comando.wav", audio_registrato.getvalue()),
                    model="whisper-large-v3-turbo",
                    language="it"
                )
                prompt_finale = trascrizione.text
            except Exception as e:
                st.error(f"Errore vocale: {e}")

    if prompt_finale:
        if chat_corrente["titolo"] == "Nuova Chat":
            chat_corrente["titolo"] = prompt_finale[:25]

        testo_storico_messaggio = prompt_finale
        if immagine_base64:
            testo_storico_messaggio += " [📸 Immagine allegata]"

        messages.append({"role": "user", "content": testo_storico_messaggio})
        salva_tutte_le_chat(st.session_state.tutte_le_chat)
        
        with st.chat_message("user"):
            st.markdown(prompt_finale)
            if immagine_base64:
                st.info("📸 Immagine allegata inviata per l'analisi visiva.")

        with st.chat_message("assistant"):
            esito_pc = esegui_azione_pc(prompt_finale) if controllo_pc_attivo else None

            if esito_pc:
                st.markdown(esito_pc)
                if risposta_vocale:
                    audio_risposta = genera_audio_risposta(esito_pc)
                    if audio_risposta:
                        st.audio(audio_risposta, format="audio/mp3", autoplay=True)
                messages.append({"role": "assistant", "content": esito_pc})
                salva_tutte_le_chat(st.session_state.tutte_le_chat)
            else:
                contesto_extra = ""
                dati_web = ""

                if testo_documento:
                    contesto_extra += f"\n\n[DOCUMENTO CARICATO]:\n{testo_documento}\n"

                if usa_web and not testo_documento and not immagine_base64:
                    with st.spinner("🌐 Ricerca in rete..."):
                        dati_web = cerca_sul_web(prompt_finale)
                        contesto_extra += f"\n\n[DATI WEB]:\n{dati_web}\n"

                with st.spinner(f"Elaborazione con {modello_scelto}..."):
                    try:
                        sys_prompt = (
                            "Sei Agent GP, un'IA avanzata di supporto tecnico e scolastico con stile cyberpunk nero e rosso. "
                            f"Oggi è {datetime.now().strftime('%d %B %Y')}. "
                            "Quando ti viene fornita un'immagine con un esercizio (es. matematica), analizzala visivamente, estrai il testo o le formule e fornisci la soluzione completa spiegata passo dopo passo. "
                            "Inizia SEMPRE ogni risposta con un titolo preceduto da '### ' (es: ### Risoluzione Esercizio)."
                        )
                        
                        messaggi_da_inviare = [{"role": "system", "content": sys_prompt}]
                        
                        for m in messages[:-1]:
                            messaggi_da_inviare.append({"role": m["role"], "content": m["content"]})
                            
                        if immagine_base64:
                            payload_corrente = [
                                {"type": "text", "text": prompt_finale + "\n\n[Analizza l'immagine allegata e risolvi l'esercizio matematico passo dopo passo con precisione]."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{immagine_base64}"}}
                            ]
                            messaggi_da_inviare.append({"role": "user", "content": payload_corrente})
                        else:
                            messaggi_da_inviare.append({"role": "user", "content": prompt_finale + contesto_extra})

                        response = client.chat.completions.create(
                            model=modello_scelto,
                            messages=messaggi_da_inviare,
                            temperature=0.3
                        )
                        
                        answer = response.choices[0].message.content
                        st.markdown(answer)

                        if risposta_vocale:
                            audio_risposta = genera_audio_risposta(answer)
                            if audio_risposta:
                                st.audio(audio_risposta, format="audio/mp3", autoplay=True)
                        
                        messages.append({"role": "assistant", "content": answer})
                        salva_tutte_le_chat(st.session_state.tutte_le_chat)
                        
                    except Exception as e:
                        st.error(f"Errore di sistema: {e}")