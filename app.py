"""
EV Calculator API - x402付费版本
收款钱包: 0x24b288c98421d7b447c2d6a6442538d01c5fce22 (Base)
价格: 0.01 USDC/次
"""

import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI

PAYMENT_INFO = {
    "price": "0.01 USDC",
    "wallet": "0x24b288c98421d7b447c2d6a6442538d01c5fce22",
    "chain": "Base (eip155:8453)"
}


def calculate_ev(p: float, win: float, loss: float) -> float:
    """计算基础EV"""
    return p * win - (1 - p) * loss


def polymarket_ev(your_prob: float, market_price: float) -> dict:
    """计算Polymarket的EV"""
    edge = your_prob - market_price
    ev_dollar = edge / market_price if market_price > 0 else 0
    return {
        "edge": round(edge, 4),
        "edge_pct": round(edge * 100, 2),
        "ev_per_dollar": round(ev_dollar, 4)
    }


app = FastAPI(title="EV Calculator API", version="1.0.0")


@app.get("/")
@app.get("/calculate")
async def calculate(
    p: float = None,
    win: float = None,
    loss: float = None,
    market: float = None,
    your: float = None
):
    """EV计算"""
    if market is not None and your is not None:
        # Polymarket模式
        result = polymarket_ev(your, market)
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "polymarket",
            "inputs": {
                "market_price": market,
                "your_probability": your
            },
            "result": result,
            "verdict": "✅ 正期望" if result["edge"] > 0 else "❌ 负期望",
            "payment": PAYMENT_INFO
        }
    
    if p is not None and win is not None and loss is not None:
        # 基础模式
        ev = calculate_ev(p, win, loss)
        ev_pct = (ev / loss * 100) if loss > 0 else 0
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "basic",
            "inputs": {
                "win_probability": p,
                "win": win,
                "loss": loss
            },
            "result": {
                "ev": round(ev, 4),
                "ev_pct": round(ev_pct, 2)
            },
            "verdict": "✅ 正期望" if ev > 0 else "❌ 负期望" if ev < 0 else "⚪ 持平",
            "payment": PAYMENT_INFO
        }
    
    # 默认返回
    return {
        "success": True,
        "message": "EV Calculator API",
        "usage": {
            "basic": "/calculate?p=0.55&win=1.10&loss=1.00",
            "polymarket": "/calculate?market=0.40&your=0.60"
        },
        "payment": PAYMENT_INFO
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
