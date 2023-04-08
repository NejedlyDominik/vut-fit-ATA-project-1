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

| `pocet_slotu_ch` | Počet slotů vozíku |
| :--------------: | ------------------ |
| 1 |  |
| 2 |  |
| 3 |  |

| `max_nosnost_ch` | Maximální nosnost vozíku |
| :--------------: | ------------------------ |
| 1 |  |
| 2 |  |
| 3 |  |

    - `max_nosnost_ch.1 -> !pocet_slotu_ch.1`
    - `max_nosnost_ch.3 -> !pocet_slotu_ch.3`

| `pocet_pozadavku_ch` | Celkový počet naplánovaných požadavků |
| :------------------: | ------------------------------------- |
| 1 |  |
| 2 |  |

| `pocet_stanic_na_trase_ch` | Celkový počet různých stanic na trase alespoň jednoho požadavku (včetně počáteční a cílové) |
| :------------------------: | ------------------------------------------------------------------------------------------- |
| 1 |  |
| 2 |  |
| 3 |  |

| `vaha_prekracuje_nosnost_ch` | Váha alespoň jednoho požadavku překračuje maximální nosnost vozíku (`vaha_pozadavku > max_nosnost`) |
| :--------------------------: | --------------------------------------------------------------------------------------------------- |
| 1 |  |
| 2 |  |

| `vaha_neprekracuje_nosnost_ch` | Váha alespoň jednoho požadavku nepřekračuje maximální nosnost vozíku (`vaha_pozadavku <= max_nosnost`) |
| :----------------------------: | ------------------------------------------------------------------------------------------------------ |
| 1 |  |
| 2 |  |

    - `(vaha_prekracuje_nosnost_ch.1 and vaha_neprekracuje_nosnost_ch.1) -> pocet_pozadavku_ch.2`
    - `vaha_prekracuje_nosnost_ch.2 -> vaha_neprekracuje_nosnost_ch.1`
    - `vaha_neprekracuje_nosnost_ch.2 -> vaha_prekracuje_nosnost_ch.1`

| `vice_pozadavku_stejny_cas_ch` | Alespoň 2 požadavky jsou naplánovány na stejný čas |
| :----------------------------: | -------------------------------------------------- |
| 1 |  |
| 2 |  |

    - `vice_pozadavku_stejny_cas_ch.1 -> pocet_pozadavku_ch.2`

| `vice_pozadavku_stejna_start_stan_ch` | Alespoň 2 požadavky jsou naplánovány ze stejné počáteční stanice |
| :-----------------------------------: | ---------------------------------------------------------------- |
| 1 |  |
| 2 |  |

    - `vice_pozadavku_stejna_start_stan_ch.1 -> pocet_pozadavku_ch.2`

| `vice_pozadavku_stejna_cil_stan_ch` | Alespoň 2 požadavky jsou naplánovány do stejné cílové stanice |
| :---------------------------------: | ------------------------------------------------------------- |
| 1 |  |
| 2 |  |

    - `vice_pozadavku_stejna_cil_stan_ch.1 -> pocet_pozadavku_ch.2`

## Kombinace všech dvojic bloků

K vytvoření kombinací byl využit nástroj: [Combine](https://combine.testos.org/). Výsledná konfigurace pro tento nástroj se nachází v souboru `combine.json`.

### Tabulka kombinací všech dvojic bloků (screenshot z nástroje [Combine](https://combine.testos.org/))

![Výsledná tabulka kombinací všech dvojic bloků](combine-table.png "Výsledná tabulka kombinací všech dvojic bloků")
