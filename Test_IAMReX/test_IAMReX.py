# SPDX-FileCopyrightText: 2025 Shuai He<hswind53@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Build and run the IAMReX CI test cases.

Usage:
    python Test_IAMReX/test_IAMReX.py                  # run every case
    python Test_IAMReX/test_IAMReX.py RSV              # run a single case
    python Test_IAMReX/test_IAMReX.py RSV LidDrivenCavity

Environment variables:
    IAMREX_MAKE_FLAGS  extra flags appended to every make invocation,
                       e.g. "USE_CCACHE=TRUE" in CI.
    IAMREX_QUIET       set to 1/true to suppress build and run output.
"""

import os
import subprocess
import sys

# Common overrides for fast CI runs: minimal steps, small grids, no file output
CI_OVERRIDES = "max_step=2 amr.plot_int=-1 amr.check_int=-1"

# Extra flags appended to every make invocation, e.g. USE_CCACHE=TRUE in CI.
MAKE_FLAGS = os.environ.get("IAMREX_MAKE_FLAGS", "")

# Test cases: name -> (directory relative to this script, make args, run command)
TESTS = {
    # 2D, no MPI - basic compilation and run test
    "LidDrivenCavity": (
        "../Tutorials/LidDrivenCavity",
        "-j8",
        f"./amr2d.gnu.ex inputs.2d.lid_driven_cavity {CI_OVERRIDES}",
    ),
    # 2D, MPI, level set
    "RSV": (
        "../Tutorials/RSV",
        "-j8",
        f"./amr2d.gnu.MPI.ex inputs.2d.rsv {CI_OVERRIDES}",
    ),
    # 3D, MPI, particles/IBM
    "DraftingKissingTumbling": (
        "../Tutorials/DraftingKissingTumbling",
        "-j8 USE_CUDA=FALSE USE_MPI=TRUE DEBUG=FALSE",
        "mpiexec -np 2 ./amr3d.gnu.MPI.ex inputs.3d.DKT max_step=1 "
        "amr.n_cell=16 8 8 amr.plot_int=-1 amr.check_int=-1",
    ),
}


def run_test (name, working_dir, make_args, run_cmd, print_output):
    """Build and run a single test case."""
    build_cmd = " ".join(filter(None, ["make", make_args, MAKE_FLAGS]))
    full_cmd = f"{build_cmd} && {run_cmd}"
    subprocess.run(
        full_cmd,
        shell=True,
        check=True,
        cwd=working_dir,
        stdout=None if print_output else subprocess.DEVNULL,
        stderr=None if print_output else subprocess.DEVNULL
    )
    print(f"Test {name} succeed")

def main():
    # Output is shown by default so that a failing build is diagnosable in CI.
    print_output = os.environ.get("IAMREX_QUIET", "").lower() not in ("1", "true")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Script Directory:", script_dir)

    names = sys.argv[1:] or list(TESTS)
    unknown = [n for n in names if n not in TESTS]
    if unknown:
        sys.exit(f"Unknown test case(s): {', '.join(unknown)}. "
                 f"Available: {', '.join(TESTS)}")

    for name in names:
        rel_dir, make_args, run_cmd = TESTS[name]
        working_dir = os.path.join(script_dir, rel_dir)
        print("Test Working Directory:", os.path.abspath(working_dir))
        run_test(name, working_dir, make_args, run_cmd, print_output)


if __name__ == "__main__":
    main()
