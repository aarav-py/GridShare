# GridShare

P2P Energy Trading solution for MIT Policy Hackathon 2025.

## Project Structure
- `src/backend`: registration, transaction logging, SDNC-like routing, and Ohio interconnect configuration.
- `src/ledger`: blockchain ledger adapter abstraction for transaction receipts.
- `src/mobile`: onboarding and transaction submission flows for a mobile client.
- `tests`: initial pytest coverage for registration, routing, and ledger logging.
- `docs`: deployment guidance for Ohio utility interties and EV charging partners.

## Quickstart
1. Create a virtual environment and install dependencies.
2. Run the tests to validate the workflow:
   ```bash
   pytest -q
   ```
3. Review `docs/DEPLOYMENT.md` for instructions on integrating with Ohio utilities and EV charging partners.
