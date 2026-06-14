"""
ai_api.py - 统一 LLM API 调用层
支持 OpenAI 兼容协议，用户可自由配置 endpoint / key / model
"""
import json
import requests

from PySide6.QtCore import QSettings


SETTINGS_ORG = "印流PDflow"
SETTINGS_APP = "印流PDflow"

# 默认配置
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 60


def _get_settings():
    return QSettings(SETTINGS_ORG, SETTINGS_APP)


def get_api_config():
    """读取 API 配置"""
    s = _get_settings()
    return {
        "base_url": s.value("ai/base_url", DEFAULT_BASE_URL),
        "api_key": s.value("ai/api_key", ""),
        "model": s.value("ai/model", DEFAULT_MODEL),
        "timeout": int(s.value("ai/timeout", DEFAULT_TIMEOUT)),
    }


def save_api_config(base_url, api_key, model, timeout=DEFAULT_TIMEOUT):
    """保存 API 配置到 QSettings（PySide6 在 Windows 上使用注册表，相对安全）"""
    s = _get_settings()
    s.setValue("ai/base_url", base_url.rstrip("/"))
    s.setValue("ai/api_key", api_key)
    s.setValue("ai/model", model)
    s.setValue("ai/timeout", str(timeout))


def is_api_configured():
    """检查是否已配置 API Key"""
    cfg = get_api_config()
    return bool(cfg["api_key"])


def call_llm(messages, stream=False, timeout=None):
    """
    调用 LLM API（OpenAI 兼容格式）
    
    参数:
        messages: list[dict]，格式 [{"role": "user", "content": "..."}]
        stream: 是否流式返回
        timeout: 超时秒数
    
    返回:
        str: 模型返回的文本内容
    
    抛出:
        ConnectionError: 网络连接失败
        ValueError: API Key 未配置或返回错误
        TimeoutError: 请求超时
    """
    cfg = get_api_config()
    api_key = cfg["api_key"]
    if not api_key:
        raise ValueError("请先在「AI 设置」中配置 API Key")

    base_url = cfg["base_url"]
    model = cfg["model"]
    timeout = timeout or cfg["timeout"]

    # 构造请求
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        raise TimeoutError(f"连接超时（{timeout}秒），请检查网络或 API 地址")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"无法连接到 {base_url}，请检查 API 地址是否正确")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"网络请求失败: {e}")

    if resp.status_code == 401:
        raise ValueError("API Key 无效或已过期，请在「AI 设置」中重新配置")
    elif resp.status_code == 404:
        raise ValueError(f"模型 '{model}' 不存在，请检查模型名称")
    elif resp.status_code == 429:
        raise ValueError("请求频率过高，请稍后重试")
    elif resp.status_code != 200:
        try:
            err_detail = resp.json().get("error", {}).get("message", resp.text)
        except Exception:
            err_detail = resp.text[:200]
        raise ValueError(f"API 返回错误 ({resp.status_code}): {err_detail}")

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise ValueError(f"解析 API 返回数据失败: {e}")


def test_connection():
    """测试 API 连接是否正常，返回 (成功: bool, 消息: str)"""
    try:
        result = call_llm([
            {"role": "user", "content": "请回复「连接成功」四个字，不要多说"}
        ], timeout=15)
        return True, f"连接成功！模型返回: {result[:50]}"
    except (ValueError, ConnectionError, TimeoutError) as e:
        return False, str(e)
    except Exception as e:
        return False, f"未知错误: {e}"