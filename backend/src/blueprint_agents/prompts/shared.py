from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.review import Issue


def format_brief(brief: Brief) -> str:
    text = (
        f"Idea: {brief.idea}\n"
        f"Who it's for: {brief.who}\n"
        f"Problem it solves: {brief.problem}\n"
        f"Platform: {brief.platform}\n"
        f"Must-do on day one: {brief.features}\n"
        f"Timeline and budget: {brief.budget}\n"
        f"Technical comfort: {brief.comfort}"
    )
    if brief.clarifications:
        answers = "\n".join(f"- {c.question} -> {c.answer}" for c in brief.clarifications)
        text += "\n\nAnswers to prior clarifying questions:\n" + answers
    return text


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


def format_used_titles(used_titles: list[str]) -> str:
    """Render the product names this user has already generated in past specs, so the
    Product agent doesn't propose one of them again. Returns "" if none, so callers can
    append unconditionally."""

    if not used_titles:
        return ""
    lines = "\n".join(f"- {title}" for title in used_titles)
    return (
        "\n\nThis user has already generated specs with these product names — pick a name "
        "that is clearly different from all of them, not a minor variation:\n" + lines
    )
