# TP Neo4j

## Setup

1. Create python virtual environment
    ```bash
    python -m venv .venv

    # On Windows
    .\.venv\Scripts\activate
    ```
2. Install dependences
    ```bash
    pip install -r requirements.txt
    ```
3. Start the Neo4j database container
    ```
    docker run --name neo4j -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j
    ```
4. Start the api
    ```
    python .\main.py
    ```

## Usage

- Visit the API at [localhost:5000](http://localhost:5000)
- Visit the API documentation at [localhost:5000/docs/](http://localhost:5000/docs/) to see the fully documented routes