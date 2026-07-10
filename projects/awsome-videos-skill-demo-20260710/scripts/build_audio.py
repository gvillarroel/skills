#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import json
from pathlib import Path
import subprocess


PROJECT = Path(__file__).resolve().parents[1]
AUDIO = PROJECT / "artifacts" / "audio"
VOICE = "es-MX-DaliaNeural"
RUNTIME = 70.0

CUES = [
    (0.0, 5.0, "Si Codex necesita este muro de prompt, no es especialista: solo está cargando equipaje."),
    (5.0, 13.0, "Una skill lo comprime en un paquete: SKILL punto eme de declara cuándo activarse, qué proceso seguir, qué recursos consultar y qué resultado entregar. Menos improvisación; más contrato operativo."),
    (13.0, 22.0, "Pero no carga todo de golpe. Con divulgación progresiva, Codex lee primero el núcleo y abre una referencia solo cuando la decisión actual la exige; lo demás permanece fuera."),
    (22.0, 31.0, "Dentro, cada pieza tiene oficio: referencias para criterio, scripts para operaciones repetibles y assets para plantillas, estilos o medios. El paquete separa conocimiento, ejecución y materia prima."),
    (31.0, 41.0, "Después enruta por intención: un flujo convencional va a Mermaid, geometría o datos complejos a D tres, y una escena ilustrada a ImageGen. Cada especialista devuelve un artefacto verificable."),
    (41.0, 51.0, "Ese artefacto cruza una puerta de validación: se comprueban rutas, estructura, contenido y calidad visual. Si falla una condición, la entrega se bloquea antes de parecer correcta por accidente."),
    (51.0, 61.0, "El beneficio también se mide en contexto: frente al muro completo, Codex mantiene cargado un núcleo pequeño y paga detalle solo al necesitarlo. Limitación: una skill inflada o mal diseñada vuelve a pagar la factura."),
    (61.0, 70.0, "Así, la misma especialidad reaparece en cada proyecto, actualizable y bajo demanda. El muro del inicio no desapareció por magia: se convirtió en un workflow reutilizable que sabe cuándo despertar."),
]


def run(command: list[str], timeout: float | None = None) -> None:
    subprocess.run(command, check=True, timeout=timeout)


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def atempo_chain(value: float) -> str:
    values: list[float] = []
    remaining = value
    while remaining > 2.0:
        values.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        values.append(0.5)
        remaining /= 0.5
    values.append(remaining)
    return ",".join(f"atempo={item:.6f}" for item in values)


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    processed: list[Path] = []
    cue_report: list[dict] = []
    for index, (start, end, text) in enumerate(CUES, start=1):
        raw = AUDIO / f"voice-{index:02d}-raw.mp3"
        wav = AUDIO / f"voice-{index:02d}.wav"
        if not raw.exists():
            run(["edge-tts", "--voice", VOICE, "--rate", "+8%", "--text", text, "--write-media", str(raw)], timeout=60)
        raw_duration = duration(raw)
        available = (end - start) - 0.65
        tempo = max(1.0, raw_duration / available)
        if not wav.exists():
            filter_chain = f"{atempo_chain(tempo)},highpass=f=75,lowpass=f=14500,acompressor=threshold=-18dB:ratio=2.5:attack=12:release=140,afade=t=in:st=0:d=0.035,afade=t=out:st={max(0.1, raw_duration / tempo - 0.08):.3f}:d=0.08,aresample=48000,pan=stereo|c0=c0|c1=c0"
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", filter_chain, "-c:a", "pcm_s24le", str(wav)])
        processed.append(wav)
        cue_report.append({"index": index, "start": start, "end": end, "text": text, "rawDuration": raw_duration, "tempo": tempo, "processedDuration": duration(wav)})

    vo_master = AUDIO / "voiceover-master.wav"
    input_args: list[str] = []
    filters: list[str] = []
    labels: list[str] = []
    for index, ((start, _, _), wav) in enumerate(zip(CUES, processed, strict=True)):
        input_args += ["-i", str(wav)]
        delay_ms = int(round((start + 0.18) * 1000))
        label = f"v{index}"
        labels.append(f"[{label}]")
        filters.append(f"[{index}:a]adelay={delay_ms}|{delay_ms}[{label}]")
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{RUNTIME},alimiter=limit=0.92[vo]")
    run(["ffmpeg", "-y", "-loglevel", "error", *input_args, "-filter_complex", ";".join(filters), "-map", "[vo]", "-c:a", "pcm_s24le", str(vo_master)])

    bed = AUDIO / "procedural-bed.wav"
    bed_filter = (
        "[0:a]volume=0.025,tremolo=f=0.11:d=0.18[a0];"
        "[1:a]volume=0.016,tremolo=f=0.17:d=0.22[a1];"
        "[2:a]lowpass=f=900,highpass=f=90,volume=0.010[a2];"
        "[a0][a1][a2]amix=inputs=3:normalize=0,afade=t=in:st=0:d=0.8,afade=t=out:st=68.4:d=1.6,pan=stereo|c0=c0|c1=c0[bed]"
    )
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi", "-i", f"sine=frequency=110:duration={RUNTIME}:sample_rate=48000",
        "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={RUNTIME}:sample_rate=48000",
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:duration={RUNTIME}:sample_rate=48000:amplitude=0.18",
        "-filter_complex", bed_filter, "-map", "[bed]", "-c:a", "pcm_s24le", str(bed),
    ])

    hit = AUDIO / "seam-hit.wav"
    run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=760:duration=0.11:sample_rate=48000",
        "-af", "volume=0.22,afade=t=out:st=0.02:d=0.09,pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_s24le", str(hit),
    ])
    sfx = AUDIO / "semantic-sfx.wav"
    seam_times = [0.0, 5.0, 13.0, 22.0, 31.0, 41.0, 51.0, 61.0]
    sfx_inputs: list[str] = []
    sfx_filters: list[str] = []
    sfx_labels: list[str] = []
    for index, seam in enumerate(seam_times):
        sfx_inputs += ["-i", str(hit)]
        delay_ms = int(round(seam * 1000))
        label = f"h{index}"
        sfx_labels.append(f"[{label}]")
        pitch = 1.0 if index % 2 == 0 else 0.82
        sfx_filters.append(f"[{index}:a]asetrate=48000*{pitch},aresample=48000,adelay={delay_ms}|{delay_ms}[{label}]")
    sfx_filters.append(f"{''.join(sfx_labels)}amix=inputs={len(sfx_labels)}:normalize=0,apad,atrim=0:{RUNTIME}[sfx]")
    run(["ffmpeg", "-y", "-loglevel", "error", *sfx_inputs, "-filter_complex", ";".join(sfx_filters), "-map", "[sfx]", "-c:a", "pcm_s24le", str(sfx)])

    final_mix = AUDIO / "final-mix.wav"
    mix_filter = (
        "[1:a][0:a]sidechaincompress=threshold=0.012:ratio=7:attack=18:release=320:makeup=1[ducked];"
        "[0:a]volume=1.0[voice];[2:a]volume=0.52[hits];"
        "[voice][ducked][hits]amix=inputs=3:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=7,apad,atrim=0:70,aresample=48000[final]"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vo_master), "-i", str(bed), "-i", str(sfx), "-filter_complex", mix_filter, "-map", "[final]", "-c:a", "pcm_s24le", str(final_mix)])
    report = {"ok": True, "voice": VOICE, "runtimeSeconds": RUNTIME, "finalMix": str(final_mix.relative_to(PROJECT).as_posix()), "finalDurationSeconds": duration(final_mix), "cues": cue_report, "rights": "Procedural bed and SFX; synthetic neural narration; no copyrighted music."}
    (AUDIO / "mix-build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
