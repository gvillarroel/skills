# Naturalistic case: contextual illustration composition

Use the loaded UsefulCharts-style skill to create an original, polished educational poster titled **Three Regions of the Valen Coast**. All data below is fictional. Show 1800–2000 on one numeric year scale, three stable region colors, simultaneous periods, and the explicit divisions/unions. Use a selective mixture of fine duration stems with local name capsules for quiet continuities and broader duration bands for principal periods. Keep exact dates readable from the full stems, not the name capsules. Use clear horizontal event notes, deliberate hierarchy, and three contextual drawings: a clock mechanism for the clockmaking schools, a bridge for the road survey, and a stagecoach beside the discussion of winter roads. Identify these as explanatory images rather than evidence of the invented events. Let the images form readable local groups with their notes; use at least two different relative placements, including one beside its prose. Keep complete image silhouettes at a useful size. Allocate unequal regional widths when the actual concurrent histories need that space; avoid making every period look alike. The composition should read as an educational wall chart with enough space to follow the relationships. Keep every supplied name, date, event note and relationship exactly; preserve all real gaps between periods. Widths do not encode population or territorial area.

Create these exact files: `result/source.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. Inspect the final PNG with an image-reading tool and repair any visible problems. State that the data is fictional in the poster. Do not invent people, periods or events.

## Periods

| ID | Region | Name | Start | End |
| --- | --- | --- | --- | --- |
| c1 | Coast | Council of Harbors | 1800 | 1860 |
| c2 | Coast | Port Authority | 1865 | 1910 |
| c3 | Coast | Merchant Guild | 1865 | 1930 |
| c4 | Coast | Coastal Assembly | 1950 | 2000 |
| h1 | Hills | Highland Estates | 1800 | 1880 |
| h2 | Hills | Eastern County | 1890 | 1940 |
| h3 | Hills | Western County | 1890 | 1960 |
| h4 | Hills | Hill Federation | 1970 | 2000 |
| p1 | Plains | Field Councils | 1800 | 1850 |
| p2 | Plains | Road Council | 1810 | 1870 |
| p3 | Plains | Land Union | 1880 | 1935 |
| p4 | Plains | Civic League | 1945 | 2000 |

## Explicit relationships

- Divisions: `c1 -> c2`, `c1 -> c3`, `h1 -> h2`, `h1 -> h3`.
- Unions: `c2 -> c4`, `c3 -> c4`, `h2 -> h4`, `h3 -> h4`, `p1 -> p3`, `p2 -> p3`.
- Succession: `p3 -> p4`.

## Dated events

| ID | Region | Year | Heading | Note |
| --- | --- | --- | --- | --- |
| ec1 | Coast | 1808 | Harbor surveys | Pilots mark the safe channels. |
| ec2 | Coast | 1820 | Clockmaking schools | Workshops teach the anchor escapement. |
| ec3 | Coast | 1852 | Common harbor dues | Ports agree one schedule of fees. |
| ec4 | Coast | 1885 | Public navigation school | The authority trains coastal pilots. |
| ec5 | Coast | 1940 | The coastal convention | Delegates prepare a common charter. |
| ec6 | Coast | 1980 | Regional ferry service | Islands and mainland share a timetable. |
| eh1 | Hills | 1805 | Pass shelters | Estates maintain refuges on winter roads. |
| eh2 | Hills | 1835 | A mountain archive | Clerks preserve land grants and maps. |
| eh3 | Hills | 1872 | The ridge railway | Freight crosses the high pass. |
| eh4 | Hills | 1918 | County hospitals | Two administrations fund local care. |
| eh5 | Hills | 1950 | A shared radio network | Stations coordinate weather reports. |
| eh6 | Hills | 1988 | The federal university | Colleges establish a joint curriculum. |
| ep1 | Plains | 1815 | A road survey | Engineers record bridges and distances. |
| ep2 | Plains | 1840 | Irrigation courts | Farmers agree rules for seasonal water. |
| ep3 | Plains | 1878 | The field convention | Councils prepare a common land register. |
| ep4 | Plains | 1905 | Rural electrification | Cooperative lines connect scattered farms. |
| ep5 | Plains | 1940 | The civic charter | Towns debate a new system of representation. |
| ep6 | Plains | 1985 | The river restoration | Communities reopen the former floodplain. |

Keep `skills/usefulcharts-style/` read-only. Write all generated files inside this workspace. Use the bundled resources without network research or repository discovery.
