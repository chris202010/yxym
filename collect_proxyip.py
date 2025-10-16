import socket
import os
import logging
from time import sleep
import urllib.request
import urllib.error

# ==========================
# 基本配置
# ==========================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

domains = [
    'proxyip.fxxk.dedyn.io',
    'proxyip.us.fxxk.dedyn.io',
    'proxyip.sg.fxxk.dedyn.io',
    'proxyip.jp.fxxk.dedyn.io',
    'proxyip.hk.fxxk.dedyn.io',
    'proxyip.aliyun.fxxk.dedyn.io',
    'proxyip.oracle.fxxk.dedyn.io',
    'proxyip.digitalocean.fxxk.dedyn.io',
    'proxyip.oracle.cmliussss.net',
    'tp50000.kr.proxyip.fgfw.eu.org:50000'
]

DEFAULT_PORT = 443
remote_url = "https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/bestproxy.txt"
output_file = "proxyip.txt"

# ==========================
# 工具函数
# ==========================

def is_port_open(ip: str, port: int, timeout: float = 0.5) -> bool:
    """检测端口是否开放"""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

# ==========================
# 主逻辑
# ==========================

# 删除旧文件
if os.path.exists(output_file):
    os.remove(output_file)

logging.info("--- 开始进行域名解析 ---")

ip_set = set()  # 用于去重

with open(output_file, 'a', encoding='utf-8') as file:

    # 1️⃣ 域名解析部分
    for domain in domains:
        try:
            ip_address = socket.gethostbyname(domain)
            ip_port = f"{ip_address}:{DEFAULT_PORT}"

            if ip_port not in ip_set:
                # 检测端口是否可用
                if is_port_open(ip_address, DEFAULT_PORT):
                    file.write(f"{ip_port}\n")
                    ip_set.add(ip_port)
                    logging.info(f"✅ 域名解析成功: {domain} -> {ip_port} (端口可用)")
                else:
                    logging.warning(f"⚠️ 域名解析成功但端口不可用: {domain} -> {ip_port}")
        except socket.gaierror as e:
            logging.error(f"无法解析域名 {domain}: {e}")
        sleep(1)

    logging.info("--- 域名解析完成 ---")
    logging.info(f"--- 开始采集远程 URL 数据: {remote_url} ---")

    # 2️⃣ 远程 IP 列表部分
    try:
        with urllib.request.urlopen(remote_url, timeout=10) as response:
            remote_data = response.read().decode('utf-8')
            ip_lines = remote_data.strip().split('\n')

            logging.info(f"成功获取到 {len(ip_lines)} 条远程数据。")

            for line in ip_lines:
                line = line.strip()
                if not line:
                    continue

                # 拆分 IP 和端口
                parts = line.split(':')
                ip = parts[0]
                port = int(parts[1]) if len(parts) > 1 else DEFAULT_PORT
                ip_port = f"{ip}:{port}"

                if ip_port not in ip_set:
                    if is_port_open(ip, port):
                        file.write(f"{ip_port}\n")
                        ip_set.add(ip_port)
                        logging.debug(f"✅ 添加远程 IP: {ip_port}")
                    else:
                        logging.debug(f"⛔ 跳过端口不可用: {ip_port}")

    except urllib.error.URLError as e:
        logging.error(f"无法从远程 URL 获取数据 {remote_url}: {e.reason}")
    except Exception as e:
        logging.error(f"处理远程数据时发生未知错误: {e}")

logging.info(f"✅ 完成！共收集 {len(ip_set)} 个有效 IP:端口，已保存到 {output_file}")
