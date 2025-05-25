# mKast Game Launcher - Snelstartgids

## Overzicht

mKast is een aanpasbare game launcher met een retro arcade-stijl interface. Hiermee kun je al je games organiseren en starten vanuit één aantrekkelijk overzicht met ondersteuning voor:

- Automatische extractie van game-iconen uit EXE-bestanden  
- Aangepaste pixelart-afbeeldingen en geanimeerde GIFs  
- Rasterindeling die zich aanpast aan je schermresolutie  
- Admin-modus voor het toevoegen/bewerken van games  
- Wachtwoordbeveiliging om ongeautoriseerde afsluiting te voorkomen  

## Installatie

1. **Installeer de benodigde pakketten**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Dit installeert:
   - pygame: Voor grafische weergave en gebruikersinterface
   - pillow: Voor beeldverwerking
   - pywin32: Voor Windows API-toegang voor icoonextractie

2. **Alternatieve handmatige installatie**:
   ```bash
   pip install pygame
   pip install pillow
   pip install pywin32
   ```

## Aan de slag

1. **Start de launcher**:
   ```bash
   python main.py
   ```
   
   Of met een aangepast games-bestand:
   ```bash
   python main.py games_demo.json
   ```
   
   Of met de -g optie:
   ```bash
   python main.py -g games_demo.json
   ```

2. **Standaard wachtwoorden**:
   - Admin-modus: `admin123`
   - Afsluiten: `exit123`
   
   Deze kunnen worden aangepast in het bestand `config.json`.

3. **Games toevoegen**:
   - Klik op "Admin" en voer het admin-wachtwoord in
   - Klik op "Add New Game"
   - Selecteer een uitvoerbaar bestand (.exe)
   - Voer een naam en beschrijving in
   - Kies of je een aangepaste afbeelding wilt gebruiken of het icoon uit de EXE wilt halen

4. **Games starten**:
   - Klik op een game in het raster
   - Klik op de knop "Launch" om het spel te starten
   - De launcher minimaliseert terwijl het spel draait

## Configuratie

Het bestand `config.json` bevat instellingen die je kunt aanpassen:

```json
{
    "admin_password": "admin123",
    "exit_password": "exit123",
    "fullscreen": true,
    "resolution": [1920, 1080],
    "theme": {
        "background_color": [10, 10, 40],
        "button_color": [80, 80, 200],
        "button_hover_color": [120, 120, 255],
        "text_color": [255, 255, 255],
        "header_color": [255, 200, 0]
    }
}
```

- Zet `"fullscreen": false` om in venstermodus te draaien  
- Pas kleuren aan via de RGB-waarden in `theme`  
- Wijzig wachtwoorden voor extra beveiliging

De resolutie wordt automatisch gedetecteerd bij het opstarten. Je kunt ook deze opdracht gebruiken om de resolutie opnieuw te detecteren:
```bash
python main.py --update-resolution
```

## Aangepaste Pixelart

Voor de beste visuele ervaring kun je aangepaste pixelart gebruiken:

1. **Statische afbeeldingen**: Gebruik PNG-formaat met een aanbevolen formaat van 200x200 pixels  
2. **Animaties**: Gebruik GIF-formaat met 4–8 frames voor een retro gevoel  
3. **Gedetailleerde handleidingen**:
   - Zie `assets/README.md` voor instructies over het toevoegen van afbeeldingen  
   - Zie `assets/PIXELART_GUIDE.md` voor het maken van je eigen pixelart  

## Demo-inhoud

Probeer het bestand `games_demo.json` om voorbeelden te zien met geanimeerde GIFs:

```bash
python main.py -g games_demo.json
```

Of kopieer de demo-afbeeldingen naar je normale gameslijst.

## Tips & Tricks

1. **Aangepaste lettertypes**: Plaats een pixellettertype met de naam `pixel.ttf` in de map `assets/fonts`  
2. **Prestaties**: Als animaties traag zijn, gebruik dan PNG’s in plaats van GIFs  
3. **Games organiseren**: Je kunt ook direct het bestand `games.json` bewerken  
4. **Schaalbaarheid scherm**: Het raster past zich automatisch aan jouw schermresolutie aan  

## Sneltoetsen

- `ESC`-toets: Verlaat admin-modus (alleen wanneer je in admin-modus bent)  
- Alle andere manieren van afsluiten zijn wachtwoordbeveiligd, zoals bij arcade-machines

## Problemen oplossen

Als je tegen problemen aanloopt:
1. Controleer of alle benodigde Python-bibliotheken zijn geïnstalleerd (`pip install -r requirements.txt`)
2. Controleer of de bestandslocaties in `games.json` juist zijn
3. Zorg dat de `assets`-mappen bestaan en de juiste rechten hebben
4. Als er een foutmelding verschijnt over ontbrekende modules, zorg dan dat alle benodigde pakketten zijn geïnstalleerd

## Credits

De mKast Game Launcher maakt gebruik van:
- Pygame voor grafische weergave en UI  
- PIL/Pillow voor beeldverwerking  
- Pixel Emulator-lettertype van Genshichi Yasui
- Pywin32 voor Windows API-toegang

De applicatie gebruikt een modulaire structuur voor betere onderhoudbaarheid:
- `src/core/`: Kernfunctionaliteit
- `src/ui/`: UI-componenten
- `src/utils/`: Hulpfuncties