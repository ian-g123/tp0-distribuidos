import sys

NETWORKS_CONFIG = """networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

def _generate_server_config(client_id: int) -> str:
    return f"""  server:
    container_name: server
    image: server:latest
    volumes:
      - ./server/config.ini:/config.ini
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - AMOUNT_OF_CLIENTS={num_clients}
    networks:
      - testing_net
"""


def _generate_client_config(client_id: int) -> str:
    return f"""  client{client_id}:
    container_name: client{client_id}
    image: client:latest
    volumes:
      - ./client/config.yaml:/config.yaml
      - ./.data/agency-{client_id}.csv:/bets.csv
    entrypoint: /client
    environment:
      - CLI_ID={client_id}
    networks:
      - testing_net
    depends_on:
      - server
"""


if len(sys.argv) != 3:
    print("Uso: python generar-compose.py <nombre-archivo> <cantidad-clientes>")
    sys.exit(1)

compose_file_name = sys.argv[1]
if not compose_file_name.endswith(".yaml"):
    print("Error: El nombre del archivo debe terminar en '.yaml'.")
    sys.exit(1)
try:
    num_clients = int(sys.argv[2])
    if num_clients < 0:
        raise ValueError(
            "Pueden haber 0 o más clientes, pero la cantidad no puede ser negativa."
        )
except ValueError:
    print("Error: La cantidad de clientes debe ser un número entero positivo.")
    sys.exit(1)


try:
    with open(compose_file_name, "w") as f:
        f.write("name: tp0\n")
        f.write("services:\n")

        f.write(_generate_server_config(num_clients))
        f.write("\n")

        for i in range(1, num_clients + 1):
            f.write(_generate_client_config(i))
            f.write("\n")

        f.write(NETWORKS_CONFIG)
except IOError as e:
    print(f"Error al escribir el archivo '{compose_file_name}': {e}")
    sys.exit(1)
