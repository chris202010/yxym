import os
import sys
import requests
import argparse

# -------------------------------
# 工具函数
# -------------------------------

def get_ip_list(url):
    """获取 IP 列表（限制 20 条）"""
    response = requests.get(url)
    response.raise_for_status()
    ip_list = response.text.strip().split('\n')
    limited_list = ip_list[:20]
    if len(ip_list) > 20:
        print(f"⚠️ 警告: {url} 返回了 {len(ip_list)} 个IP，只取前20个。")
    return limited_list


def get_cloudflare_zone(api_token, target_domain):
    """获取指定域名的 Zone ID"""
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    params = {"name": target_domain}
    response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=headers, params=params)

    if response.status_code == 403:
        raise Exception("❌ 403 Forbidden：请检查 CF_API_TOKEN 是否有效并具有该域名的 Zone 权限。")

    response.raise_for_status()
    zones = response.json().get('result', [])
    if not zones:
        raise Exception(f"❌ 未找到域名 {target_domain} 的 Zone，请确认该域名在 Cloudflare 中存在且 Token 有权限。")

    return zones[0]['id'], zones[0]['name']


def delete_existing_dns_records(api_token, zone_id, subdomain, domain):
    """删除已有的 A 记录"""
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
            print(f"🗑 删除 A 记录 {record_name} → {record['id']}")


def update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain, proxied):
    """添加新的 A 记录（跳过已存在的）"""
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'

    # 获取当前已存在的记录，避免重复
    existing_ips = set()
    response = requests.get(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}',
        headers=headers
    )
    if response.status_code == 200:
        for rec in response.json().get('result', []):
            existing_ips.add(rec["content"])

    for ip in ip_list:
        if ip in existing_ips:
            print(f"⏩ 跳过已存在的 IP: {record_name} → {ip}")
            continue

        data = {
            "type": "A",
            "name": record_name,
            "content": ip,
            "ttl": 1,
            "proxied": proxied
        }
        response = requests.post(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
            json=data,
            headers=headers
        )
        if response.status_code == 200 and response.json().get("success", False):
            print(f"✅ 添加 {record_name} → {ip} (proxied={proxied})")
        else:
            print(f"❌ 添加失败: {record_name} → {ip} | {response.status_code} {response.text}")

# -------------------------------
# 主程序入口
# -------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="自动更新 Cloudflare DNS 记录（支持多域名）"
    )
    parser.add_argument("--token", required=False, help="Cloudflare API Token（也可通过环境变量 CF_API_TOKEN）")
    parser.add_argument("--domains", required=True, help="多个域名用逗号分隔，例如：38806827.xyz,myotherdomain.com")
    parser.add_argument("--proxied", default="false", help="是否启用代理（true/false），默认 false")

    args = parser.parse_args()
    api_token = args.token or os.getenv("CF_API_TOKEN")
    if not api_token:
        print("❌ 未提供 Cloudflare Token，请使用 --token 或设置环境变量 CF_API_TOKEN")
        sys.exit(1)

    proxied = args.proxied.lower() == "true"
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    subdomain_ip_mapping = {
        'bestcf': 'https://ipdb.030101.xyz/api/bestcf.txt',
        'api': 'https://raw.githubusercontent.com/chris202010/yxym/refs/heads/main/ip.txt',
        'proxyip': 'https://raw.githubusercontent.com/chris202010/yxym/refs/heads/main/proxyip.txt',
    }

    print(f"🔧 使用代理: {proxied}")
    print(f"🌍 目标域名: {', '.join(domains)}")

    try:
        for domain_name in domains:
            zone_id, domain = get_cloudflare_zone(api_token, domain_name)
            print(f"\n🌐 处理域名 {domain} (Zone ID: {zone_id})")

            for subdomain, url in subdomain_ip_mapping.items():
                ip_list = get_ip_list(url)
                print(f"📦 获取到 {len(ip_list)} 个 IP 用于 {subdomain}.{domain}")
                delete_existing_dns_records(api_token, zone_id, subdomain, domain)
                update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain, proxied)

    except Exception as e:
        print(f"🚨 Error: {e}")


if __name__ == "__main__":
    main()
