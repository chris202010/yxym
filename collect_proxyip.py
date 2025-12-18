导入套接字 socket
导入操作系统模块 os
导入日志记录 logging
从时间导入睡眠 time import sleep
# 引入用于网络请求的库
导入urllib请求 urllib.request
导入urllib错误 urllib.error

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 目标域名列表 (原始数据)
域名 = [[
    'proxyip.fxxk.dedyn.io''proxyip.fxxk.dedyn.io',
    'proxyip.us.fxxk.dedyn.io''proxyip.us.fxxk.dedyn.io',
    'proxyip.sg.fxxk.dedyn.io''proxyip.sg.fxxk.dedyn.io',
    'proxyip.jp.fxxk.dedyn.io''proxyip.jp.fxxk.dedyn.io',
    'proxyip.hk.fxxk.dedyn.io''proxyip.hk.fxxk.dedyn.io',
    'proxyip.aliyun.fxxk.dedyn.io''proxyip.aliyun.fxxk.dedyn.io',
    'proxyip.oracle.fxxk.dedyn.io''proxyip.oracle.fxxk.dedyn.io',
    'proxyip цифровой океан fxxk dedyn io''proxyip.digitalocean.fxxk.dedyn.io',
    'https://raw.githubusercontent.com/chris202010/yxym/refs/heads/main/proxyip.csv',
    'proxyip.oracle.cmliussss.net''proxyip.oracle.cmliussss.net'
    # 你可以添加更多域名# 你可以添加更多域名
]

# 远程 IP 列表 URL
remote_url = "https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/bestproxy.txt"
"https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/bestproxy.txt"

# 检查 proxyip.txt 文件是否存在，如果存在则删除它
if os.path.exists('proxyip.txt'): os.path.exists('proxyip.txt'):
    os.remove('proxyip.txt')remove('proxyip.txt')

logging.info("--- 开始进行域名解析 ---")info("--- 开始进行域名解析 ---")

# 创建一个文件来存储解析得到的 IP 地址
with open('proxyip.txt', 'a', encoding='utf-8') as file: open('proxyip.txt', 'a', encoding='utf-8') as file:
    # 1. 解析硬编码的域名列表
    for domain in domains:
        try:
            # 使用 socket 获取 IP 地址
            ip_address = socket.gethostbyname(domain)

            # 只写入 IP，不带国家代码
            file.write(f"{ip_address}\n")
            logging.info(f"域名解析: {domain} -> {ip_address}")

        except socket.gaierror as e:
            logging.error(f"无法解析域名 {domain}: {e}")
            continue

        # 防止查询太快（可选）
        sleep(1)

    logging.info("--- 域名列表解析完成 ---")
    logging.info(f"--- 开始采集远程 URL 数据: {remote_url} ---")

    # 2. 从远程 URL 获取数据并写入文件
    try:
        # 使用 urllib.request.urlopen 打开 URL
        with urllib.request.urlopen(remote_url, timeout=10) as response:
            # 读取所有内容并按行分割
            remote_data = response.read().decode('utf-8')
            ip_lines = remote_data.strip().split('\n')

            logging.info(f"成功获取到 {len(ip_lines)} 条远程数据。")

            # 遍历每一行数据
            for line in ip_lines:
                # 假设 remote_url 中的文件每行就是一个 IP 地址或 IP:PORT
                # 我们只取 IP 地址部分（如果存在端口）
                ip_only = line.split(':')[0].strip()

                if ip_only: # 确保不是空行
                    # 简单验证是否是有效的 IP 地址 (可选，这里只简单写入)
                    # 为了和原始代码保持一致，这里直接写入。
                    file.write(f"{ip_only}\n")
                    logging.debug(f"远程 IP: {ip_only}") # 使用 debug 级别避免日志过多
                
    except urllib.error.URLError as e:
        logging.error(f"无法从远程 URL 获取数据 {remote_url}: {e.reason}")
    except Exception as e:
        logging.error(f"处理远程数据时发生未知错误: {e}")

    logging.info("--- 远程数据采集完成 ---")

logging.info("✅ 域名解析和远程数据采集完成，所有 IP 已保存到 proxyip.txt（仅 IP）。")
