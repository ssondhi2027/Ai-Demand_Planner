import numpy as np

def simulate_stockout(forecast, current_inventory, simulations=1000):
    stockouts = 0
    stockout_days = []

    for _ in range(simulations):
        inventory = current_inventory
        days = 0
        for demand in forecast:
            inventory -= demand
            if inventory < 0:
                stockouts += 1
                stockout_days.append(days)
                break
            days += 1

    probability = stockouts / simulations
    avg_days = sum(stockout_days) / len(stockout_days) if stockout_days else 0

    risk = "LOW" if probability < 0.1 else "MEDIUM" if probability < 0.3 else "HIGH"

    return probability, avg_days, risk
