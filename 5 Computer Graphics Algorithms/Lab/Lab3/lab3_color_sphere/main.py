"""Запуск интерфейса или воспроизводимого расчёта лабораторной работы 3."""
import argparse
import sys
from dataclasses import replace
from pathlib import Path

# 同时支持直接运行文件和 python -m 包方式。
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lab3_color_sphere.spectral import BASE, default_parameters, load_parameters, apply_spectra_csv
from lab3_color_sphere.rendering import run_case, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-gui", action="store_true", help="Расчёт без окна")
    parser.add_argument("--case", choices=("white", "colored", "both"), default="white")
    parser.add_argument("--config", type=Path, help="Полная сцена JSON")
    parser.add_argument("--spectra", type=Path, help="Таблица спектров CSV")
    parser.add_argument("--output", type=Path, default=BASE / "results")
    parser.add_argument("--model", choices=("reference_diagram", "lambert"))
    args = parser.parse_args(argv)
    if args.case == "both" and (args.config or args.spectra):
        parser.error("--case both нельзя сочетать с --config или --spectra")
    try:
        def scene(case):
            p = load_parameters(args.config) if args.config else default_parameters(case)
            if args.spectra:
                p = apply_spectra_csv(p, args.spectra.read_text(encoding="utf-8-sig"))
            return replace(p, model=args.model) if args.model else p
        if not args.no_gui:
            from lab3_color_sphere.gui import launch_gui
            launch_gui(scene("white" if args.case == "both" else args.case))
        else:
            for case in ("white", "colored") if args.case == "both" else (args.case,):
                directory = args.output / case if args.case == "both" else args.output
                result = run_case(case, directory, scene(case))
                print(f"[{case}] {directory.resolve()}\n{summary(result)}")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Ошибка: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
