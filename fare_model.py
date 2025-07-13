import numpy as np

fare_params = {
    'minibus': {'base': 5000, 'per_km': 500, 'fuel_mult': 3.6, 'traffic_mult': [500, 1000, 1500]},
    'keke': {'base': 5000, 'per_km': 500, 'fuel_mult': 1.3, 'traffic_mult': [1000, 2000, 3000]},
    'taxi': {'base': 5000, 'per_km': 500, 'fuel_mult': 2.4, 'traffic_mult': [1000, 2000, 3000]},
    'motorbike': {'base': 10000, 'per_km': 1000, 'fuel_mult': 0.6, 'traffic_mult': [200, 500, 800]},
    'paratransit bus': {'base': 5000, 'per_km': 500, 'fuel_mult': 7.8, 'traffic_mult': [500, 800, 1100]},
    'formal bus': {'base': 5000, 'per_km': 500, 'fuel_mult': 7.8, 'traffic_mult': [500, 800, 1100]},
}

traffic_index = {'low': 0, 'moderate': 1, 'heavy': 2}
weather_surcharge = {'clear': 0, 'cloudy': 100, 'rainy': 500, 'stormy': 1000}
traffic_period_surcharge = {'morning peak': 900, 'afternoon peak': 800, 'evening peak': 1000, 'off-peak': 0}
day_type_multiplier = {'weekday': 1.0, 'weekend': 1.1}

def calculate_fare(vehicle_type, distance_km, fuel_price, traffic_level,
                   weather_condition, traffic_period, day_type):
    params = fare_params[vehicle_type]
    base = params['base']
    rate = params['per_km'] * (1 + 0.05 * np.log1p(distance_km))
    dist_fare = distance_km * rate
    fuel_adj = (fuel_price - 30000) * params['fuel_mult'] / 1000
    traffic_surcharge = params['traffic_mult'][traffic_index.get(traffic_level, 1)]
    weather_adj = weather_surcharge.get(weather_condition, 0)
    period_adj = traffic_period_surcharge.get(traffic_period, 0)
    weekend_mult = day_type_multiplier.get(day_type, 1.0)

    subtotal = base + dist_fare + fuel_adj + traffic_surcharge + weather_adj + period_adj
    total = round(subtotal * weekend_mult, -2)

    breakdown = {
        "Base Fare": round(base, 2),
        "Distance Fare": round(dist_fare, 2),
        "Fuel Adjustment": round(fuel_adj, 2),
        "Traffic Surcharge": round(traffic_surcharge, 2),
        "Weather Surcharge": round(weather_adj, 2),
        "Period Surcharge": round(period_adj, 2),
        "Weekend Multiplier": weekend_mult,
        "Subtotal": round(subtotal, 2),
        "Total Fare": total
    }

    return total, breakdown