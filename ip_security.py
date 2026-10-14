"""
ip_security.py
Encapsulated IP Address Security & Device Limiting Logic.
Features:
1. Real Mobile IP Detection (supports Streamlit Cloud, reverse proxies, and Cloudflare)
2. Single-Device / 1-IP Attendance Enforcement (1 IP = 1 Attendance per Lecture Session)
3. Regional Network Lock (India IP verification) & VPN/Proxy Detection
"""

import urllib.request                                     # for IP geolocation API
import json                                              # for parsing geo response
import streamlit as st                                    # streamlit context


# Set to True to enable IP restrictions, or False to test freely without restrictions
ENABLE_IP_SECURITY = False


PRIVATE_IP_PREFIXES = (                                   # private and localhost IP ranges
    "127.", "10.", "172.", "192.168.", "::1", "localhost"
)


def get_client_ip():
    """Extracts the real client IP address behind reverse proxies / cloud servers."""
    headers = getattr(st.context, "headers", {})
    # 1. Check X-Forwarded-For header (Streamlit Cloud, AWS ALB, Nginx)
    xff = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    # 2. Check Cloudflare header
    cf_ip = headers.get("cf-connecting-ip") or headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    # 3. Native Streamlit IP context
    ctx_ip = getattr(st.context, "ip_address", None)
    if ctx_ip:
        return str(ctx_ip).strip()
    return None


def is_private_ip(ip):
    """Checks if an IP belongs to private/local development ranges."""
    if not ip:
        return True
    for prefix in PRIVATE_IP_PREFIXES:
        if ip.startswith(prefix):
            return True
    return False


def check_ip_india_no_vpn(ip):
    """Verifies that the client IP is from India and not using a datacenter VPN/proxy."""
    if not ENABLE_IP_SECURITY:                            # bypassed if disabled
        return {"allowed": True, "reason": "disabled"}

    if is_private_ip(ip):                                 # allow local network
        return {"allowed": True, "reason": "local"}

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,proxy,hosting"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "success":
            return {"allowed": True, "reason": "api_fail"}

        if data.get("country") != "India":
            return {"allowed": False, "reason": "non_india", "country": data.get("country", "Unknown")}

        if data.get("proxy") or data.get("hosting"):
            return {"allowed": False, "reason": "vpn_proxy"}

        return {"allowed": True, "reason": "ok"}
    except Exception:
        return {"allowed": True, "reason": "api_fail"}    # fail-open on network error


def is_ip_already_used(state, client_ip):
    """Checks if the given IP has already submitted attendance for the active lecture session."""
    if not ENABLE_IP_SECURITY or not client_ip:
        return False
    return client_ip in state.get("marked_ips", {})


def register_ip_submission(state, client_ip, roll_number):
    """Records the IP mapping to prevent duplicate submissions from the same device."""
    if not client_ip:
        return
    if "marked_ips" not in state:
        state["marked_ips"] = {}
    state["marked_ips"][client_ip] = roll_number
