# Naturalistic case: compact name and date groups in the Silver Vale

Use the loaded UsefulCharts-style skill to make an original educational family poster titled **Families of the Silver Vale** from the fictional records below. Compose it as a compact, readable chart with stable house colors, clear partnerships and descent, hierarchy between principal and supporting names, and enough context to find significant branches. All dates and relationships are invented demonstration data. Preserve every person's ID, name, known birth, death and house exactly. Houses are declared membership, including children of partners from different houses; do not derive a new category from a mixed marriage. Retain the generation as the row number in the editable source. Vertical spacing is schematic. Xavier's birth is unknown; do not estimate it.

Create exactly these deliverables: `result/source.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. Open the final PNG with an image-reading tool and repair visible problems. The final source should contain the complete editable composition. Clearly identify the data as fictional. Show lifespans beside names, using an explicit unknown-birth label for Xavier. Use clear light family colors and predominantly dark names. Keep the short name/date records compact, with distinct treatments for portraits and supporting relatives.

## People

| ID | Name | Birth | Death | House | Generation |
| --- | --- | --- | --- | --- | --- |
| p01 | Ada | 1790 | 1857 | Alder | 0 |
| p02 | Benoit | 1787 | 1860 | Birch | 0 |
| p03 | Celia | 1812 | 1870 | Alder | 1 |
| p04 | David | 1813 | 1894 | Birch | 1 |
| p05 | Elin | 1815 | 1884 | Alder | 1 |
| p06 | Felix | 1814 | 1881 | Cedar | 1 |
| p07 | Grace | 1823 | 1896 | Birch | 1 |
| p08 | Hugo | 1822 | 1880 | Dale | 1 |
| p09 | Iris | 1834 | 1915 | Alder | 2 |
| p10 | Jonas | 1837 | 1906 | Cedar | 2 |
| p11 | Klara | 1838 | 1905 | Alder | 2 |
| p12 | Leon | 1842 | 1915 | Dale | 2 |
| p13 | Mara | 1844 | 1902 | Birch | 2 |
| p14 | Nils | 1843 | 1924 | Birch | 2 |
| p15 | Opal | 1844 | 1913 | Cedar | 2 |
| p16 | Paul | 1846 | 1913 | Dale | 2 |
| p17 | Rhea | 1848 | 1921 | Cedar | 2 |
| p18 | Simon | 1848 | 1906 | Alder | 2 |
| p19 | Tessa | 1849 | 1930 | Dale | 2 |
| p20 | Ulric | 1846 | 1915 | Cedar | 2 |
| p21 | Vera | 1860 | 1927 | Alder | 3 |
| p22 | Walter | 1866 | 1939 | Dale | 3 |
| p23 | Xenia | 1868 | 1926 | Cedar | 3 |
| p24 | Yves | 1867 | 1948 | Cedar | 3 |
| p25 | Anya | 1871 | 1940 | Dale | 3 |
| p26 | Bruno | 1874 | 1941 | Alder | 3 |
| p27 | Cora | 1870 | 1943 | Birch | 3 |
| p28 | Dorian | 1875 | 1933 | Dale | 3 |
| p29 | Esme | 1877 | 1958 | Cedar | 3 |
| p30 | Finn | 1876 | 1945 | Birch | 3 |
| p31 | Greta | 1881 | 1948 | Alder | 3 |
| p32 | Henrik | 1879 | 1952 | Dale | 3 |
| p33 | Ilse | 1890 | 1948 | Alder | 4 |
| p34 | Jakob | 1894 | 1975 | Cedar | 4 |
| p35 | Kaia | 1898 | 1967 | Dale | 4 |
| p36 | Lucan | 1899 | 1966 | Alder | 4 |
| p37 | Mabel | 1900 | 1973 | Cedar | 4 |
| p38 | Noel | 1901 | 1959 | Dale | 4 |
| p39 | Orla | 1903 | 1984 | Alder | 4 |
| p40 | Pavel | 1905 | 1974 | Dale | 4 |
| p41 | Quinn | 1904 | 1971 | Birch | 4 |
| p42 | Rosa | 1903 | 1976 | Cedar | 4 |
| p43 | Soren | 1917 | 1975 | Alder | 5 |
| p44 | Thea | 1921 | 2002 | Cedar | 5 |
| p45 | Una | 1926 | 1995 | Dale | 5 |
| p46 | Viktor | 1928 | 1995 | Cedar | 5 |
| p47 | Willa | 1930 | 2003 | Birch | 5 |
| p48 | Xavier | unknown | 1958 | Dale | 5 |

## Partnerships and children

Each pair is a partnership, represented separately from its children. A person with no declared parents is an external family member, not a missing record. A partnership with no children terminates.

| ID | Partners | Children |
| --- | --- | --- |
| u01 | p01, p02 | p03, p05, p07 |
| u02 | p03, p04 | p09, p11, p13 |
| u03 | p05, p06 | p10, p15, p17 |
| u04 | p07, p08 | p12, p19 |
| u05 | p09, p10 | p21, p23 |
| u06 | p11, p12 | p22, p25 |
| u07 | p13, p14 | p27 |
| u08 | p15, p16 | p24, p29 |
| u09 | p17, p18 | p26, p31 |
| u10 | p19, p20 | p28 |
| u11 | p21, p22 | p33, p35 |
| u12 | p23, p24 | p34, p37 |
| u13 | p25, p26 | p36, p39 |
| u14 | p27, p28 | p38 |
| u15 | p29, p30 | p41 |
| u16 | p31, p32 | p40 |
| u17 | p33, p34 | p43, p44 |
| u18 | p35, p36 | p45 |
| u19 | p37, p38 | p46 |
| u20 | p39, p40 | none |
| u21 | p41, p42 | p47 |

The single additional relationship is **uncertain descent from p32 to p48**, ID `uncertain-xavier`. Use a distinct dotted treatment and explain it in the reading note. Do not attach Xavier to u16 or turn uncertainty into certainty.

## Context

Ada and Benoit are the recorded founding pair. Elin established the Cedar archive, Klara kept the Alder school, and Quinn established the Birch reading room. Give these three local landmarks clear but restrained emphasis, retaining exactly the short phrases **Cedar archive**, **Alder school**, and **Birch reading room** next to the relevant person. Their own declared houses remain unchanged. Use these three named places as larger serif captions beside their associated branches, with original symbols or emblems optically joined to the captions. Keep each caption linked in the editable source to the supplied place field on its named person. The captions must remain local, with clear ownership by the person's declared house. Explain that any invented devices are fictional. Use three bundled public-domain museum portrait samples as clearly disclosed decorative illustrations for the fictional Ada, Elin and Klara, and only these three people. Make those three records visible focal points through larger name-and-portrait groups, with subordinate dates. Retain each selected image's source identity; do not present it as a likeness of the invented person. Let the first few family units fan out enough to distinguish the focal branches while keeping the later families compact. Avoid forcing every generation across the full width.

The copied `skills/usefulcharts-style/` directory is read-only. Use only the loaded skill and normal local tools. Keep generated work inside this workspace and outside the copied skill. Do not inspect other repository files, sibling skills, Git history or remote resources.
