"""Start the networked arena with or without the Pygame viewer."""

import argparse
import threading
import time

import uvicorn

from src.settings import API_HOST, API_PORT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless", action="store_true", help="Run the API and physics without a viewer.")
    options = parser.parse_args()
    server = uvicorn.Server(
        uvicorn.Config("src.api.api_endpoints:app", host=API_HOST, port=API_PORT, log_level="info")
    )
    if options.headless:
        server.run()
        if not server.started:
            raise SystemExit("The arena API did not start.")
        return

    api_thread = threading.Thread(target=server.run, daemon=True)
    api_thread.start()
    try:
        deadline = time.monotonic() + 15
        while api_thread.is_alive() and not server.started and time.monotonic() < deadline:
            time.sleep(0.05)
        if not server.started:
            raise SystemExit("The arena API did not start. Check whether its port is already in use.")

        from src.core.game_world import game_world_instance

        game_world_instance.run_visualizer()
    finally:
        server.should_exit = True
        api_thread.join(timeout=5)


if __name__ == "__main__":
    main()
