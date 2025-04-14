# Social Network Simulation with LLM Agent

This project simulates human activity in a social network using an LLM-based agent built with LangGraph and OpenAI API.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
2. Create a .env file with your OpenAI API key:
    ```dotenv
    OPENAI_API_KEY=your_openai_api_key_here
    LOG_LEVEL=DEBUG
    ```


3. Run the simulation:
    ```bash
    python src/main.py --profile data/profiles/user_tech.json --iterations 10
    ```