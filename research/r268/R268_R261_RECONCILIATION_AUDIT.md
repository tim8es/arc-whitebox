# R268 — независимая сверка реконcиляции R261

Дата проверки: 2026-09-23. Статус: COMPLETE; проверка только по Git-артефактам и журналу управления.

## Итог

Научное решение R261 — SCIENTIFIC_REJECT до запуска кандидата — подтверждается исходным отчётом и событием finish. Исходный пакет содержит дефект целостности: receipt указывает не тот Git blob отчёта. Координаторская reconciliation note фиксирует расхождение корректно; исходные файлы и события не переписывались.

## Проверенные факты

- `research/r261/R261_TARGET_FREE_NO_GO.md`, commit `933d259ec33c37c88f98df8c214935d02d8b60ca`: фактический blob `835eee8021cfc8760c50c1b6978dcdabf2e52a2e`.
- `research/r261/R261_RECEIPT.json`, commit `c7d0e98a413c0e4fc4e462d7aa65d8eeaae42f66`: поле `report_blob` содержит `84df1b3ecbc86c4564a0c29148e49cf57a9a4528`; оно не совпадает с фактическим blob.
- Пересчитанный SHA-256 исходного receipt: `dabaa077c1eb70a4f5cf89355e8e262bf555e2ce1f23ac308de457b588885e8e`.
- Append-only события R261 сохранены: start revision 288 не содержит `code_commit`; finish revision 289 не содержит `receipt.sha256`. Finish фиксирует SCIENTIFIC_REJECT и commit/URL receipt.
- Координаторская note `research/r261/R261_COORDINATOR_RECONCILIATION.json`, commit `9dfb89faeb33617da2f5ca91d32fa776426e228b`, указывает фактический/заявленный blob, оба пробела в событиях и пересчитанный хэш receipt.
- Источник `dff3dd65e9d2210e02418cca99e05556f6bf2c75` реконструируется по нормализованной записи R209 V25, а не из события start. Текущая проекция state.json это отражает; считать этот SHA полем исходного события нельзя.
- В исходном отчёте, receipt и reconciliation note совпадает ключевой научный вывод: кандидат не запускался; 0 локальных запусков, 0 Actions, 0 public accesses, без оплаты и отправки решения.

## Согласованность очереди и остаточное расхождение

На `research/control-v2`, revision 322, проекция state.json помечает R261 как SCIENTIFIC_REJECT; её результат согласуется с событием finish revision 289 и reconciliation note. История не подменена.

Однако `research/control/STATUS.md` не синхронизирован с state.json: строка R265 всё ещё показывает RUNNING, тогда как state.json и finish event revision 305 показывают SCIENTIFIC_REJECT. Строка R268 пока RUNNING ожидаемо, так как этот аудит ещё не был закрыт на момент снимка. R268 фиксирует эту рассинхронизацию как отдельный незакрытый bookkeeping-дефект; R261 данные не редактировались.

## Границы проверки

Только чтение Git-артефактов/состояния и пересчёт receipt hash. Научные вычисления, Actions, публичные/закрытые данные, платные ресурсы, отправка решения, leaderboard и канонические файлы не затрагивались.