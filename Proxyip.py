import socket
import os
import logging
import time
from time import sleep
import urllib.request
import urllib.error

# ================== 基本配置 ==================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

domains = [
    'proxyip.fxxk.dedyn.io',
    'proxyip.us.fxxk.dedyn.io',
    'proxyip.sg.fxxk.dedyn.io',
    'proxyip.jp.fxxk.dedyn.io',
    'proxyip.hk.fxxk.dedyn.io',
    'proxyip.aliyun.fxxk.dedyn.io',
    'proxyip.oracle.fxxk.dedyn.io',
    'proxyip.digitalocean.fxxk.dedyn.io',
    'proxyip.oracle.cmliussss.net'
]

remote_url = "https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/bestproxy.txt"

OUTPUT_FILE = "proxyip.txt"
COMMON_PORTS = [80, 443, 8080, 8888, 1080]
TIMEOUT = 4

# ================== 工具函数 ==================

def check_proxy(ip, port, timeout=TIMEOUT):
    """
    检测代理类型并测速
    返回 (True, TYPE, delay_ms) 或 (False, None, None)
    """
    try:
        start = time.time()
        s = socket.create_connection((ip, port), timeout=timeout)
        s.settimeout(timeout)

        # ---- SOCKS5 探测 ----
        try:
            s.sendall(b'\x05\x01\x00')
            resp = s.recv(2)
            if resp == b'\x05\x00':
                delay = int((time.time() - start) * 1000)
                s.close()
                return True, 'SOCKS5', delay
        except Exception:
            pass

        # ---- HTTP 探测 ----
        try:
            http_req = (
                b"HEAD http://www.google.com HTTP/1.1\r\n"
                b"Host: www.google.com\r\n"
                b"Connection: close\r\n\r\n"
            )
            s.sendall(http_req)
            resp = s.recv(12)
            if b'HTTP/' in resp:
                delay = int((time.time() - start) * 1000)
                s.close()
                return True, 'HTTP', delay
        except Exception:
            pass

        s.close()
    except Exception:
        pass

    return False, None, None


def probe_proxy(ip):
    """
    探测一个 IP 的所有常见端口
    """
    for port in COMMON_PORTS:
        ok, ptype, delay = check_proxy(ip, port)
        if ok:
            logging.info(f"✅ {ip}:{port} | {ptype} | {delay}ms")
            return f"{ip}:{port}|{ptype}|{delay}ms"
    logging.warning(f"❌ 无可用代理: {ip}")
    return None


# ================== 主程序 ==================

def main():
    # 删除旧文件
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    seen_ips = set()

    logging.info("=== 开始解析域名 ===")

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as file:

        # ---- 1. 域名解析 ----
        for domain in domains:
            try:
                ip = socket.gethostbyname(domain)
                if ip in seen_ips:
                    continue
                seen_ips.add(ip)

                result = probe_proxy(ip)
                if result:
                    file.write(result + "\n")

            except socket.gaierror as e:
                logging.error(f"域名解析失败 {domain}: {e}")

            sleep(1)

        logging.info("=== 域名解析完成 ===")
        logging.info("=== 开始采集远程 IP ===")

        # ---- 2. 远程 IP ----
        try:
            with urllib.request.urlopen(remote_url, timeout=10) as resp:
                lines = resp.read().decode('utf-8').splitlines()

            logging.info(f"远程获取 {len(lines)} 条数据")

            for line in lines:
                ip = line.split(':')[0].strip()
                if not ip or ip in seen_ips:
                    continue

                seen_ips.add(ip)
                result = probe_proxy(ip)
                if result:
                    file.write(result + "\n")

        except urllib.error.URLError as e:
            logging.error(f"远程 URL 获取失败: {e}")

    logging.info("🎉 完成，结果已保存到 proxyip.txt")


# ================== 入口 ==================

if __name__ == "__main__":
    main()
