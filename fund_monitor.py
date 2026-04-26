import akshare as ak
import pandas as pd
import requests

# ===================== 你只需要改这里 =====================
FUND_CODE = "023639"
DING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=441bc96240d0319dea9d65a7d7c7ab1e60e00de310f0984e47ab1726f2f93af8"
KEYWORD = "GAMBLE"  # 你设置的关键词
# ==========================================================

def get_fund_data():
    df = ak.fund_open_fund_info_em(FUND_CODE)
    df["净值日期"] = pd.to_datetime(df["净值日期"])
    df = df.sort_values("净值日期")
    df["单位净值"] = df["单位净值"].astype(float)

    # 计算 BIAS
    df["MA6"] = df["单位净值"].rolling(6).mean()
    df["BIAS_6"] = (df["单位净值"] - df["MA6"]) / df["MA6"] * 100
    return df.iloc[-1]

def send_alert(message):
    data = {
        "msgtype": "text",
        "text": {"content": f"{KEYWORD} {message}"}  # 必须带关键词
    }
    requests.post(DING_WEBHOOK, json=data)

if __name__ == "__main__":
    latest = get_fund_data()
    nav = latest["单位净值"]
    bias = latest["BIAS_6"]

    msg = f"""【基金每日监控】
基金代码：{FUND_CODE}
单位净值：{nav:.4f}
6日乖离率：{bias:.2f}%"""

    if bias < -5:
        msg += "\n⚠️ 建仓机会：乖离率低于 -5%"
    elif bias > 3:
        msg += "\n⚠️ 减仓机会：乖离率高于 3%"

    print(msg)
    send_alert(msg)