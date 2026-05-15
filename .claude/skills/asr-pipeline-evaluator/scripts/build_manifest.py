#!/usr/bin/env python3
"""Build a JSONL eval manifest from paired audio/label directories.

Pairing rule: a wav (or other audio file) under --audio-dir matches a label file
under --labels-dir when their basenames (sans extension) are identical.

Output format (one JSON object per line):
    {"id": "<basename>", "audio": "<audio path>", "reference": "<label text>", "hypothesis": ""}

The `hypothesis` field is left blank; candidate ASR pipelines fill it after
running their /transcribe endpoint, then re-feed the manifest into the
evaluator.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def collect(dir_path: Path, exts: tuple[str, ...]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for ext in exts:
        for p in sorted(dir_path.rglob(f"*{ext}")):
            if not p.is_file():
                continue
            stem = p.stem
            if stem in out:
                print(f"warning: duplicate basename {stem!r}: {out[stem]} vs {p}", file=sys.stderr)
            out[stem] = p
    return out


def read_label(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return raw.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build JSONL ASR eval manifest from audio + label directories.")
    parser.add_argument("--audio-dir", required=True, help="Directory containing audio files")
    parser.add_argument("--labels-dir", required=True, help="Directory containing label text files")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    parser.add_argument("--audio-ext", nargs="+", default=[".wav", ".flac", ".mp3"], help="Audio file extensions to collect")
    parser.add_argument("--label-ext", nargs="+", default=[".txt"], help="Label file extensions to collect")
    parser.add_argument(
        "--audio-path-style",
        choices=["absolute", "relative-to-out", "as-given"],
        default="relative-to-out",
        help="How to write the audio path in the manifest",
    )
    args = parser.parse_args()

    audio_dir = Path(args.audio_dir).resolve()
    labels_dir = Path(args.labels_dir).resolve()
    out_path = Path(args.out).resolve()

    if not audio_dir.is_dir():
        raise SystemExit(f"audio dir not found: {audio_dir}")
    if not labels_dir.is_dir():
        raise SystemExit(f"labels dir not found: {labels_dir}")

    audio = collect(audio_dir, tuple(args.audio_ext))
    labels = collect(labels_dir, tuple(args.label_ext))

    paired = sorted(set(audio) & set(labels))
    only_audio = sorted(set(audio) - set(labels))
    only_labels = sorted(set(labels) - set(audio))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_path.open("w", encoding="utf-8") as f:
        for stem in paired:
            audio_path = audio[stem]
            if args.audio_path_style == "absolute":
                audio_field = str(audio_path)
            elif args.audio_path_style == "relative-to-out":
                try:
                    audio_field = str(audio_path.relative_to(out_path.parent))
                except ValueError:
                    audio_field = str(audio_path)
            else:
                audio_field = str(audio_path)
            record = {
                "id": stem,
                "audio": audio_field,
                "reference": read_label(labels[stem]),
                "hypothesis": "",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    print(f"wrote {written} paired entries to {out_path}")
    if only_audio:
        print(f"audio without label ({len(only_audio)}): {only_audio[:5]}{' ...' if len(only_audio) > 5 else ''}", file=sys.stderr)
    if only_labels:
        print(f"label without audio ({len(only_labels)}): {only_labels[:5]}{' ...' if len(only_labels) > 5 else ''}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
