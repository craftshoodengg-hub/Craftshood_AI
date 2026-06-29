"""Rule Packs for Building Model v2.

Provides configurable rule packs that define configuration values
used by validation, constraints, scoring, and evaluation.

Rule Packs contain no logic. They only provide configuration.

Modules:
    rule_pack: Base RulePack dataclass and serialization utilities.
    residential_rule_pack: Default rule pack for residential buildings.
    commercial_rule_pack: Default rule pack for commercial buildings.
    custom_rule_pack: Customizable rule pack with user-supplied configuration.
"""

from .rule_pack import (
    RulePack,
    RulePackAccessibility,
    RulePackBuildingCode,
    RulePackEnvironmental,
    RulePackStructural,
    RulePackVastu,
)
from .residential_rule_pack import create_residential_rule_pack
from .commercial_rule_pack import create_commercial_rule_pack
from .custom_rule_pack import create_custom_rule_pack, rule_pack_from_dict

__all__ = [
    "RulePack",
    "RulePackAccessibility",
    "RulePackBuildingCode",
    "RulePackEnvironmental",
    "RulePackStructural",
    "RulePackVastu",
    "create_residential_rule_pack",
    "create_commercial_rule_pack",
    "create_custom_rule_pack",
    "rule_pack_from_dict",
]