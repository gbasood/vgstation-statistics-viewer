import os
import click


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest
    print(TEST_PATH)
    rv = pytest.main([TEST_PATH, '--verbose', '--cov=app'])
    exit(rv)
