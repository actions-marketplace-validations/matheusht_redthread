"""Click help helpers for the campaign run command."""

from __future__ import annotations

from collections.abc import Iterable

import click

NORMAL_OPTIONS = {
    "objective",
    "system_prompt",
    "rubric",
    "personas",
    "target_model",
    "dry_run",
    "algorithm",
    "report_dir",
}

ADVANCED_OPTIONS = {
    "depth",
    "width",
    "branching",
    "turns",
    "simulations",
    "max_budget_tokens",
    "verbose",
    "env_file",
    "report_md",
    "report_json",
}

RESEARCH_OPTIONS = (
    ("--trace-all", "Enable LangSmith tracing on all nodes."),
    ("--benchmark-fixture", "Use safe jailbreak benchmark fixture metadata hints."),
    ("--persona-weighting-plan", "Use an internal adaptive persona weighting artifact."),
    ("--include-internal-sidecars", "Expose internal adaptive-learning sidecars."),
)


class RunHelpCommand(click.Command):
    """Render run-command help with normal and advanced option sections."""

    def format_options(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        visible_options = [
            param
            for param in self.get_params(ctx)
            if isinstance(param, click.Option) and not param.hidden
        ]
        self._write_group(ctx, formatter, "Options", _matching(visible_options, NORMAL_OPTIONS))
        self._write_group(
            ctx,
            formatter,
            "Advanced options",
            _matching(visible_options, ADVANCED_OPTIONS),
        )
        self._write_group(
            ctx,
            formatter,
            "Research help",
            [param for param in visible_options if param.name == "show_research"],
        )
        self._write_group(
            ctx,
            formatter,
            "Other options",
            [
                param
                for param in visible_options
                if param.name not in NORMAL_OPTIONS
                and param.name not in ADVANCED_OPTIONS
                and param.name != "show_research"
            ],
        )

    def _write_group(
        self,
        ctx: click.Context,
        formatter: click.HelpFormatter,
        title: str,
        options: Iterable[click.Option],
    ) -> None:
        rows = [record for param in options if (record := param.get_help_record(ctx))]
        if rows:
            with formatter.section(title):
                formatter.write_dl(rows)


def show_research_help(
    ctx: click.Context,
    _param: click.Parameter,
    value: bool,
) -> None:
    """Print hidden research controls on demand, then exit."""
    if not value or ctx.resilient_parsing:
        return
    lines = ["Research controls hidden from normal help:", ""]
    lines.extend(f"  {flag:<30} {description}" for flag, description in RESEARCH_OPTIONS)
    click.echo("\n".join(lines))
    ctx.exit()


def _matching(options: Iterable[click.Option], names: set[str]) -> list[click.Option]:
    return [param for param in options if param.name in names]
