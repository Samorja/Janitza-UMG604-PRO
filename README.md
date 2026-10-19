# Janitza UMG 604-PRO pre Home Assistant

Custom integrácia, ktorá číta namerané hodnoty z analyzátora siete **Janitza UMG 604-PRO** cez **Modbus TCP**. Nepotrebuje YAML konfiguráciu.

## Čo číta

Jedným Modbus dopytom (holding registre 19000–19121, float32) číta:

| Skupina | Entity |
|---|---|
| Napätie | L1-N, L2-N, L3-N, L1-L2, L2-L3, L3-L1 |
| Prúd | L1, L2, L3, súčet |
| Činný výkon | L1, L2, L3, súčet |
| Zdanlivý výkon | L1, L2, L3, súčet |
| Jalový výkon | L1, L2, L3, súčet |
| Účinník (cos φ) | L1, L2, L3 |
| Frekvencia | — |
| Činná energia | netto, odber, dodávka (kompatibilné s panelom Energia) |
| THD | napätie L1–L3, prúd L1–L3 |

> Adresy registrov vychádzajú z tabuľky „frequently required measured values“ pre UMG 604. Pred ostrým nasadením ich over v Modbus zozname adries pre svoj firmware.

## Inštalácia

### HACS (vlastný repozitár)
1. HACS → ⋮ → **Custom repositories** → pridaj `https://github.com/Samorja/Janitza-UMG604-PRO`, kategória **Integration**.
2. Nainštaluj **Janitza UMG 604-PRO** a reštartuj Home Assistant.

### Ručne
Skopíruj priečinok `custom_components/janitza_umg604` do `config/custom_components/` a reštartuj Home Assistant.

## Nastavenie
**Nastavenia → Zariadenia a služby → Pridať integráciu → Janitza UMG 604-PRO**, potom zadaj:

- **Adresa**: IP adresa analyzátora
- **Port**: `502`
- **Modbus adresa zariadenia**: `1`

Interval čítania (predvolene 10 s) zmeníš v **Možnostiach** integrácie.

## Vývoj
- `custom_components/janitza_umg604/api.py`: Modbus klient (pymodbus)
- `coordinator.py`: periodické čítanie bloku registrov
- `sensor.py`: definície senzorov a adresy registrov
- `config_flow.py`: nastavenie cez UI a možnosti
