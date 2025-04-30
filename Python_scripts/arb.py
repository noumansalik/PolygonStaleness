import requests
import time
import jwt
import datetime

# --- API URLs ---
QUOTE_API_URL = "https://accounts.redenvelope.dev/v2/quote"
CURRENCY_CHARGES_API_URL = "https://admin.redenvelope.dev/v1/orgs/78f668e3-37a7-4cc2-a36e-304811b4551a/currency_charges"

# --- Credentials (replace these placeholders!) ---
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgYTGK4xg/TDH/yEDY\nGOMwW1+s6buSkWqKYjyaqtCOALigCgYIKoZIzj0DAQehRANCAAR17BER7YPQUCjZ\nfZoW4mEfAoYLjWep+PmZJxgQUMHQO07/N5/ODwWlho49JcfDO5zRQ5vz/VwMBiSc\nM0a1Afts\n-----END PRIVATE KEY-----\n"
KEY_NAME = "org/78f668e3-37a7-4cc2-a36e-304811b4551a/apiKey/18ffb303-4a05-4b30-962b-ed77984b671c"
ORG_ID = "78f668e3-37a7-4cc2-a36e-304811b4551a"

# --- Currency ID Mapping (update with real IDs) ---
CURRENCY_ID_MAP = {
    "AUD": "7b4212e4-c64e-4823-8f2a-06ff0f4b8f0b",
    "EUR": "689b2d96-b431-4b31-85bf-f5d9f4a0a10b",
    "GBP": "138f708a-669d-43eb-87ed-32b6707a140b",
    "USD": "dd849fab-2f8c-47d2-9379-9271d503f152",
    "AED": "ea86ed05-2a4b-40fc-841d-ae2f194e106a",
    "USDT": "93f46865-1c4b-444d-a2ae-19ed934c8e13",
    "USDC": "3b1c3b53-c0e5-4a24-a134-f9358e4e3616"
}

# --- Headers for Currency Charges API (with valid cookie) ---
currency_charges_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://admin.redenvelope.dev",
    "referer": f"https://admin.redenvelope.dev/clients/{ORG_ID}/spreads",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Cookie": "CF_Authorization=eyJhbGciOiJSUzI1NiIsImtpZCI6IjU5ZThmZTE4YzFmYjFjODE0ZDBjOTdlNWUxZWE3MDI1MDA4OWE0NTlmM2Q0MTBkNGQxNjZiNjQ2YWUzZWI2YzIifQ.eyJhdWQiOlsiMjI3YWQzNDc0M2YzZmM4NGVmNjY5ZjcyNTNjMjM0NzRhN2EyODgxYzk1M2JkYzYzZDM0NDU3YWE1ZWVjNzU1NyJdLCJlbWFpbCI6Im5vdW1hbkByZWRlbnZlbG9wZS5jbyIsImV4cCI6MTc0NTIxNDg3MSwiaWF0IjoxNzQ0NjEwMDcxLCJuYmYiOjE3NDQ2MTAwNzEsImlzcyI6Imh0dHBzOi8vcmVkaHEuY2xvdWRmbGFyZWFjY2Vzcy5jb20iLCJ0eXBlIjoiYXBwIiwiaWRlbnRpdHlfbm9uY2UiOiJ0anp3cG4yQWxKQ0lac0RyIiwic3ViIjoiMjNiNTFkNDUtZTE3Mi01N2RiLWFjYzUtNjdlODhkNTM2ZTIwIiwiY291bnRyeSI6IklOIn0.QhlXy6ulfn6sDaIJJ3R8ixgYdJezLRGKDdLHBFUSSChNS__T7Pavr69lzxy6mP4a-kZ0qlncIr0-uC430CllhDudMVuMPAcrGxfG2Chbj8Ff1jtZ1YtJ6JMQ-12pLGsxMNtuUmJZJgYwrP7CzgOOaRG5vNyvfx5iEIbCm-2vgRLyG2HxLqnGT4DwkLHRgSoPLjkiJpMlEIxQJFPZiIbWPur_dSKjDHkn7besM9iyPrDrbxshhdBdPJPrQF2Vjwp7h87-VljLWwKL4C0H9M8L__CWiUf6wyFQgUU7uxz-okjSZycl4kw_Sp5ybGxbHzyhiRjKwto1x4p_SvDMwpPzgA; CF_Binding=eyJhbGciOiJSUzI1NiIsImtpZCI6IjU5ZThmZTE4YzFmYjFjODE0ZDBjOTdlNWUxZWE3MDI1MDA4OWE0NTlmM2Q0MTBkNGQxNjZiNjQ2YWUzZWI2YzIifQ.eyJzdWIiOiIyM2I1MWQ0NS1lMTcyLTU3ZGItYWNjNS02N2U4OGQ1MzZlMjAiLCJleHAiOjE3NDUyMTQ4NzEsImlhdCI6MTc0NDYxMDA3MSwidHlwZSI6ImJpbmRpbmcifQ.kedfVlmEw5yboaAptceZHlJoRuGdxhIJHYy7J7WLMlxh9Is6KzPh8FQsagsqkmn6INoL5QxXN2JofC9iU0MvsrU-OFfw7EX5-6qqI05RpvSuAfofmFP5k5KF8ut2E2VKYt6Gm7Dpw8ArSEFpAc2KKckENoPqaNp-iP97bXITxchmrrw57c3Pg8LCspoUrecBxnr3S6kdo4fcMhrKrS1fZNyVINI-YMm5yeJx2CZmqBRdXcGe8dCkVAZmahmhDGH9jkEmPIzpoNBd-kS0MAVs8M4U3_sdijAmCkn3E3_oWU_ACmGRDuDwKFnrnAlb5Nyzq4Lw84ssPnSuA9rwK0TnMg; mgmt_auth_token=7fdfd85ef1d62576fca2214bfd1be9bb36f40a793b31d2b9d76f168746082f71.%2FUNqhkm%2FUw%2FSOo4lAHW9bkfpFCN6JBHu1aCtEd4ifxg%3D; token=059d9c3a588cd65549876707b1a57095832e6b460d0893575a0abaef4fbfcdb0.lvelM42eSmA2pLKkW4juyLstFa0n85mgQQquQ%2FIp1Wk%3D" 
}

# --- JWT Token Generation ---
def generate_jwt():
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": KEY_NAME,
        "orgId": ORG_ID,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=2),
        "aud": "https://accounts.redenvelope.dev"
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return token

# --- Set Currency Charges ---
def set_currency_charges(buy_bps, sell_bps, currency):
    if currency not in CURRENCY_ID_MAP:
        raise ValueError(f"No currency charge ID mapped for {currency}")

    spread_bps = round(buy_bps + sell_bps, 6)

    payload = {
        "id": CURRENCY_ID_MAP[currency],
        "buyBps": buy_bps,
        "sellBps": sell_bps,
        "spreadBps": spread_bps
    }

    print(f"\n[Setting Charges] {currency}: buyBps={buy_bps}, sellBps={sell_bps}, spreadBps={spread_bps}")
    response = requests.post(CURRENCY_CHARGES_API_URL, json=payload, headers=currency_charges_headers)

    print("Status:", response.status_code)
    print("Response:", response.text)
    response.raise_for_status()

    return response.json()

# --- Generate Quote ---
def generate_quote(amount, buy, sell, referenced_unit):
    jwt_token = generate_jwt()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }

    payload = {
        "amount": amount,
        "buy": buy,
        "sell": sell,
        "referencedUnit": referenced_unit
    }

    response = requests.post(QUOTE_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Arbitrage Test ---
def test_arbitrage(pair, amount):
    base = pair["base"]
    quote = pair["quote"]
    print(f"\n🔹 Testing Arbitrage for {base}/{quote}")

    # Step 1: Set beneficial buy charges
    set_currency_charges(buy_bps=-2.5, sell_bps=0, currency=base)
    time.sleep(1)

    # Step 2: BUY trade (buy base currency cheaply)
    buy_resp = generate_quote(amount, buy=base, sell=quote, referenced_unit=base)
    buy_amt = buy_resp["data"]["quote"]["quoteAmount"]
    ref_amt = buy_resp["data"]["quote"]["referencedAmount"]
    buy_rate = buy_amt / ref_amt
    print(f"✅ BUY {base} rate: {buy_rate:.6f} {quote}/{base}")

    # Step 3: Reset charges to neutral for SELL
    set_currency_charges(buy_bps=0, sell_bps=0, currency=base)
    time.sleep(1)

    # Step 4: SELL trade (sell base currency normally)
    sell_resp = generate_quote(amount, buy=quote, sell=base, referenced_unit=base)
    sell_amt = sell_resp["data"]["quote"]["quoteAmount"]
    sell_rate = sell_amt / sell_resp["data"]["quote"]["referencedAmount"]
    print(f"✅ SELL {base} rate: {sell_rate:.6f} {quote}/{base}")

    # Step 5: Evaluate arbitrage
    profit = (sell_rate - buy_rate) * amount
    if profit > 0:
        print(f"🎉 Arbitrage Profit: {profit:.2f} {quote}")
    else:
        print(f"⚠️ No Arbitrage Opportunity: Loss {abs(profit):.2f} {quote}")

# --- Main Execution ---
if __name__ == "__main__":
    currency_pairs = [
        {"base": "AUD", "quote": "USD"},
        {"base": "EUR", "quote": "USD"},
        {"base": "GBP", "quote": "USD"},
        {"base": "USD", "quote": "EUR"},
        {"base": "USD", "quote": "AUD"}
    ]

    test_amount = 1000
    for pair in currency_pairs:
        test_arbitrage(pair, test_amount)
