import argparse
from src.agents.llm_agent import LLMAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main entry point for the simulation."""
    parser = argparse.ArgumentParser(description="Run LLM Agent for social network simulation.")
    parser.add_argument("--profile", default="data/profiles/user_tech.json", help="Path to user profile JSON")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")
    args = parser.parse_args()

    logger.info(f"Starting agent with profile: {args.profile}")
    agent = LLMAgent(args.profile)
    agent.run(max_iterations=args.iterations)
    logger.info("Simulation completed.")


if __name__ == "__main__":
    main()