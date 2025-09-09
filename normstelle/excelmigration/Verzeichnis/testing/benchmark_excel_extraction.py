import argparse
import contextlib
import io
import statistics
import sys
import time
from pathlib import Path


# Ensure we can import excel_extraction when running from other working dirs
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from excel_extraction import extract_excel_to_json_unified
except Exception as import_error:
    print("Failed to import extract function from excel_extraction.py:")
    raise


@contextlib.contextmanager
def suppress_output(enabled: bool):
    if not enabled:
        yield
        return
    devnull_path = 'NUL' if sys.platform.startswith('win') else '/dev/null'
    with open(devnull_path, 'w') as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            yield


def run_once(excel_path: Path, max_row: int, no_write: bool, quiet: bool) -> float:
    output_path = 'NUL' if no_write else None
    start = time.perf_counter()
    with suppress_output(quiet):
        extract_excel_to_json_unified(str(excel_path), output_json_path=output_path, max_row=max_row)
    end = time.perf_counter()
    return end - start


def benchmark(excel_path: Path, max_rows: list[int], runs: int, warmup: int, no_write: bool, quiet: bool):
    results: dict[int, list[float]] = {}
    for max_row in max_rows:
        # Warmup runs (not recorded)
        for _ in range(max(0, warmup)):
            try:
                run_once(excel_path, max_row, no_write, quiet)
            except Exception:
                # If warmup fails, propagate on main runs instead of masking issues
                break

        times: list[float] = []
        for _ in range(runs):
            t = run_once(excel_path, max_row, no_write, quiet)
            times.append(t)
        results[max_row] = times
    return results


def profile_one_run(excel_path: Path, max_row: int, no_write: bool, quiet: bool, profile_out: Path):
    import cProfile
    import pstats

    profiler = cProfile.Profile()
    def _target():
        run_once(excel_path, max_row, no_write, quiet)

    profiler.enable()
    _target()
    profiler.disable()

    profile_out.parent.mkdir(parents=True, exist_ok=True)
    profiler.dump_stats(str(profile_out))

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    print(f"Saved cProfile stats to: {profile_out}")


def print_results(results: dict[int, list[float]]):
    # Header
    print("\n=== Excel Extraction Benchmark Results ===")
    print("MaxRows  Runs  Mean(s)  Median(s)  Min(s)  Max(s)  Stdev(s)")
    for max_row, times in sorted(results.items()):
        if not times:
            continue
        mean_v = statistics.mean(times)
        median_v = statistics.median(times)
        min_v = min(times)
        max_v = max(times)
        stdev_v = statistics.stdev(times) if len(times) >= 2 else 0.0
        print(f"{max_row:<7}  {len(times):<4}  {mean_v:7.3f}  {median_v:9.3f}  {min_v:6.3f}  {max_v:6.3f}  {stdev_v:7.3f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark the performance of excel_extraction.extract_excel_to_json_unified. "
            "By default, it will run a few iterations and report timing statistics."
        )
    )
    default_excel = SCRIPT_DIR / "Verzeichnis.xlsx"
    parser.add_argument("--excel", type=Path, default=default_excel, help="Path to the source Excel file")
    parser.add_argument("--runs", type=int, default=3, help="Number of timed runs per setting")
    parser.add_argument("--warmup", type=int, default=1, help="Warmup runs (not timed)")
    parser.add_argument("--max-row", type=int, default=5000, help="Max row for extraction")
    parser.add_argument(
        "--matrix",
        type=int,
        nargs="*",
        help="Optional list of max-row values to test as a matrix (e.g., --matrix 200 500 1000)",
    )
    parser.add_argument("--no-write", action="store_true", help="Write JSON to null device to avoid disk I/O cost")
    parser.add_argument("--quiet", action="store_true", help="Suppress extractor console output during timing")
    parser.add_argument(
        "--profile",
        type=Path,
        help="If set, run a single profiled extraction and write cProfile stats to this path",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    excel_path: Path = args.excel
    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}")
        sys.exit(1)

    # If profile is requested, do that first with the single configured max_row
    if args.profile:
        print("Running one profiled extraction run...")
        profile_one_run(excel_path, args.max_row, args.no_write, args.quiet, args.profile)

    max_rows = args.matrix if args.matrix and len(args.matrix) > 0 else [args.max_row]
    print(
        f"Benchmarking: file={excel_path.name}, runs={args.runs}, warmup={args.warmup}, "
        f"no_write={'yes' if args.no_write else 'no'}, quiet={'yes' if args.quiet else 'no'}"
    )
    results = benchmark(excel_path, max_rows, args.runs, args.warmup, args.no_write, args.quiet)
    print_results(results)


if __name__ == "__main__":
    main()



