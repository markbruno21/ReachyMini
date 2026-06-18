
DIALETTI = {
    "Piemonte":              "Cume stèje, car?",
    "Valle_d_Aosta":         "Coment ve lo?",
    "Lombardia":             "Fém dü ciàcher insema?",
    "Veneto":                "Cossa te gà in mente de belo?",
    "Trentino_Alto_Adige":   "Come stat, tut a post?",
    "Friuli_Venezia_Giulia": "Mandi, come va?",
    "Liguria":               "Cöse gh'æ da mangiâ de bon?",
    "Emilia_Romagna":        "Com'andela, vècia?",
    "Toscana":               "Oh, tu come stai oggi?",
    "Umbria":                "Com'è ita, oggi?",
    "Marche":                "Com'andemo, caru?",
    "Lazio":                 "Aò, come te senti oggi?",
    "Abruzzo":               "Comu stèje, cumparì?",
    "Molise":                "Che se dice de bello?",
    "Campania":              "Comm' è bell'a te vedè!",
    "Puglia":                "Comu stai, de mmi?",
    "Basilicata":            "Uè, com'è ita?",
    "Calabria":              "Comu va, picciottu?",
    "Sicilia":               "Comu staju, beddu?",
    "Sardegna":              "Cumente ses, caru?",
}

#funzione che prende in input ripsosta dell'utente (anche se dice una città) e restituisce la frase in dialetto corrispondente alla regione
def ottieni_regione(input_utente):
    testo=input_utente.lower()
    
    if "piemonte" in testo or "torino" in testo: 
        return DIALETTI["Piemonte"]  
        
    elif "valle d'aosta" in testo or "aosta" in testo: 
        return DIALETTI["Valle_d_Aosta"]
        
    elif "lombardia" in testo or "milano" in testo: 
        return DIALETTI["Lombardia"]
        
    elif "veneto" in testo or "venezia" in testo or "verona" in testo: 
        return DIALETTI["Veneto"]
        
    elif "trentino" in testo or "trento" in testo: 
        return DIALETTI["Trentino_Alto_Adige"]
        
    elif "friuli" in testo or "trieste" in testo or "udine" in testo: 
        return DIALETTI["Friuli_Venezia_Giulia"]
        
    elif "liguria" in testo or "genova" in testo: 
        return DIALETTI["Liguria"]
        
    elif "emilia" in testo or "romagna" in testo or "bologna" in testo: 
        return DIALETTI["Emilia_Romagna"]
        
    elif "toscana" in testo or "firenze" in testo: 
        return DIALETTI["Toscana"]
        
    elif "umbria" in testo or "perugia" in testo: 
        return DIALETTI["Umbria"]
        
    elif "marche" in testo or "ancona" in testo: 
        return DIALETTI["Marche"]
        
    elif "lazio" in testo or "roma" in testo: 
        return DIALETTI["Lazio"]
        
    elif "abruzzo" in testo or "pescara" in testo: 
        return DIALETTI["Abruzzo"]
        
    elif "molise" in testo or "campobasso" in testo: 
        return DIALETTI["Molise"]
        
    elif "campania" in testo or "napoli" in testo: 
        return DIALETTI["Campania"]
        
    elif "puglia" in testo or "bari" in testo: 
        return DIALETTI["Puglia"]
        
    elif "basilicata" in testo or "potenza" in testo: 
        return DIALETTI["Basilicata"]
        
    elif "calabria" in testo or "catanzaro" in testo: 
        return DIALETTI["Calabria"]
        
    elif "sicilia" in testo or "palermo" in testo: 
        return DIALETTI["Sicilia"]
        
    elif "sardegna" in testo or "cagliari" in testo: 
        return DIALETTI["Sardegna"]
        
    else:
        return "Complimenti. Che bel posto!"