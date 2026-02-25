"""Edge Bird CLI: multi-model scatter and divergence analysis for OSINT."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from edgebird import __version__
from edgebird.context import ContextPacket
from edgebird.divergence import analyze_divergence_llm, render_fragment_matrix
from edgebird.fragments import Fragment, extract_fragments
from edgebird.registry import Registry, UnnamedPattern
from edgebird.session import SessionManager

console = Console()


def parse_models(models_str: str) -> list[dict]:
    """Parse comma-separated model specs into model dicts.

    Format: provider/model:label or just provider/model
    Examples:
        anthropic/claude-sonnet-4-20250514:claude
        openai/gpt-4o:gpt
        ollama/llama3.2:local
    """
    result = []
    for spec in models_str.split(","):
        spec = spec.strip()
        if not spec:
            continue
        if ":" in spec:
            model_id, label = spec.rsplit(":", 1)
        else:
            label = spec.split("/")[-1] if "/" in spec else spec
            model_id = spec
        result.append({"id": model_id, "label": label})
    return result


@click.group()
@click.version_option(version=__version__)
def cli():
    """Edge Bird: multi-model scatter and divergence analysis for OSINT investigations."""
    pass


# ---------- Context commands ----------


@cli.command()
@click.argument("context_file", type=click.Path(exists=True))
def inspect(context_file: str):
    """Inspect a context packet (entity/relationship data)."""
    ctx = ContextPacket.load(Path(context_file))
    console.print(Panel(ctx.render(), title="Context Packet", border_style="blue"))
    console.print(
        f"\n[bold]{len(ctx.entities)}[/bold] entities, "
        f"[bold]{len(ctx.relationships)}[/bold] relationships, "
        f"[bold]{len(ctx.gaps)}[/bold] gaps, "
        f"[bold]{len(ctx.humint_notes)}[/bold] HUMINT notes"
    )


# ---------- Scatter commands ----------


@cli.command()
@click.argument("context_file", type=click.Path(exists=True))
@click.option(
    "--models",
    "-m",
    default="anthropic/claude-sonnet-4-20250514:claude,openai/gpt-4o:gpt,ollama/llama3.2:local",
    help="Comma-separated model specs (provider/model:label)",
)
@click.option("--fragments", "-n", default=10, help="Number of fragments per model")
@click.option("--temperature", "-t", default=0.7, help="Sampling temperature (default 0.7)")
@click.option("--domain", "-d", default="", help="Investigation domain description")
@click.option("--analyst", "-a", default="", help="Analyst identifier")
@click.option(
    "--phase",
    "-p",
    type=click.Choice(["scatter", "dark_edges", "constraint_storm", "all"]),
    default="scatter",
    help="Which phase to run",
)
def run(context_file: str, models: str, fragments: int, temperature: float, domain: str, analyst: str, phase: str):
    """Run an edge-finding session against a context packet."""
    from edgebird.scatter import run_constraint_storm, run_dark_edges, run_scatter

    ctx = ContextPacket.load(Path(context_file))
    model_list = parse_models(models)
    model_labels = [m["label"] for m in model_list]

    console.print(Panel(
        f"Entities: {len(ctx.entities)} | Relationships: {len(ctx.relationships)} | "
        f"Gaps: {len(ctx.gaps)} | HUMINT notes: {len(ctx.humint_notes)}\n"
        f"Models: {', '.join(model_labels)}\n"
        f"Phase: {phase} | Fragments: {fragments} | Temperature: {temperature}",
        title="Edge Bird Session",
        border_style="green",
    ))

    # Create session
    sm = SessionManager()
    session = sm.create(ctx, domain=domain, analyst=analyst, context_path=context_file)
    session.models_used = model_labels
    console.print(f"\nSession: [bold]{session.session_id}[/bold]\n")

    phases_to_run = (
        ["scatter", "dark_edges", "constraint_storm"] if phase == "all" else [phase]
    )

    all_fragments: list[Fragment] = []

    for current_phase in phases_to_run:
        console.print(f"\n[bold yellow]Running phase: {current_phase}[/bold yellow]")

        if current_phase == "scatter":
            responses = run_scatter(ctx, model_list, fragment_count=fragments, temperature=temperature)
        elif current_phase == "dark_edges":
            responses = run_dark_edges(ctx, model_list, count=fragments, temperature=temperature)
        else:
            responses = run_constraint_storm(ctx, model_list, count=fragments, temperature=temperature)

        phase_fragments: list[Fragment] = []

        for resp in responses:
            if resp.error:
                console.print(f"  [red]Error from {resp.label}: {resp.error}[/red]")
                continue

            console.print(f"\n  [bold cyan]{resp.label}[/bold cyan] ({resp.model_id}):")

            # Save raw output
            sm.save_raw_output(session.session_id, current_phase, resp.label, resp.content)

            # Extract fragments
            frags = extract_fragments(
                resp.content, resp.label, current_phase, session.session_id
            )
            phase_fragments.extend(frags)

            for f in frags:
                content_short = f.content[:120] + "..." if len(f.content) > 120 else f.content
                console.print(f"    [{f.id}] {content_short}")

            if resp.usage:
                console.print(
                    f"    [dim]tokens: {resp.usage.get('prompt_tokens', '?')} in / "
                    f"{resp.usage.get('completion_tokens', '?')} out[/dim]"
                )

        # Save phase fragments
        sm.save_fragments(session.session_id, current_phase, phase_fragments)
        all_fragments.extend(phase_fragments)
        session.phases_completed.append(current_phase)
        session.fragment_count += len(phase_fragments)

    sm.update(session)

    # Summary
    console.print(f"\n[bold green]Session complete: {session.session_id}[/bold green]")
    console.print(f"Total fragments: {len(all_fragments)}")
    console.print(f"Phases: {', '.join(session.phases_completed)}")
    console.print(f"\nSession data saved to: sessions/{session.session_id}/")
    console.print("\nNext steps:")
    console.print("  edgebird divergence <session-id>     — analyze cross-model divergence")
    console.print("  edgebird validate <session-id>       — validate fragments interactively")
    console.print("  edgebird log <session-id>            — view session log")


# ---------- Divergence commands ----------


@cli.command()
@click.argument("session_id")
@click.option("--phase", "-p", default=None, help="Filter by phase")
@click.option("--llm/--no-llm", default=False, help="Use LLM for divergence analysis")
@click.option("--analysis-model", default="anthropic/claude-sonnet-4-20250514:analyst", help="Model for LLM analysis")
def divergence(session_id: str, phase: str | None, llm: bool, analysis_model: str):
    """Analyze cross-model fragment divergence for a session."""
    sm = SessionManager()
    fragments = sm.load_fragments(session_id, phase=phase)

    if not fragments:
        console.print(f"[red]No fragments found for session {session_id}[/red]")
        return

    console.print(Panel(
        f"Session: {session_id}\n"
        f"Fragments: {len(fragments)}\n"
        f"Models: {', '.join(sorted(set(f.source_model for f in fragments)))}\n"
        f"Phase filter: {phase or 'all'}",
        title="Divergence Analysis",
        border_style="yellow",
    ))

    # Fragment matrix
    console.print("\n[bold]Fragment Matrix:[/bold]\n")
    console.print(render_fragment_matrix(fragments))

    if llm:
        console.print("\n[bold]LLM-Assisted Divergence Analysis:[/bold]\n")
        model_spec = parse_models(analysis_model)
        _, raw_analysis = analyze_divergence_llm(fragments, model_spec[0] if model_spec else None)
        console.print(Panel(raw_analysis, title="Cross-Model Analysis", border_style="magenta"))
    else:
        console.print("\n[dim]Add --llm to run LLM-assisted divergence analysis[/dim]")


# ---------- Validation commands ----------


@cli.command()
@click.argument("session_id")
@click.option("--phase", "-p", default=None, help="Filter by phase")
def validate(session_id: str, phase: str | None):
    """Interactively validate fragments from a session."""
    sm = SessionManager()
    session = sm.load(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        return

    fragments = sm.load_fragments(session_id, phase=phase)
    if not fragments:
        console.print(f"[red]No fragments to validate[/red]")
        return

    console.print(Panel(
        f"Session: {session_id} | Fragments: {len(fragments)}",
        title="Fragment Validation",
        border_style="green",
    ))

    statuses = ["signal", "plausible", "noise", "inversion", "skip"]
    validated = 0

    for i, frag in enumerate(fragments, 1):
        console.print(f"\n[bold]Fragment {i}/{len(fragments)}[/bold]")
        console.print(f"  ID: {frag.id}")
        console.print(f"  Model: {frag.source_model}")
        console.print(f"  Phase: {frag.phase}")
        console.print(Panel(frag.content, border_style="cyan"))

        choice = click.prompt(
            "  Classify",
            type=click.Choice(statuses),
            default="skip",
        )

        if choice == "skip":
            continue

        frag.validation_status = choice
        validated += 1

        notes = click.prompt("  Notes (optional)", default="", show_default=False)
        if notes:
            frag.notes = notes

        confidence = click.prompt(
            "  Confidence",
            type=click.Choice(["high", "medium", "low", "intuition-only"]),
            default="medium",
        )
        frag.analyst_confidence = confidence

        # If signal or inversion, ask about routing
        if choice in ("signal", "inversion"):
            route = click.prompt(
                "  Route to",
                type=click.Choice(["openplanter", "registry", "next-session", "none"]),
                default="none",
            )

            if route == "registry":
                reg = Registry()
                description = click.prompt("  Pattern description")
                pattern = UnnamedPattern(
                    pattern_id="",
                    discovered="",
                    source_session=session_id,
                    source_models=[frag.source_model],
                    convergence="unique",
                    description=description,
                    fragment_ids=[frag.id],
                    analyst_notes=notes,
                )
                pattern = reg.add(pattern)
                console.print(f"  [green]Registered as {pattern.pattern_id}[/green]")
                session.patterns_registered += 1

    # Save updated fragments
    if validated > 0:
        # Reload all fragments for this phase and update the validated ones
        by_phase: dict[str, list[Fragment]] = {}
        for f in fragments:
            by_phase.setdefault(f.phase, []).append(f)
        for p, frags in by_phase.items():
            sm.save_fragments(session_id, p, frags)

        session.fragments_validated += validated
        sm.update(session)

    console.print(f"\n[bold green]Validated {validated}/{len(fragments)} fragments[/bold green]")


# ---------- Registry commands ----------


@cli.group()
def registry():
    """Manage the Unnamed Pattern Registry."""
    pass


@registry.command("list")
@click.option("--status", "-s", default=None, help="Filter by status")
def registry_list(status: str | None):
    """List unnamed patterns in the registry."""
    reg = Registry()
    patterns = reg.list_all(status=status)

    if not patterns:
        console.print("[dim]Registry is empty[/dim]")
        return

    table = Table(title="Unnamed Pattern Registry")
    table.add_column("ID", style="bold")
    table.add_column("Status")
    table.add_column("Convergence")
    table.add_column("Models")
    table.add_column("Description", max_width=60)
    table.add_column("Discovered")

    for p in patterns:
        status_style = {
            "active": "green",
            "watching": "yellow",
            "named": "bold blue",
            "promoted": "bold magenta",
            "archived": "dim",
        }.get(p.status, "")
        table.add_row(
            p.pattern_id,
            f"[{status_style}]{p.status}[/{status_style}]",
            p.convergence,
            ", ".join(p.source_models),
            p.description[:60],
            p.discovered,
        )

    console.print(table)
    stats = reg.stats()
    console.print(f"\nTotal: {stats['total']} | By status: {stats['by_status']}")


@registry.command("show")
@click.argument("pattern_id")
def registry_show(pattern_id: str):
    """Show details of an unnamed pattern."""
    reg = Registry()
    p = reg.get(pattern_id)
    if not p:
        console.print(f"[red]Pattern not found: {pattern_id}[/red]")
        return

    console.print(Panel(
        f"[bold]{p.pattern_id}[/bold] — {p.status}\n\n"
        f"Discovered: {p.discovered}\n"
        f"Session: {p.source_session}\n"
        f"Models: {', '.join(p.source_models)}\n"
        f"Convergence: {p.convergence}\n"
        f"Validation: {p.validation_status}\n\n"
        f"[bold]Description:[/bold]\n{p.description}\n\n"
        f"[bold]Analyst Notes:[/bold]\n{p.analyst_notes or 'None'}\n\n"
        f"[bold]Validation Method:[/bold]\n{p.validation_method or 'Not specified'}\n\n"
        f"[bold]Fragment IDs:[/bold] {', '.join(p.fragment_ids) or 'None'}\n"
        f"[bold]Related Patterns:[/bold] {', '.join(p.related_patterns) or 'None'}\n"
        f"[bold]Named As:[/bold] {p.named_as or 'Not yet named'}",
        title=f"Pattern: {p.pattern_id}",
        border_style="cyan",
    ))


@registry.command("status")
@click.argument("pattern_id")
@click.argument("new_status", type=click.Choice(["active", "watching", "named", "promoted", "merged", "archived"]))
def registry_status(pattern_id: str, new_status: str):
    """Update a pattern's status."""
    reg = Registry()
    if reg.update_status(pattern_id, new_status):
        console.print(f"[green]{pattern_id} → {new_status}[/green]")
    else:
        console.print(f"[red]Failed to update {pattern_id}[/red]")


@registry.command("note")
@click.argument("pattern_id")
@click.argument("notes")
def registry_note(pattern_id: str, notes: str):
    """Add analyst notes to a pattern."""
    reg = Registry()
    if reg.update_notes(pattern_id, notes):
        console.print(f"[green]Notes added to {pattern_id}[/green]")
    else:
        console.print(f"[red]Pattern not found: {pattern_id}[/red]")


@registry.command("name")
@click.argument("pattern_id")
@click.argument("name")
def registry_name(pattern_id: str, name: str):
    """Name an unnamed pattern (promote to formal type)."""
    reg = Registry()
    if reg.name_pattern(pattern_id, name):
        console.print(f"[bold green]Naming ceremony: {pattern_id} → \"{name}\"[/bold green]")
    else:
        console.print(f"[red]Pattern not found: {pattern_id}[/red]")


# ---------- Session commands ----------


@cli.command("sessions")
def list_sessions():
    """List all edge-finding sessions."""
    sm = SessionManager()
    sessions = sm.list_sessions()

    if not sessions:
        console.print("[dim]No sessions found[/dim]")
        return

    table = Table(title="Edge-Finding Sessions")
    table.add_column("Session ID", style="bold")
    table.add_column("Status")
    table.add_column("Domain")
    table.add_column("Models")
    table.add_column("Fragments")
    table.add_column("Validated")
    table.add_column("Phases")

    for s in sessions:
        table.add_row(
            s.session_id,
            s.status,
            s.domain or "-",
            ", ".join(s.models_used) or "-",
            str(s.fragment_count),
            str(s.fragments_validated),
            ", ".join(s.phases_completed) or "-",
        )

    console.print(table)


@cli.command()
@click.argument("session_id")
def log(session_id: str):
    """View session log."""
    sm = SessionManager()
    session = sm.load(session_id)
    if not session:
        console.print(f"[red]Session not found: {session_id}[/red]")
        return

    fragments = sm.load_fragments(session_id)
    log_text = sm.render_log(session, fragments)
    console.print(log_text)


if __name__ == "__main__":
    cli()
