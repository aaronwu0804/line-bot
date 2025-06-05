"""
DNS 幫助工具
提供功能：
1. 檢查 DNS 解析狀態
2. 使用不同的 DNS 伺服器嘗試解析
3. 修改系統 hosts 檔案 (需要管理員權限)
"""

import socket
import logging
import os
import platform
import subprocess
import sys
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# 常用的 DNS 伺服器
FALLBACK_DNS_SERVERS = [
    ("8.8.8.8", "Google DNS"),
    ("8.8.4.4", "Google DNS 備用"),
    ("1.1.1.1", "Cloudflare DNS"),
    ("1.0.0.1", "Cloudflare DNS 備用"),
    ("208.67.222.222", "OpenDNS"),
    ("168.95.1.1", "HiNet DNS")
]

def check_dns_resolution(hostname: str, timeout: int = 3) -> bool:
    """檢查是否可以解析指定的主機名"""
    try:
        logger.info(f"嘗試解析主機名: {hostname}")
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(hostname)
        logger.info(f"解析成功: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        logger.error(f"DNS 解析失敗: {hostname}, 錯誤: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"解析時發生未知錯誤: {str(e)}")
        return False

def try_alternate_dns_servers(hostname: str, timeout: int = 3) -> Optional[str]:
    """使用備用 DNS 伺服器嘗試解析主機名"""
    import dns.resolver  # 需要先安裝 dnspython: pip install dnspython
    
    logger.info(f"嘗試使用備用 DNS 伺服器解析: {hostname}")
    for dns_server, dns_name in FALLBACK_DNS_SERVERS:
        try:
            logger.info(f"嘗試使用 {dns_name} ({dns_server}) 解析...")
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = timeout
            resolver.lifetime = timeout
            
            answers = resolver.query(hostname, 'A')
            for rdata in answers:
                ip = rdata.address
                logger.info(f"使用 {dns_name} 解析成功: {hostname} -> {ip}")
                return ip
        except Exception as e:
            logger.error(f"使用 {dns_name} 解析失敗: {str(e)}")
    
    logger.error(f"所有備用 DNS 伺服器都解析失敗")
    return None

def add_hosts_entry(hostname: str, ip_address: str) -> bool:
    """
    添加主機名和 IP 地址對應到系統的 hosts 檔案
    注意: 此功能需要管理員權限
    """
    if platform.system() == "Windows":
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    else:  # Linux, macOS
        hosts_path = "/etc/hosts"
    
    logger.info(f"嘗試將 {hostname} -> {ip_address} 添加到 hosts 檔案")
    
    # 檢查是否有權限寫入
    if not os.access(hosts_path, os.W_OK):
        logger.error(f"無權限修改 hosts 檔案: {hosts_path}")
        logger.info("請使用管理員權限運行此腳本")
        return False
    
    try:
        # 檢查是否已存在
        with open(hosts_path, 'r') as file:
            content = file.read()
            if f"{ip_address} {hostname}" in content:
                logger.info(f"hosts 檔案中已存在 {hostname} 的對應")
                return True
        
        # 添加新條目
        with open(hosts_path, 'a') as file:
            file.write(f"\n{ip_address} {hostname} # 由 morning-post 自動添加\n")
        
        logger.info(f"成功將 {hostname} -> {ip_address} 添加到 hosts 檔案")
        return True
    except Exception as e:
        logger.error(f"修改 hosts 檔案時發生錯誤: {str(e)}")
        return False

def set_dns_server(dns_server: str) -> bool:
    """
    臨時設置系統 DNS 伺服器
    注意: 此功能需要管理員權限，並且方法因作業系統而異
    """
    system = platform.system()
    logger.info(f"嘗試設置 DNS 伺服器為 {dns_server}")
    
    try:
        if system == "Windows":
            # 需要管理員權限
            cmd = f'netsh interface ip set dns name="以太網路" static {dns_server}'
            result = subprocess.run(cmd, shell=True, check=True, text=True)
            return result.returncode == 0
        
        elif system == "Darwin":  # macOS
            # 獲取主要網路介面
            network_service = subprocess.check_output(
                "networksetup -listallnetworkservices | grep -v '*' | head -2 | tail -1", 
                shell=True, text=True
            ).strip()
            
            # 設置 DNS
            cmd = f'networksetup -setdnsservers "{network_service}" {dns_server}'
            result = subprocess.run(cmd, shell=True, check=True, text=True)
            return result.returncode == 0
            
        elif system == "Linux":
            # 根據不同 Linux 發行版可能需要不同命令
            # 這裡使用通用方法修改 resolv.conf (臨時，重啟後會重設)
            with open('/etc/resolv.conf', 'w') as f:
                f.write(f"nameserver {dns_server}\n")
            return True
            
        else:
            logger.error(f"不支援的作業系統: {system}")
            return False
            
    except subprocess.SubprocessError as e:
        logger.error(f"設置 DNS 伺服器失敗: {str(e)}")
        logger.error("請確保使用管理員權限執行")
        return False
    except Exception as e:
        logger.error(f"設置 DNS 伺服器時發生未知錯誤: {str(e)}")
        return False

def resolve_dns_issue(hostname: str = "opendata.cwb.gov.tw") -> bool:
    """
    嘗試解決 DNS 解析問題
    1. 首先檢查是否能夠正常解析
    2. 如果不行，嘗試使用備用 DNS 伺服器解析
    3. 如果成功，提示使用者修改 hosts 檔案或 DNS 設定
    """
    if check_dns_resolution(hostname):
        logger.info(f"{hostname} 可以正常解析，無需修復")
        return True
        
    logger.warning(f"{hostname} 無法解析，嘗試修復...")
    
    try:
        # 嘗試使用備用 DNS 伺服器解析
        ip = try_alternate_dns_servers(hostname)
        
        if ip:
            logger.info(f"使用備用 DNS 伺服器成功解析 {hostname} -> {ip}")
            
            # 提示用戶如何修復
            logger.info("\n=== DNS 解析問題修復建議 ===")
            logger.info(f"1. 將以下內容添加到系統 hosts 檔案:")
            logger.info(f"   {ip} {hostname}")
            logger.info("2. 或者更改系統 DNS 伺服器為 8.8.8.8 (Google DNS)")
            
            # 如果有管理員權限，嘗試自動修復
            if os.geteuid() == 0 if hasattr(os, "geteuid") else False:
                logger.info("檢測到管理員權限，嘗試自動修復...")
                if add_hosts_entry(hostname, ip):
                    logger.info("自動修復成功！")
                    return True
            
            return True  # 即使沒有自動修復，也視為成功，因為已經找到解決方案
        else:
            logger.error(f"無法解析 {hostname}，請檢查網路設定或更改 DNS 伺服器")
            return False
            
    except ImportError:
        logger.warning("缺少 dnspython 套件，無法使用備用 DNS 伺服器")
        logger.info("可以通過以下命令安裝: pip install dnspython")
        return False
    except Exception as e:
        logger.error(f"解決 DNS 問題時發生未知錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 解析命令列參數
    import argparse
    parser = argparse.ArgumentParser(description="DNS 問題修復工具")
    parser.add_argument('--hostname', default="opendata.cwb.gov.tw",
                        help='要解析的主機名')
    parser.add_argument('--dns', help='要設置的 DNS 伺服器')
    parser.add_argument('--add-hosts', action='store_true',
                        help='將解析結果添加到 hosts 檔案')
    args = parser.parse_args()
    
    if args.dns:
        set_dns_server(args.dns)
    else:
        resolve_dns_issue(args.hostname)
