#!/bin/bash

UNZIP="$(cd "$(dirname "$0")/../commits/unzip" && pwd)"
WORK="$(cd "$(dirname "$0")" && pwd)/hg_repo"

rm -rf "$WORK"
mkdir -p "$WORK"
cd "$WORK"

hg init

# r0: default (Red user)
cp "$UNZIP/commit0/"* .
hg addremove
hg commit -u "Red User <red@example.com>" -m "r0: initial commit"

# r1: branch1 (Blue user)
hg branch branch1
cp "$UNZIP/commit1/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r1: commit on branch1"

# r2: default (Red user)
hg update default
cp "$UNZIP/commit2/"* .
hg addremove
hg commit -u "Red User <red@example.com>" -m "r2: commit on default"

# r3: branch1 (Blue user)
hg update branch1
cp "$UNZIP/commit3/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r3: commit on branch1"

# r4: branch2 from branch1 (Blue user)
hg branch branch2
cp "$UNZIP/commit4/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r4: commit on branch2"

# r5: branch1 (Blue user)
hg update branch1
cp "$UNZIP/commit5/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r5: commit on branch1"

# r6: branch3 from branch1 (Blue user)
hg branch branch3
cp "$UNZIP/commit6/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r6: commit on branch3"

# r7: branch3 (Blue user)
cp "$UNZIP/commit7/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r7: commit on branch3"

# r8: branch4 from branch3 (Red user)
hg branch branch4
cp "$UNZIP/commit8/"* .
hg addremove
hg commit -u "Red User <red@example.com>" -m "r8: commit on branch4"

# r9: branch3 (Blue user)
hg update branch3
cp "$UNZIP/commit9/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r9: commit on branch3"

# r10: branch1 (Blue user)
hg update branch1
cp "$UNZIP/commit10/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r10: commit on branch1"

# r11: merge branch1 -> branch3 (Blue user)
hg update branch3
hg merge --tool internal:merge branch1
cp "$UNZIP/commit11/"* .
hg addremove
hg resolve -a -m
hg commit -u "Blue User <blue@example.com>" -m "r11: merge branch1 -> branch3"

# r12: branch5 from branch3 (Blue user)
hg branch branch5
cp "$UNZIP/commit12/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r12: commit on branch5"

# r13: branch5 (Blue user)
cp "$UNZIP/commit13/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r13: commit on branch5"

# r14: branch3 (Blue user)
hg update branch3
cp "$UNZIP/commit14/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r14: commit on branch3"

# r15: branch6 from branch3 (Blue user)
hg branch branch6
cp "$UNZIP/commit15/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r15: commit on branch6"

# r16: branch6 (Blue user)
cp "$UNZIP/commit16/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r16: commit on branch6"

# r17: branch5 (Blue user)
hg update branch5
cp "$UNZIP/commit17/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r17: commit on branch5"

# r18: branch2 (Blue user)
hg update branch2
cp "$UNZIP/commit18/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r18: commit on branch2"

# r19: merge branch2 -> branch4 (Red user)
hg update branch4
hg merge --tool internal:merge branch2
cp "$UNZIP/commit19/"* .
hg addremove
hg resolve -a -m
hg commit -u "Red User <red@example.com>" -m "r19: merge branch2 -> branch4"

# r20: merge branch4 -> branch5 (Blue user)
hg update branch5
hg merge --tool internal:merge branch4
cp "$UNZIP/commit20/"* .
hg addremove
hg resolve -a -m
hg commit -u "Blue User <blue@example.com>" -m "r20: merge branch4 -> branch5"

# r21: merge branch5 -> default (Red user)
hg update default
hg merge --tool internal:merge branch5
cp "$UNZIP/commit21/"* .
hg addremove
hg resolve -a -m
hg commit -u "Red User <red@example.com>" -m "r21: merge branch5 -> default"

# r22: branch3 (Blue user)
hg update branch3
cp "$UNZIP/commit22/"* .
hg addremove
hg commit -u "Blue User <blue@example.com>" -m "r22: commit on branch3"

# r23: merge branch3 -> branch6 (Blue user)
hg update branch6
hg merge --tool internal:merge branch3
cp "$UNZIP/commit23/"* .
hg addremove
hg resolve -a -m
hg commit -u "Blue User <blue@example.com>" -m "r23: merge branch3 -> branch6"

# r24: merge branch6 -> default (Blue user)
hg update default
hg merge --tool internal:merge branch6
cp "$UNZIP/commit24/"* .
hg addremove
hg resolve -a -m
hg commit -u "Blue User <blue@example.com>" -m "r24: merge branch6 -> default"

echo ""
echo "=== Done ==="

hg log --graph --template '{label("custom.rev", short(node))} - {label("custom.age", date|age)} {label("custom.desc", desc|firstline)} - {label("custom.author", author|person)}\n'