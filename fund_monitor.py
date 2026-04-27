import akshare as ak
import pandas as pd
import requests

# ===================== 【你只改这里】 =====================
DING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=441bc96240d0319dea9d65a7d7c7ab1e60e00de310f0984e47ab1726f2f93af8"
KEYWORD = "GAMBLE"

# 要监控的基金列表，想加多少加多少！
FUND_LIST = ["023639", "018173", "022167", "025491","014313","016708","024641","025422","024620","018463"]
# =========================================================

def get_fund_bias(fund_code):
    try:
        df = ak.fund_open_fund_info_em(fund_code)
        df["净值日期"] = pd.to_datetime(df["净值日期"])
        df = df.sort_values("净值日期")
        df["单位净值"] = df["单位净值"].astype(float)

        df["MA6"] = df["单位净值"].rolling(6).mean()
        df["BIAS_6"] = (df["单位净值"] - df["MA6"]) / df["MA6"] * 100
        return df.iloc[-1]
    except:
        return None

def send_all(msg):
    data = {
        "msgtype": "text",
        "text": {"content": f"{KEYWORD}\n{msg}"}
    }
    resp = requests.post(DING_WEBHOOK, json=data)
    print("发送结果：", resp.text)

if __name__ == "__main__":
    final_msg = "【基金多标的自动监控】\n"

    for code in FUND_LIST:
        data = get_fund_bias(code)
        if data is None:
            final_msg += f"\n{code} → 获取失败"
            continue

        nav = data["单位净值"]
        bias = data["BIAS_6"]
        date = data["净值日期"].strftime("%Y-%m-%d")

        final_msg += f"\n📌 {code}\n"
        final_msg += f"净值：{nav:.4f} | BIAS_6：{bias:.2f}%\n"

        # 预警
        if bias < -5:
            final_msg += "⚠️ 【建仓机会】乖离率过低\n"
        elif bias > 3:
            final_msg += "⚠️ 【减仓机会】乖离率过高\n"
        else:
            final_msg += "✅ 正常\n"

    print(final_msg)
    send_all(final_msg)
