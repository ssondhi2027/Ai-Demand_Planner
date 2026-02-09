import numpy as np
from scipy.stats import norm

def calculate_reorder_point(demand_mean, demand_std, lead_time, service_level):
    z = norm.ppf(service_level)
    safety_stock = int(z * demand_std * (lead_time ** 0.5))
    reorder_point = int(demand_mean * lead_time + safety_stock)

    return reorder_point, safety_stock