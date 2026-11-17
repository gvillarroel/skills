#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13"]
# ///
"""Verify the encoded delivery and publish local playback, credits and inspection sheets."""
import hashlib
import html
import json
import math
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
ART=ROOT/'artifacts'


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def stamp(seconds):
    total=round(seconds*1000);return f'{total//3600000:02}:{total//60000%60:02}:{total//1000%60:02},{total%1000:03}'


def capture(video,t,file):
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2',str(file)],check=True)


def sheet(entries,file,columns=3):
    width,height=640,400;result=Image.new('RGB',(width*columns,height*math.ceil(len(entries)/columns)),'white');draw=ImageDraw.Draw(result)
    font_path=ROOT/'composition/space-grotesk.ttf';font=ImageFont.truetype(str(font_path),20)
    for i,(path,label) in enumerate(entries):
        x,y=i%columns*width,i//columns*height
        image=Image.open(path).convert('RGB').resize((640,360));result.paste(image,(x,y));draw.text((x+12,y+367),label,font=font,fill='#333e48')
    result.save(file,quality=94)


def main():
    story=read(ROOT/'story.json');video=ART/'videos/sixties-lifestyle.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
    vs=next(s for s in probe['streams'] if s['codec_type']=='video');au=next(s for s in probe['streams'] if s['codec_type']=='audio')
    if (vs['width'],vs['height'],int(vs['nb_frames']),vs['r_frame_rate'],vs['pix_fmt'])!=(1920,1080,story['frames'],'30/1','yuv420p'):raise ValueError('Final stream does not match its declared delivery.')
    if abs(float(probe['format']['duration'])-story['duration'])>.05:raise ValueError('Final duration differs from its actual narration/visual budget.')
    color_time=story['scenes'][1]['start']+story['scenes'][1]['cues'][1]['at']+.15
    decoded_rgb=subprocess.check_output(['ffmpeg','-v','error','-ss',str(color_time),'-i',str(video),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    colors={}
    for name,x,y,expected in [('white',1000,50,[255,255,255]),('primaryRed',1280,280,[158,27,50]),('quietGray',1600,520,[231,231,231])]:
        actual=list(decoded_rgb[(y*1920+x)*3:(y*1920+x)*3+3]);colors[name]={'expected':expected,'actual':actual,'maximumChannelDifference':max(abs(a-b) for a,b in zip(actual,expected,strict=True))}
    if any(r['maximumChannelDifference']>6 for r in colors.values()):raise ValueError('Encoded authored colors differ from the intended palette.')
    audio_log=ART/'reviews/audio-stats.log'
    with audio_log.open('wb') as log:subprocess.run(['ffmpeg','-v','info','-i',str(video),'-vn','-af','astats=metadata=0:reset=0,silencedetect=noise=-45dB:d=3.5','-f','null','-'],stdout=log,stderr=log,check=True)
    audio_text=audio_log.read_text(encoding='utf-8',errors='replace');peaks=re.findall(r'Peak level dB:\s*([-\d.]+)',audio_text);rms=re.findall(r'RMS level dB:\s*([-\d.]+)',audio_text)
    audio={'peakDb':float(peaks[-1]),'rmsDb':float(rms[-1]),'silenceStartsOver3_5Seconds':[float(x) for x in re.findall(r'silence_start:\s*([\d.]+)',audio_text)],'codec':au['codec_name'],'sampleRate':au['sample_rate']}
    if audio['peakDb']>=0 or audio['rmsDb']< -45 or audio['silenceStartsOver3_5Seconds']:raise ValueError('Inspect actual encoded audio levels or long silent intervals.')
    entries=[];transitions=[];frames=ART/'images/encoded';frames.mkdir(parents=True,exist_ok=True)
    for scene in story['scenes']:
        for n,cue in enumerate([scene['cues'][0],scene['cues'][2]]):
            t=min(scene['end']-1/30,scene['start']+cue['at']+.15);file=frames/(scene['id']+'-'+str(n)+'.jpg');capture(video,t,file);entries.append((file,f'{scene["id"]} | {t:.2f}s | {cue["target"]}'))
        if scene['panSeconds']:
            for n,fraction in enumerate([.2,.5,.8]):
                t=scene['start']+scene['panSeconds']*fraction;file=frames/(scene['id']+'-pan-'+str(n)+'.jpg');capture(video,t,file);transitions.append((file,f'{scene["id"]} | lateral pan {fraction:.0%} | {t:.2f}s'))
    sheet(entries,ART/'images/encoded-scenes.jpg');sheet(transitions,ART/'images/encoded-transitions.jpg')
    capture(video,story['scenes'][1]['start']+8,ART/'images/poster.jpg')
    used={item['asset'] for scene in story['scenes'] for item in scene.get('primary',[])}|{scene['secondary'] for scene in story['scenes'] if scene.get('secondary')}|{item['asset'] for scene in story['scenes'] for item in scene.get('overview',[])}
    clips=[s for s in read(ART/'data/selected-clips.json') if s['alias'] in used];credits=[];cards=[]
    for number,row in enumerate(clips,1):
        receipt=read(ROOT/row['receipt']);source=receipt['shot'];record={**row,'archiveUrl':source['archive_url'],'nationalArchivesUrl':source.get('national_archives_url'),'rightsInformation':receipt['rights_information']};credits.append(record)
        thumb=f'images/candidates/{row["id"]}.jpg'
        cards.append(f'<article><h2>{number}. {html.escape(row["alias"])} · {row["year"]}</h2><video controls preload="none" poster="{thumb}" src="clips/{row["alias"]}.mp4"></video><p>{html.escape(row["film"])} · {row["shot"]}</p><p>{html.escape(row["observation"])}</p><p><a href="{row["pageUrl"]}">Destockd shot</a> · <a href="{source["archive_url"]}">Original archive record</a></p><code>{row["id"]} · {row["sha256"]}</code></article>')
    save(ART/'manifests/credits.json',{'source':'Destockd individual full clips, with actual Archive.org/NARA provenance','usedClips':len(clips),'clips':credits})
    (ART/'sources.html').write_text('<!doctype html><meta charset="utf-8"><title>Source clips and provenance</title><style>body{font:18px system-ui;max-width:1100px;margin:40px auto;color:#333e48;background:white}video{width:100%;max-height:480px;background:white}article{padding:24px 0;border-bottom:1px solid #e7e7e7}a{color:#9e1b32}code{font-size:12px;overflow-wrap:anywhere}</style><h1>Actual source clips</h1><p>These original downloads retain their source audio. The final commentary uses newly generated Spanish narration. Dates refer to the evidence summarized in the production notes; source appearance alone was not used to assign a year.</p><p><a href="index.html">Watch the finished video</a> · <a href="../production.md">Historical scope and date evidence</a></p>'+''.join(cards),encoding='utf-8')
    subtitles=[];n=1
    for scene in story['scenes']:
        words=read(ART/'audio'/(scene['id']+'.json'))['words'];group=[]
        def add(group):
            nonlocal n
            if not group:return
            start=scene['start']+scene['audioLead']+group[0]['at'];end=scene['start']+scene['audioLead']+group[-1]['at']+group[-1]['duration']
            subtitles.append(f'{n}\n{stamp(start)} --> {stamp(end)}\n'+ ' '.join(w['text'] for w in group)+'\n');n+=1
        for word in words:
            if group and (len(' '.join(w['text'] for w in [*group,word]))>64 or word['at']-group[0]['at']>3.2):add(group);group=[]
            group.append(word)
        add(group)
    (ART/'videos/narration-es.srt').write_text('\n'.join(subtitles),encoding='utf-8')
    duration_label=f"{round(story['duration'])//60}:{round(story['duration'])%60:02}"
    (ART/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1960s archival commentary</title><style>body{margin:0;background:white;color:#333e48;font:18px system-ui}main{max-width:1400px;margin:24px auto;padding:0 20px}video{display:block;width:100%;aspect-ratio:16/9;background:white}nav{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0}a{color:#9e1b32}p{color:#696969}</style><main><video controls playsinline preload="metadata" poster="images/poster.jpg"><source src="videos/sixties-lifestyle.mp4" type="video/mp4"></video><nav><a href="videos/sixties-lifestyle.mp4" download>Download MP4</a><a href="sources.html">Source clips and dates</a><a href="manifests/timing.json">Measured timing</a><a href="videos/narration-es.srt" download>Optional Spanish subtitles</a></nav><p>1920 × 1080 · 30 fps · @@DURATION@@ · Spanish narration · Local video export</p></main></html>'''.replace('@@DURATION@@',duration_label),encoding='utf-8')
    report={'ok':True,'video':str(video),'videoSha256':sha(video),'frames':int(vs['nb_frames']),'seconds':float(probe['format']['duration']),'width':vs['width'],'height':vs['height'],'fps':vs['r_frame_rate'],'audio':audio,'authoredColorSamples':colors,'usedClips':len(clips),'scenes':len(story['scenes']),'nativeGoogleVidsExport':False,'nativeHyperFrames':False,'visualApproval':'Separate actual encoded-scene observations are required; this utility does not approve them automatically.'}
    save(ART/'reviews/delivery.json',report);print(json.dumps({k:report[k] for k in ['ok','frames','seconds','usedClips','scenes','audio']}))


if __name__=='__main__':main()
