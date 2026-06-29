"""Constraint Category for Building Model v2.

Defines categories for organizing constraints by domain.
"""

from __future__ import annotations

from enum import Enum


class ConstraintCategory(Enum):
    """Categories for organizing constraints.
    
    Attributes:
        FUNCTIONAL: Design quality and functional constraints.
        BUILDING_CODE: Building code compliance constraints.
        ACCESSIBILITY: Accessibility compliance constraints.
        STRUCTURAL: Structural integrity constraints.
        ENVIRONMENTAL: Environmental impact constraints.
        VASTU: Vastu Shastra compliance constraints.
        CUSTOM: User-defined custom constraints.
    """
    
    FUNCTIONAL = "functional"
    BUILDING_CODE = "building_code"
    ACCESSIBILITY = "accessibility"
    STRUCTURAL = "structural"
    ENVIRONMENTAL = "environmental"
    VASTU = "vastu"
    CUSTOM = "custom"
    
    def __str__(self) -> str:
        """Return the string representation of the category.
        
        Returns:
            The category value as a string.
        """
        return self.value
    
    def __repr__(self) -> str:
        """Return a detailed representation of the category.
        
        Returns:
            A string in the format 'ConstraintCategory.NAME'.
        """
        return f"ConstraintCategory.{self.name}"
    
    @property
    def display_name(self) -> str:
        """Get a human-readable display name.
        
        Returns:
            A formatted display name.
        """
        names = {
            ConstraintCategory.FUNCTIONAL: "Functional",
            ConstraintCategory.BUILDING_CODE: "Building Code",
            ConstraintCategory.ACCESSIBILITY: "Accessibility",
            ConstraintCategory.STRUCTURAL: "Structural",
            ConstraintCategory.ENVIRONMENTAL: "Environmental",
            ConstraintCategory.VASTU: "Vastu",
            ConstraintCategory.CUSTOM: "Custom",
        }
        return names[self]