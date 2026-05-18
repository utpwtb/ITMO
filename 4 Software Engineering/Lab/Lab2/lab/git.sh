#!/bin/bash

UNZIP="$(cd "$(dirname "$0")/../commits/unzip" && pwd)"
WORK="$(cd "$(dirname "$0")" && pwd)/git_repo"

rm -rf "$WORK"
mkdir -p "$WORK"
cd "$WORK"

git init

# r0: master (Red user)
cp "$UNZIP/commit0/"* .
git add -A
git config user.name "Red User"
git config user.email "red@example.com"
git commit -m "r0: initial commit"

# r1: branch1 (Blue user)
git checkout -b branch1
cp "$UNZIP/commit1/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r1: commit on branch1"

# r2: master (Red user)
git checkout master
cp "$UNZIP/commit2/"* .
git add -A
git config user.name "Red User"
git config user.email "red@example.com"
git commit -m "r2: commit on master"

# r3: branch1 (Blue user)
git checkout branch1
cp "$UNZIP/commit3/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r3: commit on branch1"

# r4: branch2 from branch1 (Blue user)
git checkout -b branch2 branch1
cp "$UNZIP/commit4/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r4: commit on branch2"

# r5: branch1 (Blue user)
git checkout branch1
cp "$UNZIP/commit5/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r5: commit on branch1"

# r6: branch3 from branch1 (Blue user)
git checkout -b branch3 branch1
cp "$UNZIP/commit6/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r6: commit on branch3"

# r7: branch3 (Blue user)
cp "$UNZIP/commit7/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r7: commit on branch3"

# r8: branch4 from branch3 (Red user)
git checkout -b branch4 branch3
cp "$UNZIP/commit8/"* .
git add -A
git config user.name "Red User"
git config user.email "red@example.com"
git commit -m "r8: commit on branch4"

# r9: branch3 (Blue user)
git checkout branch3
cp "$UNZIP/commit9/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r9: commit on branch3"

# r10: branch1 (Blue user)
git checkout branch1
cp "$UNZIP/commit10/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r10: commit on branch1"

# r11: merge branch1 -> branch3 (Blue user)
git checkout branch3
git config user.name "Blue User"
git config user.email "blue@example.com"
git merge branch1 --no-commit -m "r11: merge branch1 -> branch3" 
cp "$UNZIP/commit11/"* .
git add -A
git commit -m "r11: merge branch1 -> branch3"

# r12: branch5 from branch3 (Blue user)
git checkout -b branch5 branch3
cp "$UNZIP/commit12/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r12: commit on branch5"

# r13: branch5 (Blue user)
cp "$UNZIP/commit13/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r13: commit on branch5"

# r14: branch3 (Blue user)
git checkout branch3
cp "$UNZIP/commit14/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r14: commit on branch3"

# r15: branch6 from branch3 (Blue user)
git checkout -b branch6 branch3
cp "$UNZIP/commit15/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r15: commit on branch6"

# r16: branch6 (Blue user)
cp "$UNZIP/commit16/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r16: commit on branch6"

# r17: branch5 (Blue user)
git checkout branch5
cp "$UNZIP/commit17/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r17: commit on branch5"

# r18: branch2 (Blue user)
git checkout branch2
cp "$UNZIP/commit18/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r18: commit on branch2"

# r19: merge branch2 -> branch4 (Red user)
git checkout branch4
git config user.name "Red User"
git config user.email "red@example.com"
git merge branch2 --no-commit -m "r19: merge branch2 -> branch4" 
cp "$UNZIP/commit19/"* .
git add -A
git commit -m "r19: merge branch2 -> branch4"

# r20: merge branch4 -> branch5 (Blue user)
git checkout branch5
git config user.name "Blue User"
git config user.email "blue@example.com"
git merge branch4 --no-commit -m "r20: merge branch4 -> branch5" 
cp "$UNZIP/commit20/"* .
git add -A
git commit -m "r20: merge branch4 -> branch5"

# r21: merge branch5 -> master (Red user)
git checkout master
git config user.name "Red User"
git config user.email "red@example.com"
git merge branch5 --no-commit -m "r21: merge branch5 -> master" 
cp "$UNZIP/commit21/"* .
git add -A
git commit -m "r21: merge branch5 -> master"

# r22: branch3 (Blue user)
git checkout branch3
cp "$UNZIP/commit22/"* .
git add -A
git config user.name "Blue User"
git config user.email "blue@example.com"
git commit -m "r22: commit on branch3"

# r23: merge branch3 -> branch6 (Blue user)
git checkout branch6
git config user.name "Blue User"
git config user.email "blue@example.com"
git merge branch3 --no-commit -m "r23: merge branch3 -> branch6" 
cp "$UNZIP/commit23/"* .
git add -A
git commit -m "r23: merge branch3 -> branch6"

# r24: merge branch6 -> master (Blue user)
git checkout master
git config user.name "Blue User"
git config user.email "blue@example.com"
git merge branch6 --no-commit -m "r24: merge branch6 -> master" 
cp "$UNZIP/commit24/"* .
git add -A
git commit -m "r24: merge branch6 -> master"

echo ""
echo "=== Done ==="
git log --graph --abbrev-commit --decorate --date-order --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(auto)%d%C(reset)' --all
