#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build neural narration and an original procedural mix for all videos.

Run this file with a Python interpreter that has VoxCPM2 provisioned:
  <path-to-voxcpm-python> \
    projects/holiday2026/scripts/build_video_audio_voxcpm.py --force
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from voxcpm import VoxCPM


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
PACKAGES = PROJECT / "video-packages"
SERIES_AUDIO = PROJECT / "artifacts" / "audio"
RUNTIME = 48.0
BEAT_SECONDS = 6.0
VOICE_OFFSET = 0.36
MAX_CUE_SECONDS = 5.68
TARGET_LUFS = -16.0
TARGET_TRUE_PEAK = -1.5
TARGET_LRA = 7.0
MODEL_ID = "openbmb/VoxCPM2"
ANCHOR_TEXT = "Welcome. Let us find a memorable family adventure close to home."


def run(command: list[str], *, timeout: int = 300, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO,
        check=True,
        timeout=timeout,
        capture_output=capture,
        text=True,
    )


def duration(path: Path) -> float:
    result = run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture=True,
    )
    return float(result.stdout.strip())


def load_prepare_module():
    path = PROJECT / "scripts" / "prepare_video_series.py"
    spec = importlib.util.spec_from_file_location("holiday2026_prepare", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def to_numpy(audio) -> np.ndarray:
    if isinstance(audio, torch.Tensor):
        audio = audio.detach().cpu().float().numpy()
    array = np.asarray(audio, dtype=np.float32)
    if array.ndim == 2:
        if array.shape[0] == 1:
            array = array[0]
        elif array.shape[1] == 1:
            array = array[:, 0]
    return np.ascontiguousarray(array.reshape(-1))


def write_wav(path: Path, audio, sample_rate: int = 48_000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, to_numpy(audio), sample_rate, subtype="PCM_24")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cue_cache_key(text: str, anchor: Path) -> str:
    payload = {
        "modelId": MODEL_ID,
        "anchorSha256": sha256_file(anchor),
        "cfgValue": 2.0,
        "inferenceTimesteps": 10,
        "maxLen": 4096,
        "normalize": False,
        "denoise": False,
        "text": text.strip(),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def seed_all(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def generate_anchor(model: VoxCPM, path: Path, force: bool) -> None:
    if path.exists() and not force:
        return
    seed_all(20260711)
    audio = model.generate(
        ANCHOR_TEXT,
        inference_timesteps=10,
        max_len=4096,
        normalize=False,
        denoise=False,
    )
    write_wav(path, audio)


def generate_cue(model: VoxCPM | None, text: str, path: Path, anchor: Path, seed: int, force: bool) -> None:
    text_cache = path.with_suffix(".source.txt")
    cache_matches = text_cache.exists() and text_cache.read_text(encoding="utf-8").strip() == text.strip()
    cache_key = cue_cache_key(text, anchor)
    shared = SERIES_AUDIO / "voice-cache-v2" / f"{cache_key}.wav"
    if shared.exists() and not force:
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shared, path)
        text_cache.write_text(text.strip() + "\n", encoding="utf-8")
        return
    if path.exists() and cache_matches and not force:
        shared.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, shared)
        return
    if model is None:
        raise RuntimeError(
            f"Missing cached neural cue for mix-only mode: {text}. "
            "Run again without --mix-only to synthesize it."
        )
    canonical_seed = int(cache_key[:8], 16)
    seed_all(canonical_seed)
    audio = model.generate(
        text,
        reference_wav_path=str(anchor),
        cfg_value=2.0,
        inference_timesteps=10,
        max_len=4096,
        normalize=False,
        denoise=False,
    )
    write_wav(path, audio)
    text_cache.write_text(text.strip() + "\n", encoding="utf-8")
    shared.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, shared)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def rubberband_filter(tempo: float) -> str:
    if tempo <= 1.001:
        return "anull"
    return (
        f"rubberband=tempo={tempo:.6f}:pitch=1:transients=smooth:"
        "detector=soft:formant=preserved"
    )


def loudnorm_measure(path: Path) -> dict[str, float]:
    result = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
            "-af", f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}:print_format=json",
            "-f", "null", "NUL",
        ],
        capture=True,
    )
    matches = re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, flags=re.DOTALL)
    if not matches:
        raise RuntimeError(f"Could not parse loudnorm report for {path}")
    raw = json.loads(matches[-1])
    return {key: float(value) for key, value in raw.items() if key not in {"normalization_type"}}


def silence_report(path: Path) -> list[dict[str, float]]:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "silencedetect=noise=-45dB:d=1.0", "-f", "null", "NUL"],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", result.stderr)]
    ends = [(float(end), float(length)) for end, length in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", result.stderr)]
    return [
        {"start": starts[index] if index < len(starts) else max(0.0, end - length), "end": end, "duration": length}
        for index, (end, length) in enumerate(ends)
    ]


def build_category_audio(
    category: dict,
    items: list[dict],
    narration: list[str],
    model: VoxCPM | None,
    anchor: Path,
    force: bool,
    max_tempo: float,
) -> dict:
    slug = category["video_slug"]
    audio = PACKAGES / slug / "artifacts" / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    (audio / "narration.txt").write_text("\n".join(narration) + "\n", encoding="utf-8")

    cue_rows: list[dict] = []
    processed: list[Path] = []
    for index, text in enumerate(narration, start=1):
        raw = audio / f"neural-voice-{index:02d}-raw.wav"
        wav = audio / f"neural-voice-{index:02d}.wav"
        (audio / f"voice-{index:02d}.txt").write_text(text + "\n", encoding="utf-8")
        generate_cue(model, text, raw, anchor, 20260711 + category["order"] * 100 + index, force)
        raw_duration = duration(raw)
        tempo = max(1.0, raw_duration / MAX_CUE_SECONDS)
        if tempo > max_tempo:
            raise RuntimeError(
                f"{slug} cue {index} needs {tempo:.3f}x tempo; shorten this line: {text}"
            )
        fade_out_start = max(0.12, raw_duration / tempo - 0.10)
        filters = (
            f"{rubberband_filter(tempo)},highpass=f=75,lowpass=f=14500,"
            "acompressor=threshold=-18dB:ratio=2.5:attack=12:release=140,"
            f"afade=t=in:st=0:d=0.035,afade=t=out:st={fade_out_start:.3f}:d=0.09,"
            "aresample=48000,pan=stereo|c0=c0|c1=c0"
        )
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", filters, "-c:a", "pcm_s24le", str(wav)])
        processed.append(wav)
        cue_rows.append(
            {
                "index": index,
                "start": (index - 1) * BEAT_SECONDS + VOICE_OFFSET,
                "end": index * BEAT_SECONDS,
                "text": text,
                "rawDurationSeconds": round(raw_duration, 3),
                "tempo": round(tempo, 4),
                "processedDurationSeconds": round(duration(wav), 3),
                "cacheKey": cue_cache_key(text, anchor),
                "rawSha256": sha256_file(raw),
            }
        )

    vo_master = audio / "voiceover-master.wav"
    input_args: list[str] = []
    filters: list[str] = []
    labels: list[str] = []
    for index, wav in enumerate(processed):
        input_args += ["-i", str(wav)]
        delay_ms = int(round((index * BEAT_SECONDS + VOICE_OFFSET) * 1000))
        label = f"v{index}"
        labels.append(f"[{label}]")
        filters.append(f"[{index}:a]adelay={delay_ms}|{delay_ms}[{label}]")
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{RUNTIME}[vo]")
    run(["ffmpeg", "-y", "-loglevel", "error", *input_args, "-filter_complex", ";".join(filters), "-map", "[vo]", "-c:a", "pcm_s24le", str(vo_master)])

    bed = audio / "procedural-bed.wav"
    bed_filter = (
        "[0:a]volume=0.032,tremolo=f=0.10:d=0.15[a0];"
        "[1:a]volume=0.024,tremolo=f=0.16:d=0.18[a1];"
        "[2:a]lowpass=f=1500,highpass=f=100,volume=0.012,asplit=2[nl][nr];"
        "[a0][nl]amix=inputs=2:normalize=0[left];"
        "[a1][nr]amix=inputs=2:normalize=0[right];"
        f"[left][right]join=inputs=2:channel_layout=stereo,afade=t=in:st=0:d=0.9,afade=t=out:st={RUNTIME - 0.8}:d=0.8[bed]"
    )
    run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"sine=frequency=110:duration={RUNTIME}:sample_rate=48000",
            "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={RUNTIME}:sample_rate=48000",
            "-f", "lavfi", "-i", f"anoisesrc=color=pink:duration={RUNTIME}:sample_rate=48000:amplitude=0.15",
            "-filter_complex", bed_filter, "-map", "[bed]", "-c:a", "pcm_s24le", str(bed),
        ]
    )

    hit = audio / "seam-hit.wav"
    sfx = audio / "semantic-sfx.wav"
    sample_rate = 48_000
    hit_frames = int(round(0.10 * sample_rate))
    hit_time = np.arange(hit_frames, dtype=np.float32) / sample_rate
    hit_envelope = np.minimum(hit_time / 0.004, 1.0) * np.exp(-38.0 * hit_time)
    base_hit = (0.11 * np.sin(2.0 * np.pi * 680.0 * hit_time) * hit_envelope).astype(np.float32)
    sf.write(hit, np.column_stack((base_hit, base_hit)), sample_rate, subtype="PCM_24")

    sfx_audio = np.zeros((int(RUNTIME * sample_rate), 2), dtype=np.float32)
    for index, seam in enumerate(range(0, 48, 6)):
        frequency = 680.0 if index % 2 == 0 else 584.8
        signal = (0.11 * np.sin(2.0 * np.pi * frequency * hit_time) * hit_envelope).astype(np.float32)
        start = seam * sample_rate
        stop = min(start + hit_frames, len(sfx_audio))
        sfx_audio[start:stop, 0] += signal[: stop - start]
        sfx_audio[start:stop, 1] += signal[: stop - start]
    sf.write(sfx, sfx_audio, sample_rate, subtype="PCM_24")

    premaster = audio / "premaster.wav"
    mix = (
        "[1:a][0:a]sidechaincompress=threshold=0.012:ratio=7:attack=18:release=300:makeup=1[ducked];"
        "[0:a]volume=1.0[voice];[2:a]volume=0.48[hits];"
        f"[voice][ducked][hits]amix=inputs=3:normalize=0,apad,atrim=0:{RUNTIME},aresample=48000[premaster]"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vo_master), "-i", str(bed), "-i", str(sfx), "-filter_complex", mix, "-map", "[premaster]", "-c:a", "pcm_s24le", str(premaster)])

    measured = loudnorm_measure(premaster)
    master = audio / "final-mix.wav"
    loudnorm = (
        f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true:print_format=summary,aresample=48000"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(premaster), "-af", loudnorm, "-c:a", "pcm_s24le", str(master)])
    final_audio = audio / "final-audio.m4a"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(master), "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(final_audio)])

    final_measure = loudnorm_measure(master)
    silences = silence_report(master)
    ok = (
        abs(final_measure["input_i"] - TARGET_LUFS) <= 0.6
        and final_measure["input_tp"] <= -1.35
        and math.isclose(duration(master), RUNTIME, abs_tol=0.15)
        and not [item for item in silences if item["duration"] > 1.2]
        and all(row["tempo"] <= max_tempo for row in cue_rows)
    )
    report = {
        "schemaVersion": 1,
        "ok": ok,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "categoryId": category["id"],
        "videoSlug": slug,
        "voiceModel": "VoxCPM2",
        "modelId": MODEL_ID,
        "voiceAnchor": str(anchor.relative_to(PROJECT).as_posix()),
        "voiceAnchorType": "project-generated synthetic voice; no human voice cloned",
        "runtimeSeconds": RUNTIME,
        "sampleRate": 48_000,
        "channels": 2,
        "targetLufs": TARGET_LUFS,
        "targetTruePeakDbtp": TARGET_TRUE_PEAK,
        "measured": final_measure,
        "silencesOverOneSecond": silences,
        "rights": "VoxCPM2 is Apache-2.0; narration uses a project-generated synthetic anchor. Bed and seam SFX are procedural; no copyrighted music.",
        "finalMix": str(master.relative_to(PACKAGES / slug).as_posix()),
        "finalAudio": str(final_audio.relative_to(PACKAGES / slug).as_posix()),
        "cues": cue_rows,
    }
    (audio / "neural-audio-build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not ok:
        raise RuntimeError(f"Audio quality gate failed for {slug}: {json.dumps(report['measured'])}")
    return report


def write_series_summary(categories: list[dict]) -> dict:
    """Aggregate the current per-package audio reports into one series gate."""
    reports: list[dict] = []
    for category in categories:
        report_path = (
            PACKAGES
            / category["video_slug"]
            / "artifacts"
            / "audio"
            / "neural-audio-build-report.json"
        )
        if not report_path.exists():
            reports.append(
                {
                    "videoSlug": category["video_slug"],
                    "ok": False,
                    "failure": f"missing {report_path}",
                }
            )
            continue
        try:
            item = json.loads(report_path.read_text(encoding="utf-8"))
            reports.append(
                {
                    "videoSlug": item["videoSlug"],
                    "ok": bool(item["ok"]),
                    "integratedLufs": item["measured"]["input_i"],
                    "truePeakDbtp": item["measured"]["input_tp"],
                    "maxTempo": max(cue["tempo"] for cue in item["cues"]),
                }
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            reports.append(
                {
                    "videoSlug": category["video_slug"],
                    "ok": False,
                    "failure": f"invalid audio report: {exc}",
                }
            )

    summary = {
        "schemaVersion": 1,
        "ok": len(reports) == len(categories) and all(item["ok"] for item in reports),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "voiceModel": "VoxCPM2",
        "modelId": MODEL_ID,
        "categoryCount": len(reports),
        "reports": reports,
    }
    (PROJECT / "artifacts" / "reviews" / "neural-audio-series-validation.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build VoxCPM2 narration and final mixes for Holiday 2026.")
    parser.add_argument("--category", action="append", help="Category ID or video slug; repeat to select multiple.")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--force-anchor",
        action="store_true",
        help="Regenerate the synthetic voice anchor; normally reuse it for voice consistency.",
    )
    parser.add_argument("--max-tempo", type=float, default=1.18)
    parser.add_argument(
        "--summarize-existing",
        action="store_true",
        help="Rebuild the 12-category audio validation report without synthesizing audio.",
    )
    parser.add_argument(
        "--mix-only",
        action="store_true",
        help="Reuse all cached neural cues and rebuild only processing, mix, and validation.",
    )
    args = parser.parse_args()

    prepare = load_prepare_module()
    all_categories = json.loads((PROJECT / "source" / "categories.json").read_text(encoding="utf-8"))
    if args.summarize_existing:
        if args.category:
            raise SystemExit("--summarize-existing cannot be combined with --category")
        summary = write_series_summary(all_categories)
        print(json.dumps(summary, indent=2))
        return 0 if summary["ok"] else 1

    categories = all_categories
    ranked = json.loads((PROJECT / "artifacts" / "data" / "ranked-places.json").read_text(encoding="utf-8"))
    requested = set(args.category or [])
    if requested:
        categories = [item for item in categories if item["id"] in requested or item["video_slug"] in requested]
        found = {item["id"] for item in categories} | {item["video_slug"] for item in categories}
        missing = requested - found
        if missing:
            raise SystemExit("Unknown categories: " + ", ".join(sorted(missing)))

    SERIES_AUDIO.mkdir(parents=True, exist_ok=True)
    anchor = SERIES_AUDIO / "holiday2026-synthetic-voice-anchor.wav"
    if args.mix_only:
        if args.force or args.force_anchor:
            raise SystemExit("--mix-only cannot be combined with --force or --force-anchor")
        if not anchor.exists():
            raise SystemExit(f"Missing voice anchor required by --mix-only: {anchor}")
        model = None
        print("Mix-only mode: reusing the existing voice anchor and cached neural cues.", flush=True)
    else:
        print(f"Loading {MODEL_ID} once on {args.device}...", flush=True)
        model = VoxCPM.from_pretrained(MODEL_ID, load_denoiser=False, device=args.device)
        generate_anchor(model, anchor, args.force_anchor)

    reports: list[dict] = []
    for category in categories:
        items = [item for item in ranked if item.get("category_id") == category["id"] and item.get("selected")]
        items.sort(key=lambda item: int(item.get("rank") or 9999))
        narration = prepare.voiceover_lines(category, items)
        print(f"Building neural audio: {category['video_slug']}", flush=True)
        reports.append(build_category_audio(category, items, narration, model, anchor, args.force, args.max_tempo))

    summary = write_series_summary(all_categories)
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
