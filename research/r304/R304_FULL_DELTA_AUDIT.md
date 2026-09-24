# R304 — полный diff первых 100 строк AIcrowd

Baseline R303: 2026-09-24T02:07:55.431Z UTC; снимок R304: 2026-09-24T02:36:19.062Z UTC.

Сверил все 100 строки R303 с 100 строками R304 по точной строке названия участника. Во всех 100 участниках совпадение; входов/выходов из первых 100 нет. Сравнены 8 общих колонок; в R304 дополнительные колонки графика и View не сравнивались.

Итог: 14 отображаемых строк отличаются: 1 изменение score, 4 сдвигов ранга/позиции, 9 изменения только относительной давности. Лидер J2W не изменился: ранг 01, отображаемый score 2.10e−9; точное значение не раскрыто.

| Участник | Категория | R303 → R304 |
|---|---|---|
| DO dogus_ozel — | relative_age_only | Sep 24, 01:18 49 min ago → Sep 24, 01:18 1 h ago |
| ME MeatProxy — | relative_age_only | Sep 23, 19:31 6 h ago → Sep 23, 19:31 7 h ago |
| SM shiv_m Independent | relative_age_only | Sep 23, 12:28 13 h ago → Sep 23, 12:28 14 h ago |
| ER emanuel_ruzak University of Buenos Aires | relative_age_only | Sep 23, 16:13 9 h ago → Sep 23, 16:13 10 h ago |
| LU LuDoe — | relative_age_only | Sep 23, 06:34 19 h ago → Sep 23, 06:34 20 h ago |
| PT pricop_tudor Alexandru Ioan Cuza University of Iasi | rank_or_position_shift | позиция 26 / ранг 26 (▼3) → 27 / 27 (▼4); score 4.80e−9 |
| MD ES Hack2Publish 2 members | rank_or_position_shift | позиция 27 / ранг 26 (▲11) → 28 / 27 (▲10); score 4.80e−9 |
| DB drmohammad_banisalman — | rank_or_position_shift | позиция 28 / ранг 28 (▼4) → 29 / 29 (▼5); score 4.90e−9 |
| SO sophie549 self study | rank_or_position_shift | позиция 29 / ранг 28 (▼4) → 30 / 29 (▼5); score 4.90e−9 |
| AN AndreasHad04 — | scored_entry_update | позиция 30 / ранг 28 (4.90e−9, MSE 2.12e−8) → 26 / 25 (4.70e−9, MSE 2.00e−8); 231× → 241×; Sep 23, 12:15 13 h ago → Sep 24, 01:22 1 h ago |
| NE neopok919 — | relative_age_only | Sep 23, 08:27 17 h ago → Sep 23, 08:27 18 h ago |
| ZR ze_rong — | relative_age_only | Sep 23, 19:11 6 h ago → Sep 23, 19:11 7 h ago |
| AK artiem_kuznietsov — | relative_age_only | Sep 23, 20:21 5 h ago → Sep 23, 20:21 6 h ago |
| AA aamir_abdul_azeez — | relative_age_only | Sep 24, 00:11 1 h ago → Sep 24, 00:11 2 h ago |

Полный снимок R304 (100 строк × 10 ячеек) сохранён отдельно в [R304_RAW_VISIBLE_ROWS.json](R304_RAW_VISIBLE_ROWS.json); нормализованные строки закреплены SHA-256 в [capture supplement receipt](R304_CAPTURE_SUPPLEMENT_RECEIPT.json).

Сравнение с R209/R223 не выводит gap или место: идентичность официальной visible‑50 панели и совместимость evaluator/meter по-прежнему не доказаны. Вне первых 100 строк данных нет. Это аудит уже сохранённых публичных снимков; новый опрос, benchmark, Actions, submission и изменения main/PR не выполнялись.
