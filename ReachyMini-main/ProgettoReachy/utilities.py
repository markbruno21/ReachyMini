#importato da alessio
from bs4 import BeautifulSoup, Comment
from audio_utils import parla
from reachy_mini_mock import ReachyMini
import re
import html


def clean_html_to_text(html_blob, max_chars=800):
    """
    Pulisce un frammento HTML e restituisce testo leggibile per TTS.
    - rimuove script/style/commenti
    - converte <li> in frasi separate
    - mantiene link come testo semplice (opzionale: aggiungi 'link' se vuoi)
    - decodifica entità HTML
    - tronca a max_chars senza spezzare parole
    """
    if not html_blob:
        return ""

    # 1. Decodifica entità HTML di base
    blob = html.unescape(html_blob)

    # 2. Parser HTML
    soup = BeautifulSoup(blob, "html.parser")

    # 3. Rimuovi script/style e commenti
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # 4. Trasforma liste in frasi separate
    for ul in soup.find_all(["ul", "ol"]):
        items = []
        for li in ul.find_all("li"):
            text = li.get_text(separator=" ", strip=True)
            if text:
                items.append(f"{text}.")
        replacement = "\n".join(items)
        ul.replace_with(replacement)

    # 5. Sostituisci i link con il loro testo visibile
    for a in soup.find_all("a"):
        txt = a.get_text(separator=" ", strip=True)
        a.replace_with(txt)

    # 6. Ottieni testo grezzo e normalizza spazi e righe
    text = soup.get_text(separator="\n", strip=True)
    # rimuovi righe vuote multiple
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    # sostituisci spazi multipli
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = text.strip()

    # 7. Tronca in modo intelligente
    if len(text) > max_chars:
        cut = text[:max_chars]
        # evita di troncare a metà parola
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        text = cut + "…"

    return text


def spegnimento(reachy: ReachyMini):
   
    parla("Avvio procedura di spegnimento")
    reachy.turn_off()
    print("✓  Robot disattivato.\n")
    return reachy