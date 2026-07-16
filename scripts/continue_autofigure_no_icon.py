"""Continue AutoFigure-Edit from an imported raster figure without icon replacement.

This is a project-local rescue path for paper pipeline figures. It skips SAM/RMBG
and asks the configured multimodal LLM to reconstruct the raster as SVG.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image


def _windows_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
    except ImportError:
        return ""

    locations = [
        (winreg.HKEY_CURRENT_USER, "Environment"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    ]
    for root, subkey in locations:
        try:
            with winreg.OpenKey(root, subkey) as key:
                value, _ = winreg.QueryValueEx(key, name)
        except OSError:
            continue
        if str(value).strip():
            return str(value).strip()
    return ""


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        value = _windows_env(name)
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--autofigure-dir", default=r"C:\Users\24431\Documents\AutoFigure-Edit")
    parser.add_argument(
        "--input-figure",
        default=r"C:\Users\24431\Documents\每日清单\outputs\autofigure_edit\main_figure_import\figure.png",
    )
    parser.add_argument(
        "--output-dir",
        default=r"C:\Users\24431\Documents\每日清单\outputs\autofigure_edit\main_figure_continue_no_icon",
    )
    parser.add_argument("--provider", default=os.environ.get("AF_PROVIDER", "custom"))
    parser.add_argument("--base-url", default=os.environ.get("AF_BASE_URL", ""))
    parser.add_argument("--model", default=os.environ.get("AF_SVG_MODEL", "gpt-5.4"))
    parser.add_argument("--optimize-iterations", type=int, default=0)
    args = parser.parse_args()

    autofigure_dir = Path(args.autofigure_dir)
    if not autofigure_dir.exists():
        raise RuntimeError(f"AutoFigure-Edit directory not found: {autofigure_dir}")
    sys.path.insert(0, str(autofigure_dir))

    from autofigure2 import (  # type: ignore
        create_embedded_figure_svg,
        generate_svg_template,
        optimize_svg_with_llm,
    )

    api_key = _env("AF_API_KEY")
    base_url = args.base_url or _env("AF_BASE_URL")
    provider = args.provider
    model = args.model

    input_figure = Path(args.input_figure)
    if not input_figure.is_file():
        raise RuntimeError(f"Input figure not found: {input_figure}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    figure_path = output_dir / "figure.png"
    samed_path = output_dir / "samed.png"
    boxlib_path = output_dir / "boxlib.json"
    template_svg_path = output_dir / "template.svg"
    optimized_svg_path = output_dir / "optimized_template.svg"
    final_svg_path = output_dir / "final.svg"

    shutil.copyfile(input_figure, figure_path)
    shutil.copyfile(input_figure, samed_path)

    with Image.open(figure_path) as image:
        width, height = image.size
    boxlib = {
        "image_size": {"width": width, "height": height},
        "prompts_used": [],
        "boxes": [],
        "no_icon_mode": True,
    }
    boxlib_path.write_text(json.dumps(boxlib, indent=2), encoding="utf-8")

    try:
        generate_svg_template(
            figure_path=str(figure_path),
            samed_path=str(samed_path),
            boxlib_path=str(boxlib_path),
            output_path=str(template_svg_path),
            api_key=api_key,
            model=model,
            base_url=base_url,
            provider=provider,
            placeholder_mode="label",
            no_icon_mode=True,
        )
    except Exception as exc:
        print(f"SVG reconstruction failed: {exc}")
        print("Writing embedded-raster fallback final.svg so the run still has an inspectable artifact.")
        create_embedded_figure_svg(str(figure_path), str(final_svg_path))
        return 2

    svg_for_final = template_svg_path
    if args.optimize_iterations > 0:
        optimize_svg_with_llm(
            figure_path=str(figure_path),
            samed_path=str(samed_path),
            final_svg_path=str(template_svg_path),
            output_path=str(optimized_svg_path),
            api_key=api_key,
            model=model,
            base_url=base_url,
            provider=provider,
            max_iterations=args.optimize_iterations,
            no_icon_mode=True,
        )
        if optimized_svg_path.is_file():
            svg_for_final = optimized_svg_path

    shutil.copyfile(svg_for_final, final_svg_path)
    print(f"AutoFigure no-icon continuation output: {output_dir}")
    print(f"Final SVG: {final_svg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
