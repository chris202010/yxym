import os
import requests

def get_ip_list(url):
    response = requests.get(url)
    response.raise_for_status()
    ip_list = response.text.strip().split('\n')
    limited_list = ip_list[:20]
    if len(ip_list) > 20:
        print(f"⚠️ 警告: {url} 返回了 {len(ip_list)} 个IP，只取前20个。")
    return limited_list

def get_cloudflare_zone(api_token):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=headers)
    response.raise_for_status()
    zones = response.json().get('result', [])
    if not zones:
        raise Exception("No zones found")
    return zones[0]['id'], zones[0]['name']

def delete_existing_dns_records(api_token, zone_id, subdomain, domain):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'
    while True:
        response = requests.get(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}',
            headers=headers
        )
        response.raise_for_status()
        records = response.json().get('result', [])
        if not records:
            break
        for record in records:
            delete_response = requests.delete(
                f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record["id"]}',
                headers=headers
            )
            delete_response.raise_for_status()
            print(f"Del {subdomain}:{record['id']}")

def update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'

    # ✅ 自动控制小黄云开关
    # 你可以根据需要自行添加或修改规则
    proxied = subdomain in ['bestcf', 'api']

    for ip in ip_list:
        data = {
            "type": "A",
            "name": record_name,
            "content": ip,
            "ttl": 1,
            "proxied": proxied  # 根据子域自动开关小黄云
        }
        response = requests.post(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
            json=data,
            headers=headers
        )
        result = response.json()
        if response.status_code == 200 and result.get("success", False):
            print(f"Add {subdomain}:{ip} (☁️ {'橙云开' if proxied else '灰云关'})")
        else:
            print(f"Failed to add A record for {subdomain} ({ip}): {response.status_code} {response.text}")

if __name__ == "__main__":
    api_token = os.getenv('CF_API_TOKEN')
    
    # 子域和IP来源映射
    subdomain_ip_mapping = {
        'bestcf': 'https://ipdb.030101.xyz/api/bestcf.txt',  
        'api': 'https://raw.githubusercontent.com/chris202010/yxym/refs/heads/main/ip.txt',
        'proxyip': 'https://raw.githubusercontent.com/chris202010/yxym/refs/heads/main/proxyip.txt',
    }
    
    try:
        zone_id, domain = get_cloudflare_zone(api_token)
        
        for subdomain, url in subdomain_ip_mapping.items():
            ip_list = get_ip_list(url)
            print(f"共获取 {len(ip_list)} 个IP，用于 {subdomain}.{domain}")
            delete_existing_dns_records(api_token, zone_id, subdomain, domain)
            update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain)
            
    except Exception as e:
        print(f"Error: {e}")
