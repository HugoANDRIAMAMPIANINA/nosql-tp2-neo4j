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
    pip install flask py2neo
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

1. Visit the API at [localhost:8080](http://localhost:8080)