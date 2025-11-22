"""
Test runner script with coverage reporting.
"""
import sys
import subprocess


def run_tests():
    """Run pytest with coverage."""
    print("=" * 70)
    print("RUNNING TESTS WITH COVERAGE")
    print("=" * 70)
    print()

    # Run pytest with coverage
    cmd = [
        'pytest',
        '-v',
        '--cov=src',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-branch',
        'tests/'
    ]

    result = subprocess.run(cmd, capture_output=False)

    print()
    print("=" * 70)
    if result.returncode == 0:
        print("ALL TESTS PASSED")
        print("Coverage report generated in htmlcov/index.html")
    else:
        print("SOME TESTS FAILED")
    print("=" * 70)

    return result.returncode


def run_specific_tests(test_type):
    """
    Run specific test types.

    Args:
        test_type (str): Type of tests to run (unit, integration, etl, analytics)
    """
    print(f"Running {test_type} tests...")

    cmd = ['pytest', '-v', '-m', test_type, 'tests/']
    result = subprocess.run(cmd, capture_output=False)

    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        sys.exit(run_specific_tests(test_type))
    else:
        sys.exit(run_tests())
