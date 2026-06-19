"""
Sample plaintext German military messages from the WWII era (1939-1945).

Intended as realistic plaintext inputs for the Enigma simulator / cipher work.
These are period-authentic in phrasing (Wehrmacht / Kriegsmarine / Luftwaffe
style) and meant as plaintext to be enciphered.

Each entry is a dict with:
  - "text":   the German plaintext
  - "source": what the message represents

Spelling reflects mid-20th-century German military usage. If you need a strict
Enigma alphabet you will typically transliterate ae/oe/ue/ss and strip spaces
and punctuation before enciphering.
"""

MESSAGES = [
    {
        "text": (
            "AN ALLE GRUPPEN FEINDLICHER GELEITZUG GESICHTET QUADRAT "
            "ALPHA FUENF ZWEI KURS NORDOST GESCHWINDIGKEIT ACHT KNOTEN "
            "ANGRIFF BEI EINBRUCH DER DUNKELHEIT"
        ),
        "source": "Kriegsmarine, U-Boot Rudeltaktik Funkspruch",
    },
    {
        "text": (
            "WETTERBERICHT FUER HEUTE FRUEH HIMMEL BEDECKT WIND AUS "
            "WESTSUEDWEST STAERKE VIER SICHT ZEHN KILOMETER LEICHTER "
            "REGEN AM NACHMITTAG ERWARTET"
        ),
        "source": "Wetterfunkstelle, taeglicher Wetterbericht",
    },
    {
        "text": (
            "OBERKOMMANDO MELDET EIGENE PANZERVERBAENDE HABEN DEN "
            "FLUSSUEBERGANG ERZWUNGEN BRUECKENKOPF GEHALTEN NACHSCHUB "
            "AN TREIBSTOFF UND MUNITION DRINGEND ERFORDERLICH"
        ),
        "source": "Heer, Lagemeldung an das Oberkommando",
    },
    {
        "text": (
            "AN DIVISION FEINDLICHE BOMBER IM ANFLUG AUS RICHTUNG "
            "WESTEN HOEHE VIERTAUSEND METER FLAK FEUERBEREIT JAEGER "
            "ZUR ABWEHR ANGEFORDERT"
        ),
        "source": "Luftwaffe, Luftlagemeldung der Flak",
    },
    {
        "text": (
            "BEFEHL AN ALLE EINHEITEN ANGRIFF BEGINNT MORGEN FUNF UHR "
            "FUENFZEHN NACH ARTILLERIEVORBEREITUNG INFANTERIE FOLGT "
            "DEN PANZERN ZIEL HOEHENZUG OESTLICH DER ORTSCHAFT"
        ),
        "source": "Heer, Angriffsbefehl an die Frontverbaende",
    },
    {
        "text": (
            "U BOOT MELDET ZWEI FRACHTER VERSENKT GESAMTTONNAGE "
            "VIERZEHNTAUSEND TORPEDOS VERBRAUCHT VIER VERBLEIBEND "
            "ZWEI MARSCHIERE ZURUECK ZUM STUETZPUNKT BREST"
        ),
        "source": "Kriegsmarine, Erfolgsmeldung U-Boot",
    },
    {
        "text": (
            "FUNKSPRUCH AN HAUPTQUARTIER NACHSCHUBWEG DURCH "
            "FEINDLICHE LUFTANGRIFFE UNTERBROCHEN UMLEITUNG UEBER "
            "DEN SUEDLICHEN VERSORGUNGSPUNKT EINGELEITET"
        ),
        "source": "Etappendienst, Nachschubmeldung",
    },
    {
        "text": (
            "AUFKLAERUNG MELDET STARKE FEINDLICHE TRUPPENBEWEGUNGEN "
            "ENTLANG DER KUESTENSTRASSE PANZER UND ARTILLERIE "
            "VERMUTET ANGRIFF AUF UNSERE STELLUNGEN BEI TAGESANBRUCH"
        ),
        "source": "Heer, Aufklaerungsmeldung an den Divisionsstab",
    },
    {
        "text": (
            "AN OBERKOMMANDO DER WEHRMACHT STELLUNG WIRD UNTER "
            "SCHWEREM FEUER GEHALTEN VERLUSTE HOCH VERSTAERKUNG "
            "UND LUFTUNTERSTUETZUNG SOFORT ERBETEN"
        ),
        "source": "Heer, dringende Lagemeldung von der Front",
    },
    {
        "text": (
            "WETTERLAGE FUER DEN KANAL VERSCHLECHTERT SICH STURM "
            "AUS NORDWEST STAERKE ACHT SEEGANG HOCH ALLE BOOTE "
            "BLEIBEN VORERST IM HAFEN"
        ),
        "source": "Kriegsmarine, Wettermeldung fuer den Aermelkanal",
    },
    {
        "text": (
            "BEFEHL ZURUECKZIEHEN AUF DIE ZWEITE VERTEIDIGUNGSLINIE "
            "BRUECKEN NACH UEBERGANG SPRENGEN NACHHUT DECKT DEN "
            "RUECKZUG VERBINDUNG ZUM NACHBARREGIMENT HALTEN"
        ),
        "source": "Heer, Rueckzugsbefehl an die Regimenter",
    },
    {
        "text": (
            "AN ALLE FLIEGERHORSTE EINSATZBEREITSCHAFT HERSTELLEN "
            "ANGRIFF AUF FEINDLICHE NACHSCHUBLINIEN BEI MORGENGRAUEN "
            "JEDE MASCHINE VOLL BEWAFFNEN UND BETANKEN"
        ),
        "source": "Luftwaffe, Einsatzbefehl an die Geschwader",
    },
]

# Convenience: just the plaintext strings, in case you only want the texts.
PLAINTEXTS = [m["text"] for m in MESSAGES]


if __name__ == "__main__":
    for i, m in enumerate(MESSAGES, 1):
        print(f"[{i:02d}] {m['source']}")
        print(f"      {m['text']}")
        print()
