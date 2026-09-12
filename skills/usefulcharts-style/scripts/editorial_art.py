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
    if kind=='heraldry':
        # Original fictional devices, used as consistent diagram identifiers.
        # They are not reconstructions of a historical coat of arms.
        outline='M18 8H82L79 53Q76 76 50 94Q24 76 21 53Z'
        path(outline,paint,ink,2.5)
        gold='#FFE4A3';light='#FFF9DF';v=variant%7
        if v==0:
            path('M49 76V30M49 56L32 39M49 47L65 31',stroke=gold,width=5)
            for x,y in [(33,34),(42,27),(64,27),(57,49)]:
                path(f'M{x} {y+9}C{x-12} {y+1} {x-8} {y-11} {x} {y-7}C{x+8} {y-11} {x+12} {y+1} {x} {y+9}Z',light,ink,1)
        elif v==1:
            for x,y in [(35,32),(65,32),(50,62)]:
                path(f'M{x+7} {y-10}A13 13 0 1 0 {x+7} {y+10}A10 10 0 0 1 {x+7} {y-10}Z',gold,ink,1)
        elif v==2:
            for x,y in [(35,31),(65,31),(50,62)]:
                points=[]
                for i in range(10):
                    angle=-math.pi/2+i*math.pi/5;r=13 if i%2==0 else 5.5
                    points.append(f'{x+math.cos(angle)*r:.2f},{y+math.sin(angle)*r:.2f}')
                p.append(f'<polygon points="{" ".join(points)}" fill="{light}" stroke="{ink}" stroke-width="1"/>')
        elif v==3:
            for y,w in [(28,53),(47,50),(66,34)]:
                x=50-w/2
                path(f'M{x} {y}Q{x+w/4} {y-6} 50 {y}T{x+w} {y}V{y+7}Q{50+w/4} {y+1} 50 {y+7}T{x} {y+7}Z',light,ink,1)
        elif v==4:
            path('M32 74V39H27V24H35V31H45V21H55V31H65V24H73V39H68V74Z',light,ink,1.6)
            path('M45 74V59Q50 50 55 59V74Z',paint,ink,1)
            for x in (38,57):path(f'M{x} 41H{x+5}V48H{x}Z',paint,ink,.7)
            path('M32 51H68M34 66H42M58 66H67',stroke=ink,width=.7)
        elif v==5:
            for i in range(12):
                a=i*math.pi/6
                path(f'M{50+math.cos(a)*18:.2f} {48+math.sin(a)*18:.2f}L{50+math.cos(a+.07)*30:.2f} {48+math.sin(a+.07)*30:.2f}L{50+math.cos(a+.14)*18:.2f} {48+math.sin(a+.14)*18:.2f}Z',gold,ink,.8)
            circle(50,48,16,gold,ink,1)
            path('M44 44H45M55 44H56M45 55Q50 59 55 55',stroke=ink,width=1)
        else:
            for i in range(5):
                a=-math.pi/2+i*2*math.pi/5
                circle(round(50+math.cos(a)*14,2),round(47+math.sin(a)*14,2),11,light,ink,1)
            circle(50,47,9,gold,ink,1.2)
            path('M50 59V77M49 68Q34 56 34 68Q36 77 49 71M51 68Q66 56 66 68Q64 77 51 71',stroke=gold,width=3)
    elif kind in ("shield","crown"):
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
    elif kind=='star':
        # A celestial device, distinct from a compass rose at small print sizes.
        points=[]
        for i in range(16):
            angle=-math.pi/2+i*math.pi/8;r=39 if i%2==0 else 12
            points.append(f'{50+math.cos(angle)*r:.2f},{50+math.sin(angle)*r:.2f}')
        p.append(f'<polygon points="{" ".join(points)}" fill="{paint}" stroke="{ink}" stroke-width="2"/>')
        path('M50 11V89M11 50H89',stroke='#F6EBCF',width=2.3)
        circle(50,50,8,'#F6EBCF',ink,1.6)
        for x,y in ((18,18),(82,18),(18,82),(82,82)):
            path(f'M{x} {y-4}V{y+4}M{x-4} {y}H{x+4}',stroke=ink,width=1.7)
    elif kind=='sun':
        for i in range(16):
            angle=i*math.pi/8
            a=angle-.07;b=angle+.07
            points=[(50+math.cos(a)*27,50+math.sin(a)*27),
                    (50+math.cos(angle)*45,50+math.sin(angle)*45),
                    (50+math.cos(b)*27,50+math.sin(b)*27)]
            path('M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in points)+'Z',paint,ink,1.1)
        circle(50,50,26,'#F2D28A',ink,2)
        circle(50,50,22,'none',paint,1)
        path('M36 43Q41 39 46 43M55 43Q60 39 65 43M49 44L47 55H53M41 63Q50 68 60 61',width=1.7)
        circle(41,45,1.7,ink,'none');circle(60,45,1.7,ink,'none')
    elif kind=='compass':
        circle(50,50,36,"none",paint,4)
        for i in range(16):
            a=i*math.pi/8;r=43 if i%4==0 else 38
            path(f'M{50+math.sin(a)*31:.1f} {50+math.cos(a)*31:.1f}L{50+math.sin(a)*r:.1f} {50+math.cos(a)*r:.1f}',stroke=ink,width=1)
        for i in range(8):
            a=i*math.pi/4;dx,dy=math.sin(a),math.cos(a)
            path(f'M50 50L{50+dx*31:.1f} {50+dy*31:.1f}L{50+math.sin(a+.25)*9:.1f} {50+math.cos(a+.25)*9:.1f}Z',paint if i%2 else '#FBF7E5',ink,1)
        circle(50,50,5,'#FBF7E5',ink,1)
    elif kind=='astrolabe':
        circle(50,9,6,'none',ink,2)
        path('M44 18L50 13L56 18V25H44Z',paint,ink,1.7)
        circle(50,57,36,paint,ink,2)
        circle(50,57,31,'#F6EBCF',ink,1.3)
        circle(50,57,27,'none',paint,1.3)
        for i in range(36):
            a=i*math.pi/18
            r=30 if i%3 else 28
            path(f'M{50+math.cos(a)*r:.2f} {57+math.sin(a)*r:.2f}L{50+math.cos(a)*34:.2f} {57+math.sin(a)*34:.2f}',width=.8)
        circle(50,63,21,'none',ink,1.1)
        path('M24 67Q50 22 76 67M30 75Q50 42 70 75M50 27V84M23 57H77',stroke=paint,width=1.2)
        path('M28 79L69 31L72 34L31 82Z',paint,ink,1.4)
        circle(50,57,4,'#F6EBCF',ink,1.5)
    elif kind=='orbit':
        circle(49,48,24,'#F6EBCF',ink,1.8)
        p.append(f'<ellipse cx="49" cy="48" rx="12" ry="24" {line}/>')
        path('M25 48H73M28 37Q49 29 70 37M29 59Q49 66 69 59',stroke=paint,width=1.2)
        p.append(f'<ellipse cx="50" cy="50" rx="46" ry="17" transform="rotate(-33 50 50)" fill="none" stroke="{ink}" stroke-width="2.2"/>')
        path('M72 19L84 11L89 19L77 27Z',paint,ink,1.3)
        path('M79 15L84 23M75 17L80 25',stroke='#F6EBCF',width=1)
        circle(14,76,4,paint,ink,1.5)
        path('M22 13V21M18 17H26M79 76V84M75 80H83',stroke=ink,width=1.3)
    elif kind=='globe':
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
    elif kind=='wheel':
        circle(50,50,39,'#9B7447',ink,2)
        circle(50,50,31,'#F6EBCF',ink,1.5)
        for i in range(10):
            a=i*math.pi/5
            path(f'M{50+math.cos(a)*7:.2f} {50+math.sin(a)*7:.2f}L{50+math.cos(a)*31:.2f} {50+math.sin(a)*31:.2f}',stroke='#8E693E',width=5)
            x,y=50+math.cos(a)*35,50+math.sin(a)*35
            circle(round(x,2),round(y,2),1.4,'#F6EBCF','none')
        circle(50,50,9,paint,ink,2);circle(50,50,3,'#F6EBCF',ink,1)
    elif kind=='gear':
        circle(50,50,28,paint,ink,2);circle(50,50,19,'#F6EBCF',ink,1.5)
        for i in range(12):
            a=i*math.pi/6
            x,y=50+math.cos(a)*33,50+math.sin(a)*33
            p.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" transform="rotate({i*30} {x} {y})" fill="{paint}" stroke="{ink}" stroke-width="1.5"/>')
            path(f'M50 50L{50+math.cos(a)*18:.1f} {50+math.sin(a)*18:.1f}',stroke=ink,width=2)
        circle(50,50,5,paint)
    elif kind=='lens':
        path('M4 50H97',stroke='#898779',width=1)
        path('M48 12Q71 50 48 88Q28 50 48 12Z','#BEDBD8',ink,2)
        path('M48 17Q58 50 48 83',stroke='#FAFFF5',width=2.5)
        for yy in (28,50,72):
            path(f'M3 {yy}H45L82 50L97 {50+(50-yy)*.4:.2f}',stroke=paint,width=2.3)
        circle(82,50,3,ink,'none')
        path('M48 89V94M35 95H61',stroke=ink,width=2)
    elif kind=='prism':
        path('M16 80L49 17L86 80Z','#C1D7D3',ink,2)
        path('M49 17L57 65L86 80M16 80L57 65',stroke='#7497A7',width=1.5)
        path('M1 45L37 45L68 58L100 45',stroke=paint,width=3)
        for i,c in enumerate(('#E05D43','#E8BA2C','#93B18A','#689BC4','#B28BC0')):
            path(f'M68 58L99 {54+i*5}',stroke=c,width=2.5)
    elif kind=='anchor':
        circle(50,13,8,'none',ink,3)
        path('M47 22H53V68Q65 76 79 59L72 57L89 46L87 66L82 62Q71 84 50 94Q29 84 18 62L13 66L11 46L28 57L21 59Q35 76 47 68Z',paint,ink,2)
        path('M29 32H71V38H29Z','#8F744E',ink,2)
        path('M50 25V74M28 69Q37 80 50 87Q63 80 72 69',stroke='#F6EBCF',width=1.6)
    elif kind=='ship':
        path('M9 72Q48 83 91 67L79 84Q48 94 20 83Z','#795A36')
        path('M49 14V77M72 31V73',stroke='#55462D',width=3)
        path('M45 20Q24 35 21 60L45 60Z','#F6ECD3')
        path('M54 21Q71 41 67 62L54 62Z','#F9E9BB')
        path('M76 34L90 61H76Z','#EEE3C9')
        for yy in (89,94):path(f'M6 {yy}Q20 {yy-5} 34 {yy}T62 {yy}T90 {yy}',stroke=paint,width=2)
    elif kind=='tower':
        path('M18 92H82V97H18ZM26 31H74V92H26Z','#C9BD9C',ink,2)
        path('M23 14H33V23H44V14H56V23H67V14H77V35H23Z',paint,ink,2)
        path('M39 92V74Q50 59 61 74V92Z','#675E4B',ink,1.8)
        path('M43 47Q50 35 57 47V59H43Z','#F6EBCF',ink,1.5)
        for yy in (39,64,83):path(f'M27 {yy}H39M62 {yy}H73',stroke='#887D63',width=1.1)
        path('M27 53H37M64 53H73M33 35V43M67 35V43M32 74V82M68 74V82',stroke='#887D63',width=1.1)
    elif kind=='observatory':
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
