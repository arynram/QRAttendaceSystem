import urllib.request                                     # for IP geolocation API
import json                                              # for parsing geo response
import streamlit as st                                    # streamlit context

ENABLE_IP_SECURITY = False                                # toggle flag for ip security enforcement
PRIVATE_IP_PREFIXES = ("127.", "10.", "172.", "192.168.", "::1", "localhost") # local ip ranges


def get_client_ip():
    headers = getattr(st.context, "headers", {})          # request headers
    xff = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For") # proxy header
    if xff:
        return xff.split(",")[0].strip()                  # extract client ip
    cf_ip = headers.get("cf-connecting-ip") or headers.get("CF-Connecting-IP") # cloudflare header
    if cf_ip:
        return cf_ip.strip()                              # extract cloudflare client ip
    ctx_ip = getattr(st.context, "ip_address", None)      # native streamlit context
    if ctx_ip:
        return str(ctx_ip).strip()                        # extract context ip
    return None


def is_private_ip(ip):
    if not ip:
        return True
    for prefix in PRIVATE_IP_PREFIXES:
        if ip.startswith(prefix):
            return True                                   # matches private ip prefix
    return False


def check_ip_india_no_vpn(ip):
    if not ENABLE_IP_SECURITY:
        return {"allowed": True, "reason": "disabled"}   # security bypassed

    if is_private_ip(ip):
        return {"allowed": True, "reason": "local"}      # allow local development

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,proxy,hosting" # geolocation endpoint
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}) # request object
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())       # parse json response

        if data.get("status") != "success":
            return {"allowed": True, "reason": "api_fail"}

        if data.get("country") != "India":
            return {"allowed": False, "reason": "non_india", "country": data.get("country", "Unknown")}

        if data.get("proxy") or data.get("hosting"):
            return {"allowed": False, "reason": "vpn_proxy"} # block vpn or datacenter proxy

        return {"allowed": True, "reason": "ok"}
    except Exception:
        return {"allowed": True, "reason": "api_fail"}    # fail-open on network error


def is_ip_already_used(state, client_ip):
    if not ENABLE_IP_SECURITY or not client_ip:
        return False
    return client_ip in state.get("marked_ips", {})       # check if ip already marked


def register_ip_submission(state, client_ip, roll_number):
    if not client_ip:
        return
    if "marked_ips" not in state:
        state["marked_ips"] = {}                          # initialize ip map
    state["marked_ips"][client_ip] = roll_number          # map ip to roll number
