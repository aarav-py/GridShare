# Deployment Guide: Ohio Utility Intertie & EV Charging Partners

This document describes how to deploy the GridShare services into an Ohio utility intertie with blockchain-backed logging and SDNC-like routing.

## Prerequisites
- Python 3.11+
- Access credentials for the selected Ohio utility partner (e.g., AEP Ohio API keys)
- Connectivity to EV charging partner APIs (ChargePoint, Electrify America, municipal depots)
- Container runtime (Docker or Podman) if packaging services

## Components
- **Backend services** (`src/backend`): registration, transaction logging, and routing logic.
- **Ledger integration** (`src/ledger`): blockchain adapter for immutable logs.
- **Mobile client** (`src/mobile`): onboarding and transaction submission flows.

## Ohio Interconnect Configuration
Configuration lives in `src/backend/config.py` under `OHIO_INTERCONNECT`. Adjust fields to match deployment:
- **transmission_operator**: PJM Interconnection
- **compliance_rules**: PUCO and IEEE 1547 alignment
- **utility_partners**: AEP Ohio, Duke Energy Ohio, FirstEnergy
- **ev_charging_partners**: reference EV hub endpoints
- **grid_nodes**: node graph used by SDNC-like routing

To override at runtime, export `GRIDSHARE_REGION=ohio` and point your service loader to `DEFAULT_CONFIGS[GRIDSHARE_REGION]`.

## Deployment Steps
1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt  # create this if packaging for production
   ```
2. **Run backend services**
   - Wire `Registry`, `TransactionLogger`, and `Router` with `OHIO_INTERCONNECT`.
   - Expose APIs that wrap onboarding and transaction submission; secure them with utility-issued credentials.
3. **Connect blockchain ledger**
   - Replace `src/ledger/adapter.py` with a production adapter (e.g., Hyperledger Fabric chaincode client).
   - Ensure append operations include compliance metadata for PUCO audits.
4. **Enable routing**
   - Confirm producer and consumer metadata includes `node` identifiers matching `grid_nodes` keys.
   - Use `Router.compute_route` to validate feasible power paths before clearing trades.
5. **Integrate EV charging partners**
   - Map EV hubs to `grid_nodes` (e.g., `EVHub-Dayton`, `EVHub-Cleveland`).
   - Exchange certificates or API tokens per partner requirements.
6. **Observability & audits**
   - Stream `TransactionLogger` events to your monitoring stack.
   - Persist ledger receipts for PUCO compliance and PJM reporting.

## Validation
- Run the built-in workflow tests:
  ```bash
  pytest -q
  ```
- Simulate a producer-to-consumer transaction using the mobile client API and confirm ledger writes.
