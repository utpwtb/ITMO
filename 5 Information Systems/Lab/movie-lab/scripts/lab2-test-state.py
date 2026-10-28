"""Snapshot/restore only the seven named Lab 2 test tables; refuses restore/drop while app runs."""
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
TABLES=['import_operation','movie','person','coordinates','location','app_state','app_user']
names=['s407960.lab2_4101_test_'+t for t in TABLES]
mode=sys.argv[1]
path=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'.runtime/comparison-baseline.dump'
if not path.is_relative_to(ROOT/'.runtime'):raise ValueError('Private dump must stay inside deployment .runtime')
os.umask(0o077)
if mode=='backup':
    args=['pg_dump','-h','pg','-U','s407960','-d','studs','-w','-Fc','-f',str(path)]
    for name in names:args+=['-t',name]
    subprocess.run(args,check=True);print('Private test snapshot saved; not included in evidence/source archives')
elif mode in ('drop','restore'):
    running=subprocess.run(['ps','-ww','-U','s407960','-o','command='],text=True,capture_output=True,check=True).stdout
    if any(str(ROOT/'.runtime/payara-micro-6.2025.1.jar') in line and '/bin/java' in line for line in running.splitlines()):
        sys.exit('Stop the candidate instance and wait for exit first')
    subprocess.run(['psql','-X','-h','pg','-U','s407960','-d','studs','-w','-v','ON_ERROR_STOP=1','-c','DROP TABLE IF EXISTS '+','.join(names)+';'],check=True)
    if mode=='restore':subprocess.run(['pg_restore','-h','pg','-U','s407960','-d','studs','-w','--exit-on-error','--no-owner',str(path)],check=True)
else:sys.exit('backup|restore|drop [.runtime/file.dump]')
