import re

def estrai_nome(testo: str) -> str:
    testo = testo.lower().strip()
    
    for frase in ["mi chiamo", "il mio nome è", "mi chiamano", "sono"]:
        if frase in testo:
            nome = testo.split(frase)[-1].strip()
            # prende solo la prima parola (o le prime due se è nome+cognome)
            parole = nome.split()
            if len(parole) >= 2:
                return f"{parole[0]} {parole[1]}".title()
            elif len(parole) == 1:
                return parole[0].title()
    
    # fallback: ultima parola del testo
    return testo.split()[-1].title()

def interpreta_si_no(testo: str) -> str:
    testo = testo.lower().strip()
    
    si = ["sì", "si", "yes", "certo", "certamente", "ovviamente", "esatto",
          "va bene", "ok", "okay", "volentieri", "assolutamente", "certo che sì",
          "per favore", "dai", "perfetto", "esattamente"]
    
    no = ["no", "non voglio", "non mi interessa", "lascia perdere",
          "no grazie", "per ora no", "non ora", "nah", "neanche", "assolutamente no"]
    
    for parola in si:
        if parola in testo:
            return "si"
    
    for parola in no:
        if parola in testo:
            return "no"
    
    return "non capito"  # fallback