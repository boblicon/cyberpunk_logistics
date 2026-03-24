import pynetlogo
import numpy as np


class NetLogoModel:

    def __init__(self):
        netlogo_path = r"X:\Games"
        jvm_path = r"C:\Program Files\Java\jdk-17\bin\server\jvm.dll"
        self.netlogo = pynetlogo.NetLogoLink(
            gui=False, netlogo_home=netlogo_path, jvm_path=jvm_path
        )
        self.netlogo.load_model("kursovaya.nlogox")

    def command(self, cmd):
        self.netlogo.command(cmd)

    def safe_report(self, query, default):
        try:
            result = self.netlogo.report(query)
            if result is None:
                return default
            if isinstance(result, np.ndarray):
                if result.size == 0:
                    return default
                return result.tolist()
            if isinstance(result, (list, tuple)):
                if len(result) == 0:
                    return default
                return list(result)
            return result
        except Exception:
            return default

    def setup(self, couriers, customers, order_rate, warehouses, speed, congestion):
        self.command(f"set num-couriers {couriers}")
        self.command(f"set num-customers {customers}")
        self.command(f"set order-rate {order_rate}")
        self.command(f"set num-warehouses {warehouses}")
        self.command(f"set courier-speed {speed}")
        self.command(f"set congestion-weight {congestion}")
        self.command("set avoid-traffic? true")
        self.command("setup")

    def set_avoid_traffic(self, value):
        self.command(f"set avoid-traffic? {'true' if value else 'false'}")

    def step(self):
        self.command("go")

    def get_stats(self):
        return {
            "delivered": self.safe_report("delivered-orders", 0),
            "avg_wait": self.safe_report("avg-wait-time", 0.0),
            "active": self.safe_report("count orders", 0)
        }

    def get_agents(self):
        return {
            "warehouses": self.safe_report("warehouses-data", []),
            "couriers": self.safe_report("couriers-data", []),
            "customers": self.safe_report("customers-data", []),
            "orders": self.safe_report("orders-data", []),
            "roads": self.safe_report("roads-data", [])
        }

    def get_couriers_status(self):
        raw = self.safe_report("couriers-status-data", [])
        if not raw:
            return []
        result = []
        for item in raw:
            try:
                parts = str(item).split(",")
                if len(parts) >= 3:
                    result.append((float(parts[0]), float(parts[1]), parts[2]))
            except (ValueError, IndexError):
                continue
        return result