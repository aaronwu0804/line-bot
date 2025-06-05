#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/dns_fix_helper.py
"""
DNS 修復工具
此腳本嘗試使用不同的 DNS 伺服器解析特定域名，並提供診斷信息
"""

import socket
import logging
import sys
import dns.resolver  # 需要 pip install dnspython
import requests
import argparse
from time import sleep

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dns_resolution(hostname, dns_servers=None):
    """測試DNS解析是否正常工作"""
    try:
        logger.info(f"嘗試解析 {hostname}...")
        
        # 使用預設DNS
        try:
            ip = socket.gethostbyname(hostname)
            logger.info(f"系統DNS解析成功： {hostname} -> {ip}")
            return True
        except socket.gaierror as e:
            logger.error(f"系統DNS解析失敗： {hostname}, 錯誤: {str(e)}")
        
        # 嘗試使用指定的DNS伺服器
        if dns_servers:
            for dns in dns_servers:
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [dns]
                    answers = resolver.resolve(hostname, 'A')
                    for rdata in answers:
                        logger.info(f"DNS {dns} 解析成功： {hostname} -> {rdata}")
                        return True
                except Exception as e:
                    logger.error(f"使用 DNS {dns} 解析失敗： {str(e)}")
        
        return False
    except Exception as e:
        logger.error(f"解析時發生未知錯誤： {str(e)}")
        return False

def check_with_alternative_dns(hostname):
    """使用多種常用DNS伺服器嘗試解析域名"""
    dns_servers = [
        '8.8.8.8',       # Google DNS
        '8.8.4.4',       # Google DNS
        '1.1.1.1',       # Cloudflare DNS
        '1.0.0.1',       # Cloudflare DNS
        '208.67.222.222',# OpenDNS
        '168.95.1.1',    # HiNet DNS (台灣)
        '168.95.192.1'   # HiNet DNS (台灣)
    ]
    
    logger.info("=== 使用替代 DNS 伺服器嘗試解析 ===")
    for dns in dns_servers:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns]
            logger.info(f"使用 DNS {dns} 嘗試解析 {hostname}...")
            answers = resolver.resolve(hostname, 'A')
            for rdata in answers:
                logger.info(f"成功: {dns} => {hostname} -> {rdata}")
                return str(rdata)
        except Exception as e:
            logger.error(f"失敗: {dns} => {str(e)}")
    
    return None

def check_connectivity(url, timeout=10):
    """檢查是否可以連接到指定的URL"""
    try:
        logger.info(f"嘗試連接到 {url}...")
        response = requests.get(url, timeout=timeout)
        logger.info(f"連接成功: {url}, 狀態碼: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"連接失敗: {url}, 錯誤: {str(e)}")
        return False

def add_hosts_entry(hostname, ip):
    """建議添加 hosts 項目"""
    hosts_path = "/etc/hosts" if sys.platform != "win32" else r"C:\Windows\System32\drivers\etc\hosts"
    logger.info(f"建議添加以下項目到您的 hosts 檔案 ({hosts_path}):")
    logger.info(f"{ip} {hostname}")
    
    # 在 macOS/Linux 上，可以直接提供命令
    if sys.platform != "win32":
        logger.info("您可以使用以下指令添加 (需要管理員權限):")
        logger.info(f"echo '{ip} {hostname}' | sudo tee -a {hosts_path}")
    return

def show_diagnostics(hostname):
    """顯示網路診斷資訊"""
    logger.info("=== 進行網路診斷 ===")
    
    # 嘗試使用系統 DNS 解析
    try:
        ip = socket.gethostbyname(hostname)
        logger.info(f"系統 DNS 解析: {hostname} -> {ip}")
    except socket.gaierror:
        logger.info(f"系統 DNS 解析失敗: {hostname}")
        
        # 嘗試使用備用 DNS
        ip = check_with_alternative_dns(hostname)
        if ip:
            add_hosts_entry(hostname, ip)

def main():
    parser = argparse.ArgumentParser(description='DNS 解析測試與修復工具')
    parser.add_argument('--hostname', default='opendata.cwb.gov.tw',
                      help='要測試的域名 (預設: opendata.cwb.gov.tw)')
    parser.add_argument('--url', default='https://opendata.cwb.gov.tw',
                      help='要測試連接的 URL (預設: https://opendata.cwb.gov.tw)')
    args = parser.parse_args()
    
    logger.info("====== DNS 修復幫手 ======")
    hostname = args.hostname
    url = args.url
    
    # 檢查 DNS 解析
    dns_ok = check_dns_resolution(hostname)
    
    # 如果 DNS 解析失敗，進行診斷
    if not dns_ok:
        show_diagnostics(hostname)
    
    # 檢查網站連接
    conn_ok = check_connectivity(url)
    
    # 顯示結果摘要
    logger.info("====== 測試結果摘要 ======")
    logger.info(f"DNS 解析: {'成功' if dns_ok else '失敗'}")
    logger.info(f"網站連接: {'成功' if conn_ok else '失敗'}")
    
    if not dns_ok:
        logger.info("DNS 解析失敗，建議檢查網路設定或聯繫您的網路管理員")
    
    if not conn_ok and dns_ok:
        logger.info("DNS 解析正常但無法連接網站，可能是網路連接問題、防火牆設定或目標服務器異常")
    
    return dns_ok and conn_ok

if __name__ == "__main__":
    main()
