#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Original small vector emblems and engraved illustrations for poster layouts."""

import math


def symbol(kind, paint="#9A7332", variant=0):
    """Return original artwork in a 100 by 100 local coordinate space."""
    ink = "#34342E"
    line = f'fill="none" stroke="{ink}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"'
    p=[]
    def path(d,fill="none",stroke=ink,width=2):
        p.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')
    def circle(x,y,r,fill="none",stroke=ink,width=2):
        p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    if kind in ("shield","crown"):
        path('M23 28L77 28L75 61Q70 81 50 91Q30 81 25 61Z',paint)
        if variant%3==0:
            path('M47 30H53V87H47ZM26 48H74V55H26Z','#FAF3D3',"none")
        elif variant%3==1:
            path('M26 34L69 77L74 66L36 29Z','#FAF3D3',"none")
            for x,y in ((40,53),(57,68),(60,43)):circle(x,y,3,'#E8BD39',ink,1)
        else:
            for x,y in ((39,44),(62,44),(50,66)):
                path(f'M{x} {y-7}L{x+2} {y-2}L{x+7} {y-2}L{x+3} {y+2}L{x+5} {y+7}L{x} {y+4}L{x-5} {y+7}L{x-3} {y+2}L{x-7} {y-2}L{x-2} {y-2}Z','#F8D45C',ink,.8)
        path('M28 21L23 9L36 17L41 6L50 17L59 6L64 17L77 9L72 21Z','#D5AF50')
        path('M28 22H72V27H28Z','#F2D179')
    elif kind in ("star","sun","compass"):
        circle(50,50,36,"none",paint,4)
        for i in range(16):
            a=i*math.pi/8;r=43 if i%4==0 else 38
            path(f'M{50+math.sin(a)*31:.1f} {50+math.cos(a)*31:.1f}L{50+math.sin(a)*r:.1f} {50+math.cos(a)*r:.1f}',stroke=ink,width=1)
        for i in range(8):
            a=i*math.pi/4;dx,dy=math.sin(a),math.cos(a)
            path(f'M50 50L{50+dx*31:.1f} {50+dy*31:.1f}L{50+math.sin(a+.25)*9:.1f} {50+math.cos(a+.25)*9:.1f}Z',paint if i%2 else '#FBF7E5',ink,1)
        circle(50,50,5,'#FBF7E5',ink,1)
    elif kind in ("globe","astrolabe","orbit"):
        circle(50,44,31,'#F6EBCF',paint,3)
        p.append(f'<ellipse cx="50" cy="44" rx="14" ry="31" {line}/>')
        p.append(f'<ellipse cx="50" cy="44" rx="31" ry="12" {line}/>')
        path('M19 44H81M50 13V75M28 22L72 66M27 66L72 22',width=1)
        path('M25 10Q3 57 39 79L41 87H59L60 80Q88 68 89 45',stroke=paint,width=5)
        path('M39 79L36 93H65L60 79Z',paint)
        path('M29 94H72',stroke=ink,width=3)
    elif kind in ("book","archive"):
        path('M10 20Q31 13 49 25Q69 13 91 20V78Q69 72 50 86Q30 73 10 78Z','#F6EBCF')
        path('M50 25V86M7 26V83Q30 79 50 91Q72 78 94 83V25',stroke=paint,width=4)
        for y in range(31,72,8):
            path(f'M18 {y}Q31 {y-3} 42 {y+3}M58 {y+3}Q70 {y-3} 84 {y}',stroke=ink,width=1.2)
    elif kind in ("wheel","gear"):
        circle(50,50,28,paint,ink,2);circle(50,50,19,'#F6EBCF',ink,1.5)
        for i in range(12):
            a=i*math.pi/6
            x,y=50+math.cos(a)*33,50+math.sin(a)*33
            p.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" transform="rotate({i*30} {x} {y})" fill="{paint}" stroke="{ink}" stroke-width="1.5"/>')
            path(f'M50 50L{50+math.cos(a)*18:.1f} {50+math.sin(a)*18:.1f}',stroke=ink,width=2)
        circle(50,50,5,paint)
    elif kind in ("lens","prism"):
        path('M16 80L49 17L86 80Z','#C1D7D3',ink,2)
        path('M49 17L57 65L86 80M16 80L57 65',stroke='#7497A7',width=1.5)
        path('M1 45L37 45L68 58L100 45',stroke=paint,width=3)
        for i,c in enumerate(('#E05D43','#E8BA2C','#93B18A','#689BC4','#B28BC0')):
            path(f'M68 58L99 {54+i*5}',stroke=c,width=2.5)
    elif kind in ("ship","anchor"):
        path('M9 72Q48 83 91 67L79 84Q48 94 20 83Z','#795A36')
        path('M49 14V77M72 31V73',stroke='#55462D',width=3)
        path('M45 20Q24 35 21 60L45 60Z','#F6ECD3')
        path('M54 21Q71 41 67 62L54 62Z','#F9E9BB')
        path('M76 34L90 61H76Z','#EEE3C9')
        for yy in (89,94):path(f'M6 {yy}Q20 {yy-5} 34 {yy}T62 {yy}T90 {yy}',stroke=paint,width=2)
    elif kind in ("tower","observatory"):
        path('M15 88H86V94H15ZM24 43H77V87H24Z','#C9BD9C')
        path('M18 43Q20 18 50 13Q79 17 83 43Z',paint)
        path('M31 42Q30 18 50 13Q69 20 69 42M50 13V43',stroke=ink,width=1)
        for x in (31,47,64):path(f'M{x} 57Q{x+5} 47 {x+10} 57V71H{x}Z','#6D6A59')
        for y in (77,82):path(f'M25 {y}H76',stroke='#9C9178',width=1)
        path('M47 87V74Q52 68 57 74V87Z','#504A3E')
    elif kind in ("press","machine"):
        path('M19 8H29V89H19ZM73 8H83V89H73ZM16 9H86V20H16Z','#826039')
        path('M37 32H66V42H37ZM33 64H69V73H33ZM11 82H89V89H11Z','#C5A679')
        path('M51 18V63M42 29H70M49 21L56 25L47 30L56 35L47 40L56 45L47 50L53 55',stroke=ink,width=3)
        path('M24 75L71 75L86 87H14Z','#F4E9CE')
        for y in range(76,84,3):path(f'M31 {y}H65',stroke='#958A74',width=.8)
    elif kind in ("obelisk","monument"):
        path('M39 16L50 3L61 16L68 84H31Z','#C8AD73')
        path('M50 3L53 84H68L61 16Z','#9A7E4B',"none")
        path('M23 85H77V94H23Z','#CAB280')
        for y in range(25,75,8):
            path(f'M41 {y}H47M43 {y+2}V{y+5}M49 {y+5}H54',stroke='#76613E',width=1)
    elif kind in ("leaf","branch"):
        path('M47 88Q58 51 51 14',stroke='#65764B',width=4)
        for i in range(5):
            yy=70-i*11
            path(f'M51 {yy}Q22 {yy+3} 22 {yy-16}Q44 {yy-21} 51 {yy}Z',paint)
            path(f'M53 {yy-6}Q82 {yy-3} 83 {yy-22}Q61 {yy-24} 53 {yy-6}Z',paint)
    elif kind in ("portrait","bust"):
        # Fictional illustrated faces; never presented as a likeness of a real person.
        skin=['#D3B48B','#C89975','#BCA384','#AD805F'][variant%4]
        hair=['#4D4237','#80745F','#C7BFA7','#766151'][variant%4]
        path('M0 0H100V100H0Z','#6B6954',"none")
        path('M12 100Q11 73 34 70L67 69Q91 78 94 100Z',paint,ink,1)
        path('M40 59L38 76L52 85L65 72L59 58Z',skin,ink,1)
        path('M30 28Q35 9 57 13Q76 17 71 46L65 63Q57 77 44 67L32 52Z',skin,ink,1)
        path('M28 48Q17 21 38 12Q67 1 78 25L73 53L66 50L68 30Q49 39 35 25L34 46Z',hair,ink,1)
        path('M36 43Q42 39 48 43M55 43Q61 38 65 43M51 44L48 54L54 54M44 61Q53 63 60 59',stroke='#665047',width=1.4)
        circle(42,44,1.4,ink,"none");circle(59,44,1.4,ink,"none")
        path('M38 74L48 89L42 96L27 76M64 73L53 89L61 95L77 77','#E8DFC5',ink,1)
        if variant%2:
            path('M33 53Q32 77 52 79Q70 73 68 52L61 65L44 66Z',hair,ink,.7)
        else:
            path('M25 73Q15 46 25 28L29 55L37 72Z',hair,ink,.7)
        for x in range(22,91,7):path(f'M{x} 88L{x-5} 99',stroke='#3D3B32',width=.6)
        path('M31 24L27 13L39 18L48 8L57 17L70 11L68 24Z','#C4A35B',ink,1)
    else:
        return symbol("compass",paint,variant)
    return ''.join(p)


if __name__ == "__main__":
    print("Import symbol(kind, paint, variant) to render original vector poster artwork.")
