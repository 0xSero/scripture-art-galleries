#!/usr/bin/env python3
"""Make the work counts on the three gallery pages follow the manifest.

The love gallery's manifest was trimmed from 50 works to 46, but its prose still
said fifty. These replacements derive every count from len(M) so the pages cannot
drift from the manifest again.
"""
FILES = {
    "/Users/sero/love-gallery/build.py": [
        ('content="Fifty public-domain works', 'content="{len(M)} public-domain works'),
        ('<p class="kicker">A gallery of classical art &middot; 50 public-domain works</p>',
         '<p class="kicker">A gallery of classical art &middot; {len(M)} public-domain works</p>'),
        ('<caption>All fifty plates in catalogue order', '<caption>All {len(M)} plates in catalogue order'),
        ('<p>All fifty reproductions are public domain', '<p>All {len(M)} reproductions are public domain'),
    ],
    "/Users/sero/friends-gallery/build.py": [
        ('content="Twenty-five public-domain works', 'content="{len(M)} public-domain works'),
        ('<p class="kicker">A gallery of classical art &middot; 25 public-domain works</p>',
         '<p class="kicker">A gallery of classical art &middot; {len(M)} public-domain works</p>'),
        ('<caption>All twenty-five plates in catalogue order', '<caption>All {len(M)} plates in catalogue order'),
        ('<p>All twenty-five reproductions are public domain', '<p>All {len(M)} reproductions are public domain'),
    ],
    "/Users/sero/parents-gallery/build.py": [
        ('content="Twenty-five public-domain works', 'content="{len(M)} public-domain works'),
        ('<p class="kicker">A gallery of classical art &middot; 25 public-domain works</p>',
         '<p class="kicker">A gallery of classical art &middot; {len(M)} public-domain works</p>'),
        ('<caption>All twenty-five plates in catalogue order', '<caption>All {len(M)} plates in catalogue order'),
        ('<p>All twenty-five reproductions are public domain', '<p>All {len(M)} reproductions are public domain'),
    ],
}

for path, edits in FILES.items():
    text = open(path).read()
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{path}: {n} matches for {old!r}")
        text = text.replace(old, new)
    open(path, "w").write(text)
    print("patched", path)
