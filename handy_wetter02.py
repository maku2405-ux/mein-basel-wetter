def hole_fussball(team_suche):
    try:
        url = "https://api.openligadb.de/getmatchdata/ch1/2025"
        spiele = requests.get(url, timeout=5).json()
        
        # Wir drehen die Liste um (reversed), um das aktuellste Spiel zu finden
        for m in reversed(spiele):
            if team_suche in m["team1"]["teamName"] or team_suche in m["team2"]["teamName"]:
                # Wir suchen das Spiel, das zeitlich am nächsten an HEUTE liegt
                match_time = datetime.fromisoformat(m["matchDateTime"].replace('Z', ''))
                diff = match_time - datetime.now()
                
                # Wir nehmen Spiele von heute oder die nächsten anstehenden
                if diff.days >= -1: 
                    t1, t2 = m["team1"]["shortName"], m["team2"]["shortName"]
                    dt = m["matchDateTime"].split('T')
                    datum = dt[0].split('-')[2] + "." + dt[0].split('-')[1] + "."
                    uhrzeit = dt[1][:5]
                    
                    if m["matchResults"]:
                        r = m["matchResults"][-1]
                        return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2} (LIVE/Endstand)"
                    
                    prefix = "Heute" if datum == datetime.now().strftime("%d.%m.") else datum
                    return f"{prefix}: {t1} vs. {t2} ({uhrzeit} Uhr)"
        return "Kein Spiel gefunden"
    except: return "⚠️ Verbindung klemmt"
