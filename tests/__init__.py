"""Test package initializer to ensure project root is on sys.path when running pytest.

This allows imports such as ``import building_model_v2`` from within the ``tests``
directory without requiring the package to be installed.
"""

import sys
import os

# Add the repository root (parent of the ``tests`` directory) to ``sys.path``.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
