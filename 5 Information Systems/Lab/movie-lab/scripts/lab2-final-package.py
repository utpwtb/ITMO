"""Repackage final Russian guide/assets on Helios; prove tested Java classes remain identical."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'verification/Lab2/final';out.mkdir(parents=True,exist_ok=True)
def classes():
    return {str(p.relative_to(ROOT/'target/classes')):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'target/classes').rglob('*.class'))}
before=classes()
env=os.environ.copy();env.update(JAVA_HOME='/usr/local/openjdk21',MAVEN_OPTS='-Xmx384m -XX:ActiveProcessorCount=2')
with (out/'final-assets-build.log').open('w') as log:
    subprocess.run(['mvn','-B','-ntp','-s','scripts/maven-settings.xml','-DskipTests','package'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
after=classes()
result={'testedJavaClassHashes':before,'packagedJavaClassHashes':after,'unchanged':bool(before) and before==after,
    'warSha256':hashlib.sha256((ROOT/'target/movie-lab.war').read_bytes()).hexdigest(),
    'note':'Only Russian format guide and delivery docs/assets changed after full 140-test clean verify; all C scenes must run on this WAR.'}
(out/'tested-classes-and-war.json').write_text(json.dumps(result,indent=2));print(json.dumps({'unchanged':result['unchanged'],'warSha256':result['warSha256']}))
if not result['unchanged']:sys.exit(1)
