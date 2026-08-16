import os

import uvicorn


def main() -> None:
    uvicorn.run("blueprint_agents.api.app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


if __name__ == "__main__":
    main()
