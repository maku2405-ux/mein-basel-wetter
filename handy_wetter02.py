def hole_fussball(team_suche):
    try:
        # Wir laden alle Spiele der Saison 2025
        url = "https://api.openligadb.de/getmatchdata/ch1/2025"
        spiele = requests.get(url, timeout=5).json()
        
        # Wir suchen einfach das ERSTE Spiel in der Liste, das noch nicht fertig ist
        for m in spiele:
            t1 = m["team1"]["teamName"]
            t2 = m["team2"]["teamName"]
            
            if team_suche in t1 or team_suche in t2:
                # Sobald wir ein Spiel finden, das nicht beendet ist, nehmen wir es!
                if not m["matchIsFinished"]:
                    t1_s = m["team1"]["shortName"]
                    t2_s = m["team2"]["shortName"]
                    
                    # Datum hübsch machen
                    dt = m["matchDateTime"].split('T')
                    d_raw = dt[0].split('-')
                    datum = f"{d_raw[2]}.{d_raw[1]}."
                    uhrzeit = dt[1][:5]
                    
                    # Live-Check (falls Tore da sind)
                    if m["matchResults"]:
                        r = m["matchResults"][-1]
                        return f"{t1_s} {r['pointsTeam1']}:{r['pointsTeam2']} {t2_s} (LIVE)"
                    
                    # "Heute" Check
                    heute = datetime.now().strftime("%d.%m.")
                    prefix = "Heute" if datum == heute else datum
                    return f"{prefix}: {t1_s} vs. {t2_s} ({uhrzeit} Uhr)"
        
        return "Kein Spiel gefunden"
    except:
        return "⚠️ API Problem"
