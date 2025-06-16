from abc import ABC, abstractmethod

class CostComponent(ABC):
    """Abstract Base Class for different cost components in Life Cycle Cost Analysis."""

    def __init__(self, amount, category, is_initial, is_recurring, present_worth_factor):
        """
        Initialize a generic cost component.

        :param amount: Cost amount in INR
        :param category: Economic, Environmental, or Social
        :param is_initial: True if an initial cost, False if future cost
        :param is_recurring: True if recurring, False if one-time
        :param present_worth_factor: Discounting factor for future costs (present_worth_factor)
        """
        self.amount = amount
        self.category = category
        self.is_initial = is_initial
        self.is_recurring = is_recurring
        self.present_worth_factor = present_worth_factor

    @abstractmethod
    def calculate_cost(self):
        """Abstract method to be implemented by subclasses for cost calculation."""
        pass


class InitialConstructionCost(CostComponent):
    """Covers material, labor, and equipment costs for bridge construction."""

    def __init__(self, quantity, rate):
        super().__init__(amount=quantity * rate, category="Economic", is_initial=True, is_recurring=False, present_worth_factor=1.00)
        self.quantity = quantity
        self.rate = rate

    def calculate_cost(self):
        return self.quantity * self.rate * self.present_worth_factor


class InitialCarbonEmissionCost(CostComponent):
    """Calculates initial carbon emissions from material production and transport."""

    def __init__(self, material_quantity, carbon_emission_factor, carbon_cost):
        super().__init__(amount=(material_quantity * carbon_emission_factor) * carbon_cost, category="Environmental", is_initial=True, is_recurring=False, present_worth_factor=1.00)
        self.material_quantity = material_quantity
        self.carbon_emission_factor = carbon_emission_factor
        self.carbon_cost = carbon_cost

    def calculate_cost(self):
        return (self.material_quantity * self.carbon_emission_factor) * self.carbon_cost * self.present_worth_factor


class TimeCost(CostComponent):
    """Calculates economic losses due to construction delays."""

    def __init__(self, construction_cost, interest_rate, time, investment_ratio):
        cost = construction_cost * interest_rate * time * investment_ratio
        super().__init__(amount=cost, category="Economic", is_initial=True, is_recurring=False, present_worth_factor=1.00)
        self.construction_cost = construction_cost
        self.interest_rate = interest_rate
        self.time = time
        self.investment_ratio = investment_ratio

    def calculate_cost(self):
        return self.construction_cost * self.interest_rate * self.time * self.investment_ratio * self.present_worth_factor


class RoadUserCost(CostComponent):
    """Evaluates economic impact on road users due to delays and detours."""

    def __init__(self, vehicles_affected, vehicle_operation_cost, construction_time):
        cost = vehicles_affected * vehicle_operation_cost * construction_time
        super().__init__(amount=cost, category="Economic", is_initial=True, is_recurring=False, present_worth_factor=1.00)
        self.vehicles_affected = vehicles_affected
        self.vehicle_operation_cost = vehicle_operation_cost
        self.construction_time = construction_time

    def calculate_cost(self):
        return self.vehicles_affected * self.vehicle_operation_cost * self.construction_time * self.present_worth_factor


class AdditionalCarbonEmissionCost(CostComponent):
    """Accounts for increased emissions from detoured traffic during bridge work."""

    def __init__(self, vehicles_affected, reroute_distance, co2_emission_per_km, carbon_cost):
        cost = vehicles_affected * reroute_distance * co2_emission_per_km * carbon_cost
        super().__init__(amount=cost, category="Environmental", is_initial=True, is_recurring=False, present_worth_factor=1.00)
        self.vehicles_affected = vehicles_affected
        self.reroute_distance = reroute_distance
        self.co2_emission_per_km = co2_emission_per_km
        self.carbon_cost = carbon_cost

    def calculate_cost(self):
        return self.vehicles_affected * self.reroute_distance * self.co2_emission_per_km * self.carbon_cost * self.present_worth_factor


class PeriodicMaintenanceCost(CostComponent):
    """Includes expenses for routine maintenance activities."""

    def __init__(self, maintenance_cost_rate, construction_cost, discount_rate, period, design_life):
        pwf = sum(1 / ((1 + discount_rate) ** (i * period)) for i in range(1, int(design_life / period) + 1))
        cost = maintenance_cost_rate * construction_cost * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=True, present_worth_factor=pwf)
        self.maintenance_cost_rate = maintenance_cost_rate
        self.construction_cost = construction_cost
        self.discount_rate = discount_rate
        self.period = period
        self.design_life = design_life

    def calculate_cost(self):
        return self.maintenance_cost_rate * self.construction_cost * self.present_worth_factor


class PeriodicMaintenanceCarbonCost(CostComponent):
    """Calculates emissions from maintenance activities."""

    def __init__(self, material_quantity, carbon_emission_factor, carbon_cost, discount_rate, period, design_life):
        pwf = sum(1 / ((1 + discount_rate) ** (i * period)) for i in range(1, int(design_life / period) + 1))
        cost = material_quantity * carbon_emission_factor * carbon_cost * pwf
        super().__init__(amount=cost, category="Environmental", is_initial=False, is_recurring=True, present_worth_factor=pwf)
        self.material_quantity = material_quantity
        self.carbon_emission_factor = carbon_emission_factor
        self.carbon_cost = carbon_cost

    def calculate_cost(self):
        return self.material_quantity * self.carbon_emission_factor * self.carbon_cost * self.present_worth_factor


class RoutineInspectionCost(CostComponent):
    """Annual cost of inspections for structural integrity."""

    def __init__(self, quantity, rate, discount_rate, design_life):
        pwf = sum(1 / ((1 + discount_rate) ** i) for i in range(1, design_life + 1))
        cost = quantity * rate * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=True, present_worth_factor=pwf)
        self.quantity = quantity
        self.rate = rate

    def calculate_cost(self):
        return self.quantity * self.rate * self.present_worth_factor


class RepairAndRehabilitationCost(CostComponent):
    """Covers major structural repairs and retrofitting."""

    def __init__(self, repair_cost_rate, construction_cost, discount_rate, period, design_life):
        pwf = sum(1 / ((1 + discount_rate) ** (i * period)) for i in range(1, int(design_life / period) + 1))
        cost = repair_cost_rate * construction_cost * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=True, present_worth_factor=pwf)

    def calculate_cost(self):
        return self.amount


class DemolitionCost(CostComponent):
    """Costs incurred at the end of bridge life for demolition and disposal."""

    def __init__(self, demolition_rate, construction_cost, discount_rate, design_life):
        pwf = 1 / ((1 + discount_rate) ** design_life)
        cost = demolition_rate * construction_cost * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=False, present_worth_factor=pwf)

    def calculate_cost(self):
        return self.amount


class RecyclingCost(CostComponent):
    """Accounts for material salvage and repurposing costs."""

    def __init__(self, scrap_value, quantity, discount_rate, design_life):
        pwf = 1 / ((1 + discount_rate) ** design_life)
        cost = scrap_value * quantity * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=False, present_worth_factor=pwf)

    def calculate_cost(self):
        return self.amount
