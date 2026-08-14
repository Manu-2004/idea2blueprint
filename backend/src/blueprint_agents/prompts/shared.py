from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.review import Issue


def format_brief(brief: Brief) -> str:
    return (
        f"Idea: {brief.idea}\n"
        f"Who it's for: {brief.who}\n"
        f"Problem it solves: {brief.problem}\n"
        f"Platform: {brief.platform}\n"
        f"Must-do on day one: {brief.features}\n"
        f"Timeline and budget: {brief.budget}\n"
        f"Technical comfort: {brief.comfort}"
    )


def format_issues(issues: list[Issue], agent: str) -> str:
    """Render the subset of issues addressed to one agent as revision instructions.
    Returns "" if none apply, so callers can append unconditionally."""

    relevant = [issue for issue in issues if issue.agent == agent]
    if not relevant:
        return ""
    lines = "\n".join(f"- [{issue.severity}] ({issue.section}) {issue.description}" for issue in relevant)
    return (
        "\n\nThe reviewer flagged issues with your previous draft. Make a targeted revision "
        "that fixes these specifically — don't start over from scratch:\n" + lines
    )
