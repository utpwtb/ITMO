# Helios baseline — 2026-10-28

SSH host key verified against existing ~/.ssh/known_hosts. DPAPI PSCredential read in memory by bundled Python transport. No decrypted credential written to artifacts.

- FreeBSD 14.5-STABLE; s407960; /home/studs/s407960.
- OpenJDK21.0.4 (/usr/local/openjdk21), Maven3.8.4, PostgreSQL18.3, Python3.11.9; Payara Micro6.2025.1 copied from existing Lab1 runtime.
- Default java/mvn try an oversized heap and fail; explicit384MiB heap / ActiveProcessorCount2 used for actual server builds.
- Old Lab1 directory /home/studs/s407960/is-lab1-4101 and lab1_4101_ tables retained. Existing32 movies have zero (name,director_id) duplicate groups, including null.
- Original tests executed on server from baseline source copy: fail because movies-helios-test is missing. Evidence: baseline-server-test.txt and remote baseline/baseline-test.log. No claim of original green baseline.
- Lab2 isolated directory /home/studs/s407960/is-lab2-4101; HTTP loopback40797; local tunnel18083; database pg:5432/studs, schema s407960, production prefixlab2_4101_, test prefixlab2_4101_test_. No existing Lab2 resources were present at initial inspection.
- Migration validated on separate narrowly named lab2_4101_test_upgrade_ copies; twice applied, counts/fingerprints unchanged. See migration-pilot.txt and downloaded candidate/migration.json.

Raw inventories: helios-environment-raw.txt, helios-baseline-raw.txt. Original workspace changes: git-status-before.txt. No git reset/clean/staging/commit performed.
