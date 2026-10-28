# Helios environment verified 2026-10-28 (Europe/Moscow)

| Item | Actual value / evidence |
|---|---|
| Host / SSH | helios.cs.ifmo.ru, s407960, port 2222; existing known_hosts verified; DPAPI credential used only in memory |
| OS | FreeBSD 14.5-STABLE ec3ebfaf9fd3 amd64 |
| Project | /home/studs/s407960/is-lab2-4101 |
| Java | /usr/local/openjdk21, OpenJDK21.0.4+7-1 |
| Maven | /usr/local/share/java/maven, 3.8.4 |
| Python | python3.11, 3.11.9 |
| PostgreSQL client/server | 18.3; pg:5432/studs; schema s407960 |
| Payara | Micro6.2025.1, loopback HTTP40797, .runtime/payara.log |
| EclipseLink in JUnit | 4.0.5.v202412231137-a96b873527f305f932543045c8679bb1de8d3a43, final/build-test.log |
| EclipseLink in deployed Payara | 4.0.1.payara-p3.v202409231228, actual deployed transaction exception in initial-isolation/server-serializable.log; container parent loading differs from Maven |
| JMeter | Apache5.6.3, server-side tools/apache-jmeter-5.6.3; jmeter-install.txt |
| Database isolation | Default READ COMMITTED; actual Database.write + metadata connections measured by final JUnit; SERIALIZABLE explicitly configured for comparison and generated real serialization failures |
| Write protocol | AppState(id=1) PESSIMISTIC_WRITE before final reads/validation; client expected version + JPA @Version |
| Lock timeout | Default10000ms via SET LOCAL; JUnit override200ms actually raised55P03 in217ms on first successful run |
| Production / test tables | lab2_4101_ / lab2_4101_test_, seven entity tables each; narrow upgrade-copy tables removed after migration test |
| Private baseline snapshot | .runtime/comparison-baseline.dump, never included in source/evidence tar; same SHA256 checked for comparison groups |
| SSH tunnel | Local127.0.0.1:18083 to server127.0.0.1:40797; browser screenshots are of remote application |
| Original Lab1 | /home/studs/s407960/is-lab1-4101 and lab1_4101_ tables preserved; initial32 movies had no new-key conflicts |

Plain java/mvn initially failed because the server default heap was oversized. Actual build/test scripts constrain heap384MiB; JMeter uses256MiB. `quota` was unavailable in the initial shell; disk availability was checked with df in jmeter-install.txt. No claim is made that a user quota value was obtained.

Raw inventories and commands: helios-environment-raw.txt, helios-baseline-raw.txt, jmeter-install.txt, final-server-test.txt, comparison configuration.json/command.json and raw logs. Historical Lab1 deployment records are not counted as Lab2 results.
