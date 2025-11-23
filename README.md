# GridShare

GridShare is a lightweight P2P energy trading demo that links clean energy producers to EV charging sites. It combines registration, SDNC-like routing, and blockchain-style ledger logging so you can explore how regional interconnects move clean power while preserving auditability.

## Project Structure

- `src/backend`: registration, transaction logging, SDNC-like routing, and Ohio interconnect configuration.
- `src/frontend`: command-line interface for running a full demo without writing code.
- `src/ledger`: blockchain ledger adapter abstraction for transaction receipts.
- `src/mobile`: onboarding and transaction submission flows for a mobile client.
- `tests`: pytest coverage for registration, routing, ledger logging, and the new frontend CLI.
- `docs`: deployment guidance for Ohio utility interties and EV charging partners.

## Features

- **Interconnect-aware registration**: validate producers, consumers, and hybrids against utility intertie metadata.
- **Route computation**: compute SDNC-like shortest paths across the Ohio interconnect graph before clearing trades.
- **Ledger logging**: append enriched transaction payloads to a blockchain-style adapter for audits.
- **Usable frontend**: run an end-to-end EV charging request from the command line with sensible defaults.

## Quickstart

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt  # optional; the demo works with stdlib
   ```
2. **Run the tests to validate the workflow**
   ```bash
   pytest -q
   ```
3. **Drive the demo from the frontend CLI**
   ```bash
   # Register demo producer/consumer on the Ohio interconnect
   python -m src.frontend.cli bootstrap

   # Submit an EV charging energy request with routing + ledger logging
   python -m src.frontend.cli request \
     --tx-id tx-cli-001 \
     --kilowatt-hours 150.5 \
     --price-usd 42.00 \
     --desired-start 2025-06-01T10:00:00 \
     --priority fast-track

   # Inspect all logged transactions in a human-readable format
   python -m src.frontend.cli ledger
   ```

## How the pieces fit together

- **Configuration** (`src/backend/config.py`): defines the Ohio interconnect, PJM/PUCO constraints, and node graph used for routing.
- **Registry** (`src/backend/registration.py`): stores participants with node metadata that align to the grid graph.
- **Routing** (`src/backend/routing.py`): computes shortest paths between producer and consumer nodes before clearing a trade.
- **Transactions** (`src/backend/transactions.py` + `src/ledger/adapter.py`): enrich transactions with interconnect and routing metadata, then append them to the ledger adapter.
- **Mobile orchestration** (`src/mobile/app.py`): wires registry, routing, and ledger logging for EV charging scenarios.
- **Frontend CLI** (`src/frontend/cli.py`): exposes `bootstrap`, `request`, and `ledger` commands so anyone can exercise the flow.

## Demo workflow

1. **Bootstrap participants**: `python -m src.frontend.cli bootstrap` registers a solar producer at `AEP-Columbus` and an EV hub consumer at `EVHub-Cleveland`.
2. **Submit a charge**: use `python -m src.frontend.cli request` to log a transaction; the CLI validates timestamps, computes the SDNC route, and writes to the ledger.
3. **Review ledger**: `python -m src.frontend.cli ledger` prints a readable summary of every transaction, or append `--as-json` to inspect the raw payloads.

## Configuration tweaks

Ohio defaults live in `src/backend/config.py` under `OHIO_INTERCONNECT`. Override nodes, compliance rules, or partners if you want to model another territory; keep node names aligned with participants’ `metadata["node"]` values to preserve routing.

## Additional docs

See `docs/DEPLOYMENT.md` for guidance on integrating with Ohio utilities, EV charging partners, and production-grade ledger adapters.
