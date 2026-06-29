"""Demo CLI for Craftshood AI.

Exposes the deterministic GenerationPipeline through a command-line interface.
No AI. No LLM. Pure deterministic orchestration.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from building_model_v2.ai.generation_pipeline import GenerationPipeline


def format_requirements(result) -> str:
    """Format design requirements for display."""
    lines = []
    if result.design_requirements is not None:
        b = result.design_requirements.building
        lines.append(f"  Building Type: {b.building_type or 'Not specified'}")
        lines.append(f"  Bedrooms: {b.bedrooms or 'Not specified'}")
        lines.append(f"  Bathrooms: {b.bathrooms or 'Not specified'}")
        lines.append(f"  Floors: {b.floors or 'Not specified'}")
        lines.append(f"  Parking: {'Yes' if b.parking else 'No'}")
        lines.append(f"  Pooja Room: {'Yes' if b.pooja else 'No'}")
        lines.append(f"  Office: {'Yes' if b.office else 'No'}")
        lines.append(f"  Balcony: {'Yes' if b.balcony else 'No'}")
        lines.append(f"  Utility: {'Yes' if b.utility else 'No'}")
        lines.append(f"  Vastu Required: {'Yes' if b.vastu_required else 'No'}")
        lines.append(f"  Accessibility: {'Yes' if b.accessibility_required else 'No'}")
        if result.design_requirements.style:
            lines.append(f"  Style: {result.design_requirements.style}")
    return "\n".join(lines)


def format_space_program(result) -> str:
    """Format space program summary for display."""
    lines = []
    if result.space_program is not None:
        sp = result.space_program
        lines.append(f"  Total Rooms: {sp.room_count}")
        lines.append(f"  Bedrooms: {sp.bedroom_count}")
        lines.append(f"  Bathrooms: {sp.bathroom_count}")
        lines.append(f"  Floors: {sp.floor_count}")
        lines.append(f"  Total Target Area: {sp.total_target_area:.0f} sqft")
        lines.append(f"  Circulation Area: {sp.circulation_area:.0f} sqft")
        lines.append(f"  Usable Area: {sp.usable_area:.0f} sqft")
        lines.append("")
        lines.append("  Rooms:")
        for room in sp.rooms:
            req = "required" if room.required else "optional"
            area = f"{room.target_area:.0f} sqft" if room.target_area else "N/A"
            lines.append(f"    - {room.name} ({room.room_type}): {area} [{req}]")
    return "\n".join(lines)


def format_improvements(result) -> str:
    """Format improvement recommendations for display."""
    lines = []
    if result.improvement_plan is not None:
        plan = result.improvement_plan
        if hasattr(plan, "actions") and plan.actions:
            lines.append(f"  Recommended Actions: {len(plan.actions)}")
            for action in plan.actions[:5]:
                lines.append(f"    - {action.title}")
        else:
            lines.append("  No improvements recommended.")
    else:
        lines.append("  No improvements recommended.")
    return "\n".join(lines)


def run_demo(prompt: str, output_file: str | None = None) -> dict:
    """Run the generation pipeline and return results."""
    pipeline = GenerationPipeline()
    result = pipeline.generate(prompt)

    # Print results
    print("=" * 60)
    print("CRAFTSHOOD AI - Generation Pipeline Demo")
    print("=" * 60)
    print(f"\nPrompt: {prompt}")
    print(f"\nSuccess: {result.success}")
    print(f"\n--- Design Requirements ---")
    print(format_requirements(result))
    print(f"\n--- Space Program Summary ---")
    print(format_space_program(result))
    print(f"\n--- Scores ---")
    print(f"  Final Score: {result.final_score:.1f}/100")
    print(f"  Layout Score: {result.layout_score:.1f}/100")
    print(f"  Quality: {result.quality}")
    print(f"  Iterations: {result.iteration_count}")
    print(f"\n--- Recommended Improvements ---")
    print(format_improvements(result))

    if result.metadata.get("warnings"):
        print(f"\n--- Warnings ---")
        for w in result.metadata["warnings"]:
            print(f"  - {w}")

    print("\n" + "=" * 60)

    # Serialize result
    result_dict = result.to_dict()

    # Save to file if requested
    if output_file:
        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, default=str)
        print(f"\nResult saved to: {output_path}")

    return result_dict


def main() -> None:
    """Main entry point for the demo CLI."""
    parser = argparse.ArgumentParser(
        description="Craftshood AI - Deterministic Generation Pipeline Demo",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="",
        help="Design prompt (natural language)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read prompt from stdin",
    )

    args = parser.parse_args()

    # Get prompt
    if args.stdin:
        prompt = sys.stdin.read().strip()
    else:
        prompt = args.prompt

    if not prompt:
        print("Error: No prompt provided.", file=sys.stderr)
        sys.exit(1)

    run_demo(prompt, args.output)


if __name__ == "__main__":
    main()
