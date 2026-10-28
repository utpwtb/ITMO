# Lab 2 execution progress

Updated 2026-10-28 (Europe/Moscow).

## P0 complete
- Plans/contracts and both assignments read; original Git changes saved in git-status-before.txt; no reset/staging.
- Helios FreeBSD 14.5, Java 21.0.4, Maven 3.8.4, PostgreSQL 18.3; default READ COMMITTED. No existing Lab 1 movie-key duplicates (helios-baseline-raw.txt).
- Original server baseline fails due to missing movies-helios-test PU (baseline-server-test.txt); existing Lab 1 tables/processes preserved.

## P1–P5 implemented; end-to-end verification in progress
- Strict Jackson UTF-8 parser/DTO, exact integers, all-level whitelists/duplicate properties; fixtures and import-format.md.
- USER/ADMIN, ImportOperation, idempotent 003 migration, explicit Instant converter, all local/Helios/test mappings.
- Shared CRUD/import uniqueness and domain validation under AppState lock; one transaction per file; independent history commits; SQLSTATE handling/uncertain-commit lookup.
- Multipart endpoint, owner/admin history APIs; Russian/Chinese import/history UI, raw File upload, independent history refresh.
- Helios source-only archive/manifest transport and isolated deployment scripts; test candidate listening 127.0.0.1:40797; local tunnel 18083 (exec session 87688).

## P6 in progress
- Server Maven clean verify: 139 tests, zero failures/errors/skips, BUILD SUCCESS (candidate-server-test.txt; remote candidate/build-test.log + Surefire).
- Actual business isolation READ COMMITTED and 200ms lock timeout measured (217ms, SQLSTATE55P03).
- Migration twice on independent copy of 32 Lab1 movies / 3 accounts: counts and fingerprints preserved; all roles USER (migration-pilot.txt).
- HTTP functional checks: 17 passed on Helios; real media/size/CSRF/role/history checks (remote candidate/http-functional.json).
- Browser via tunnel: real File chooser upload succeeds, duplicate rejected, owner-only history and Chinese labels observed; screenshots in browser/.
- JMeter 5.6.3 installed on Helios. C03 pilot: 2 rounds x10, exactly2 commits+18 expected409, no residue/duplicates/JTL failures.
- Initial C01 harness assumed initial @Version=0; actual EclipseLink starts at1. Fixed assertion to initialVersion+1; must rerun formal A suite. This was a harness failure, not a claimed pass.

## Next
Finish browser dual-session/stale-form checks; run all C01–C12 (C02 delete variant included), compare SERIALIZABLE with same WAR/lock and final READ COMMITTED rerun. Deploy same verified WAR to production lab2_4101_ tables; restart/persistence smoke. Download raw results, write ACCEPTANCE/isolation analysis, final README, UML and Russian report/PDF. Server unexecuted items must remain unpassed until actual evidence exists.


## Update after final server build and initial isolation comparison
- User correction: final Web must be Russian only, no top variant number. Removed switch/dictionary and top4101/title4101; translated served format guide to Russian. Older Chinese screenshots are historical/superseded.
- Final Java clean verify on Helios:140 tests,0 failures/errors/skips (final/build-test.log and Surefire); final Java includes MovieKey use and accurate person-role paths.
- Browser stale form: second session wins, old draft preserved by polling, old save rejected; screenshot browser/stale-edit-conflict.png. Admin/owner history observed separately.
- All13 C01–C12 variants x20 rounds passed in read-committed-A2 and controlled-RC-A. Controlled fixed private test-table snapshot retained for level comparisons.
- SERIALIZABLE with same global lock and retry limit3: C05 produced an unexpected failure after9 commits/1 failure in first round; JMeter stopped group, unexecuted rounds are NOT passes. Raw logs retained. Other C scenes still being collected.
- Remaining: repackage final Russian guide (prove compiled Java hashes unchanged), full final-WAR RC/SERIALIZABLE controlled comparison, formal lab2_4101_ deployment/restart/browser, evidence download and final report/index.
