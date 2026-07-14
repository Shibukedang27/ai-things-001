# Binance Futures Testnet Trading Bot

A production-minded Python 3.12 CLI for placing simplified Binance USDT-M Futures Testnet orders. It supports MARKET and LIMIT orders, BUY and SELL sides, validated interactive input, structured logging, retry-aware API access, and formatted terminal output.

## Architecture

The project keeps the CLI thin and moves business logic into service modules:

- `cli.py` handles interactive prompts, confirmation, and Rich output.
- `bot/config.py` loads environment configuration.
- `bot/client.py` wraps Binance Futures Testnet API communication, timeouts, retries, and request logging.
- `bot/orders.py` owns order request modeling, payload creation, order placement, and response formatting.
- `bot/validators.py` validates user input and returns clear domain errors.
- `bot/logging_config.py` configures rotating log files.
- `bot/exceptions.py` defines expected application exceptions.
- `bot/utils.py` contains reusable formatting and console helpers.

## Folder Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── config.py
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── orders.py
│   ├── utils.py
│   └── validators.py
├── tests/
├── logs/
│   ├── sample_limit_success.log
│   └── sample_market_success.log
├── cli.py
├── pytest.ini
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation

```bash
cd trading_bot
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `python3.12` is not available on your machine, use any compatible Python 3 version that can install the dependencies.

## Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Required values:

```env
API_KEY=your_binance_futures_testnet_api_key
API_SECRET=your_binance_futures_testnet_api_secret
TESTNET_URL=https://testnet.binancefuture.com/fapi
```

Use Binance Futures Testnet credentials, not production Binance credentials.

## Running

```bash
python cli.py
```

The CLI displays:

```text
1. Market Order
2. Limit Order
3. Exit
```

It then prompts for symbol, side, quantity, and price for LIMIT orders only. Before submitting an order, it displays an order request summary and asks for confirmation.

## CLI Examples

Market BUY:

```text
Choose an option: 1
Symbol: BTCUSDT
Side: BUY
Quantity: 0.01
Place this order on Binance Futures Testnet? [y/n]: y
```

Limit SELL:

```text
Choose an option: 2
Symbol: ETHUSDT
Side: SELL
Quantity: 0.10
Price: 4500
Place this order on Binance Futures Testnet? [y/n]: y
```

## Sample Output

The application prints an order summary table, a formatted API response table, and a green success panel when Binance accepts the order. On validation, authentication, network, or API errors, it shows a red failure panel with a meaningful message and logs the details.

## Logging

Runtime logs are written to:

```text
logs/trading_bot.log
```

The logger uses rotating files and records endpoint, payload, response, execution time, warnings, and errors. Sample successful order logs are included in `logs/sample_market_success.log` and `logs/sample_limit_success.log`.

## Testing

Run the unit tests:

```bash
pytest
```

Run an import/compile smoke check:

```bash
python -m compileall .
```

## Assumptions

- This bot targets Binance USDT-M Futures Testnet only.
- Symbols must end in `USDT`.
- LIMIT orders use `GTC` time-in-force.
- The bot places one-way orders and does not manage leverage, margin type, position mode, stop loss, take profit, or account balances.

## Troubleshooting

- Missing credentials: ensure `.env` exists in the `trading_bot/` directory and contains `API_KEY` and `API_SECRET`.
- Authentication failure: confirm the credentials were created for Binance Futures Testnet and have futures permissions.
- Network failure: verify internet connectivity and that `TESTNET_URL` is reachable.
- API validation error: confirm the symbol exists on USDT-M Futures Testnet and that quantity/price satisfy Binance filters.

## Future Improvements

- Exchange metadata validation for symbol quantity and tick-size filters.
- Leverage and margin mode controls.
- Stop loss and take profit orders.
- Dry-run mode for local demos.
- Non-interactive command options for automation.
- Structured JSON logs for observability pipelines.
