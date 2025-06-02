
# Aplikace pro kontrolu naměřených hodnot elektrospotřebičů v PDF

## Popis projektu
Tato desktopová aplikace byla vytvořena za účelem zrychlení a zefektivnění opakovaných testů elektrospotřebičů.  
Automaticky načítá soubory PDF s výsledky měření a analyzuje jejich obsah podle stanovených limitů pro hodnoty jako jsou Rpe, RisoM-PE, IaltEq, IdirTouch a napětí SELV/PELV.  
Výstup je zobrazen přehledně s využitím ikon pro snadnou orientaci.

## Použité technologie
- Programovací jazyk: **Python 3**
- GUI: **Tkinter**
- Práce s PDF: **PyMuPDF (fitz)**
- Regulární výrazy: `re` modul
- Testování: `unittest` + manuální testování

## Testování
Aplikace byla otestována jak pomocí unit testů, tak i manuálního testování podle připravených testovacích scénářů a testovacích případů (test case).  
Unit testy testují funkčnost analyzátoru PDF (`analyze_pdf`) pomocí mockovaných vstupů.  
Manuální testování probíhalo podle dokumentace, která zahrnuje testování GUI, uživatelských akcí a chování při chybách.


## Cíl aplikace
Cílem této aplikace je usnadnit elektrotechnikům a revizním pracovníkům kontrolu naměřených hodnot z elektrospotřebičů bez nutnosti ručního pročítání PDF zpráv.  
Díky přehlednému výstupu a automatické analýze lze výrazně zrychlit celý proces kontroly a minimalizovat riziko lidské chyby.

## Autor
**Zdeněk Borovec** 
Aplikace byla vytvořena jako součást osobního rozvoje v oblasti Pythonu, GUI aplikací a testování, přičemž je plně využitelná pro rychlou a efektivní kontrolu naměřených hodnot u elektrospotřebičů při opakovaných zkouškách a revizích.