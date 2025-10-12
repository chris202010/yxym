import socket
import os
import logging
from time import sleep

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 目标域名列表
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
    # 你可以添加更多域名
]

# 检查 proxyip.txt 文件是否存在，如果存在则删除它
if os.path.exists('proxyip.txt'):
    os.remove('proxyip.txt')

# 创建一个文件来存储解析得到的 IP 地址
with open('proxyip.txt', 'w', encoding='utf-8') as file:
    for domain in domains:
        try:
            # 使用 socket 获取 IP 地址
            ip_address = socket.gethostbyname(domain)

            # 只写入 IP，不带国家代码
            file.write(f"{ip_address}\n")
            logging.info(f"{domain} -> {ip_address}")

        except socket.gaierror as e:
            logging.error(f"无法解析域名 {domain}: {e}")
            continue

        # 防止查询太快（可选）
        sleep(1)

logging.info("✅ 域名解析完成，所有 IP 已保存到 proxyip.txt（仅 IP）。")
