# Dokumentace testů

Autor: Dominik Nejedlý (xnejed09)

## Graf přícin a důsledků (CEG)

K vytvoření grafu byl využit nástroj: [Ceg](http://ceg.testos.org/). Výsledná konfigurace pro tento nástroj se nachází v souboru `ceg.json`.

### Graf příčin a důsledů (screenshot z nástroje [Ceg](http://ceg.testos.org/))

![Graf příčin a důsledků (CEG)](ceg-graph.png "Graf příčin a důsledků (CEG)")

### Výsledná rozhodovací tabulka (screenshot z nástroje [Ceg](http://ceg.testos.org/))

![Výsledná rozhodovací tabulka](ceg-table.png "Výsledná rozhodovací tabulka")

## Identifikace vstupních parametrů

| Identifikátor     | Popis                                                          |
| :---------------: | -------------------------------------------------------------- |
| `pocet_slotu`     | Počet slotů vozíku                                             |
| `max_nosnost`     | Maximální nosnost vozíku                                       |
| `pocet_pozadavku` | Celkový počet naplánovaných požadavků                          |
| `start_stanice`   | Počáteční stanice požadavku (stanice, kde je materiál naložen) |
| `cil_stanice`     | Cílová stanice požadavku (stanice, kde je materiál vyložen)    |
| `vaha_pozadavku`  | Váha požadavku (váha meteriálu, který má být převezen)         |
| `cas_pozadavku`   | Naplánovaný čas vystavení požadavku                            |

## Charakteristiky parametrů

## Kombinace všech dvojic bloků

K vytvoření kombinací byl využit nástroj: [Combine](https://combine.testos.org/). Výsledná konfigurace pro tento nástroj se nachází v souboru `combine.json`.

### Tabulka kombinací všech dvojic bloků (screenshot z nástroje [Combine](https://combine.testos.org/))

![Výsledná tabulka kombinací všech dvojic bloků](combine-table.png "Výsledná tabulka kombinací všech dvojic bloků")
