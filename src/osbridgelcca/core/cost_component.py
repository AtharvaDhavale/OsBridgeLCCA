from abc import ABC, abstractmethod
from .cost_defaults import (
    get_carbon_emission_factor,
    get_social_cost_of_carbon,
    get_coefficient_carbon_emissions_concrete,
    get_carbon_emission_factor_per_km,
    get_coefficient_embodied_energy_hysd_steel,
    get_coefficient_carbon_emissions_structural_steel,
    get_periodic_maintenance_cost_rate,  # eg (default)
    get_annual_routine_inspection_cost_rate,  # eg (default)
    get_repair_and_rehabilitation_cost_rate,  # eg (default)
    get_periodic_maintenance_frequency_years,
    get_routine_inspection_frequency_years,
    get_demolition_cost_rate,
    get_scrap_value_structural_steel,
    get_structural_steel_scrap_rate
)
from .material_types_consts import (
    get_material_cost_template, get_materials, get_grades, get_units,
    is_valid_material, is_valid_grade, is_valid_unit
)

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
        amount = (material_quantity * carbon_emission_factor) * carbon_cost
        super().__init__(amount=amount, category="Environmental", is_initial=True, is_recurring=False, present_worth_factor=1.00)
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

    def __init__(self, maintenance_cost_rate, construction_cost, discount_rate=0, period=None, design_life=1):
        if period is None:
            period = get_periodic_maintenance_frequency_years()
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

    def __init__(self, material_quantity, carbon_emission_factor, carbon_cost, discount_rate=0.0, period=1, design_life=1):
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

    def __init__(self, quantity, rate, discount_rate=0, design_life=1, period=None):
        if period is None:
            period = get_routine_inspection_frequency_years()
        pwf = sum(1 / ((1 + discount_rate) ** (i * period)) for i in range(1, int(design_life / period) + 1))
        cost = quantity * rate * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=True, present_worth_factor=pwf)
        self.quantity = quantity
        self.rate = rate
        self.period = period
        self.discount_rate = discount_rate
        self.design_life = design_life

    def calculate_cost(self):
        return self.quantity * self.rate * self.present_worth_factor


class RepairAndRehabilitationCost(CostComponent):
    """Covers major structural repairs and retrofitting."""

    def __init__(self, repair_cost_rate, construction_cost=0, discount_rate=0, period=None, design_life=1):
        if period is None:
            period = get_periodic_maintenance_frequency_years()
        pwf = sum(1 / ((1 + discount_rate) ** (i * period)) for i in range(1, int(design_life / period) + 1))
        cost = repair_cost_rate * construction_cost * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=True, present_worth_factor=pwf)

    def calculate_cost(self):
        return self.amount


class DemolitionCost(CostComponent):
    """Costs incurred at the end of bridge life for demolition and disposal."""

    def __init__(self, demolition_rate, construction_cost=0, discount_rate=0, design_life=1):
        pwf = 1 / ((1 + discount_rate) ** design_life)
        cost = demolition_rate * construction_cost * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=False, present_worth_factor=pwf)
        self.demolition_rate = demolition_rate
        self.construction_cost = construction_cost
        self.discount_rate = discount_rate
        self.design_life = design_life

    def calculate_cost(self):
        return self.amount


class RecyclingCost(CostComponent):
    """Accounts for material salvage and repurposing costs."""

    def __init__(self, scrap_value, quantity=0, scrap_rate=None, discount_rate=0, design_life=1):
        if scrap_rate is None:
            scrap_rate = get_structural_steel_scrap_rate()
        pwf = 1 / ((1 + discount_rate) ** design_life)
        cost = scrap_value * quantity * scrap_rate * pwf
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=False, present_worth_factor=pwf)
        self.scrap_value = scrap_value
        self.quantity = quantity
        self.scrap_rate = scrap_rate
        self.discount_rate = discount_rate
        self.design_life = design_life

    def calculate_cost(self):
        return self.amount


class ReconstructionCost(CostComponent):
    """Accounts for partial or complete reconstruction of the bridge due to structural failures or obsolescence."""

    def __init__(self, demolition_cost, reconstruction_cost, reconstruction_carbon_cost, reconstruction_time_cost, reconstruction_roaduser_cost, reconstruction_rerouting_carbon_cost, design_life, discount_rate):
        pwf = 1 / ((1 + discount_rate) ** design_life)
        cost = (demolition_cost + reconstruction_cost + reconstruction_carbon_cost + reconstruction_time_cost + reconstruction_roaduser_cost + reconstruction_rerouting_carbon_cost) * pwf 
        super().__init__(amount=cost, category="Economic", is_initial=False, is_recurring=False, present_worth_factor=pwf)

    def calculate_cost(self):
        return self.amount


#COST CALULATIONS 

# For Initial Construction Cost Calculation


if __name__ == "__main__":
    from .cost_defaults import get_annual_routine_inspection_cost_rate

    material_costs = get_material_cost_template()

    # user inputs will be here, for eg:
    user_materials = [
        {"material": "concrete", "grade": "M40", "unit": "cum", "quantity": 214, "rate": 11994},  # eg (quantity: cum, rate: INR/cum)
        {"material": "steel", "grade": "E 250(Fe 410W)A", "unit": "MT", "quantity": 27.99, "rate": 91565},  # eg (quantity: MT, rate: INR/MT)
        {"material": "steel", "grade": "E 300(Fe 440)", "unit": "MT", "quantity": 5.69, "rate": 185100},  # eg (quantity: MT, rate: INR/MT)     
    ]

    # 1. Initial Construction Cost Calculation
    total_initial_construction_cost = 0
    for item in user_materials:
        component = InitialConstructionCost(
            quantity=item["quantity"],
            rate=item["rate"]
        )
        total_initial_construction_cost += component.calculate_cost()
    print("Total Initial Construction Cost:", total_initial_construction_cost)  # INR

    # 2. Initial Carbon Emission Cost Calculation (Concrete + Steel)
    total_concrete_kg = 0
    for item in user_materials:
        if item["material"] == "concrete":
            qty = item["quantity"]
            unit = item["unit"].lower()
            if unit == "cum":
                qty = qty * 2549.25  # eg (density: kg/cum)
            # If already in kg, use as is
            total_concrete_kg += qty
    concrete_emission_factor = get_carbon_emission_factor("Concrete (M25)")  # eg (default, kgCO2e/kg)
    total_steel_kg = 0
    for item in user_materials:
        if item["material"] == "steel":
            qty = item["quantity"]
            unit = item["unit"].upper()
            if unit == "MT":
                qty = qty * 1000  # eg (1 MT = 1000 kg)
            # If already in kg, use as is
            total_steel_kg += qty
    steel_emission_factor = get_carbon_emission_factor("Rebar")  # eg (default, kgCO2e/kg)
    carbon_cost = get_social_cost_of_carbon()  # eg (default, INR/kg)
    total_carbon_emission_cost = (
        (total_concrete_kg * concrete_emission_factor) + (total_steel_kg * steel_emission_factor)
    ) * carbon_cost
    print("Total Initial Carbon Emission Cost:", total_carbon_emission_cost)  # INR

    # 3. Time Cost Calculation
    interest_rate = 0.1  # eg (fraction)
    time = 0.75  # eg (years)
    investment_ratio = 0.5  # eg (fraction)
    time_cost_component = TimeCost(
        construction_cost=total_initial_construction_cost,
        interest_rate=interest_rate,
        time=time,
        investment_ratio=investment_ratio
    )
    print("Time Cost:", time_cost_component.calculate_cost())  # INR

    # 4. Road User Cost Calculation
    # User defines vehicle types, lane type, roughness, and RF
    from osbridgelcca.core.cost_defaults import get_vehicle_types, get_lane_types, get_roughness_values, get_rf_values

    # Example user input (can be replaced by actual UI/db input)
    user_vehicle_data = [
        {"type": "Small Car", "count": 500, "operation_cost": 5.5},
        {"type": "Bus", "count": 100, "operation_cost": 15.0},
        # ... add more as needed
    ]
    lane_type = "Two Lane"  # user input
    roughness = 3000        # user input
    rf = 10                 # user input

    # If user does not define vehicle types, default to Big Car
    if not user_vehicle_data:
        user_vehicle_data = [{"type": "Big Car", "count": 1, "operation_cost": 6.62}]

    # Sum total road user cost for all vehicle types
    total_road_user_cost = 0
    total_vehicles_affected = 0
    for v in user_vehicle_data:
        total_road_user_cost += v["count"] * v["operation_cost"]
        total_vehicles_affected += v["count"]

    construction_time_days = time * 365  # eg (days)
    total_road_user_cost *= construction_time_days

    road_user_cost_component = RoadUserCost(
        vehicles_affected=total_vehicles_affected,  # user-defined count
        vehicle_operation_cost=total_road_user_cost / construction_time_days if construction_time_days else 0,
        construction_time=construction_time_days
    )
    print("Road User Cost (all vehicle types):", road_user_cost_component.calculate_cost())  # INR

    # 5. Additional Carbon Emission Cost Calculation
    reroute_distance = 2  # eg (km)
    co2_emission_per_km = get_carbon_emission_factor_per_km()  # eg (default, kgCO2e/km)
    additional_carbon_emission_component = AdditionalCarbonEmissionCost(
        vehicles_affected=total_vehicles_affected,
        reroute_distance=reroute_distance,
        co2_emission_per_km=co2_emission_per_km,
        carbon_cost=carbon_cost
    )
    print("Additional Carbon Emission Cost:", additional_carbon_emission_component.calculate_cost())  # INR

    # 6. Periodic Maintenance Cost Calculation
    maintenance_cost_rate = get_periodic_maintenance_cost_rate()  # eg (default, fraction)
    period = get_periodic_maintenance_frequency_years()  # eg (default, years)
    discount_rate = 0.05  # eg (fraction)
    design_life = 50  # eg (years)
    periodic_maintenance_component = PeriodicMaintenanceCost(
        maintenance_cost_rate=maintenance_cost_rate,
        construction_cost=total_initial_construction_cost,
        discount_rate=discount_rate,
        period=period,
        design_life=design_life
    )
    print("Periodic Maintenance Cost:", periodic_maintenance_component.calculate_cost())  # INR

    # 7. Periodic Maintenance Carbon Emission Cost Calculation
    maintenance_concrete_kg = total_concrete_kg
    maintenance_steel_kg = total_steel_kg
    maintenance_concrete_emission_factor = get_carbon_emission_factor("Concrete (M25)")  # eg (default, kgCO2e/kg)
    maintenance_steel_emission_factor = get_carbon_emission_factor("Rebar")  # eg (default, kgCO2e/kg)
    maintenance_carbon_cost = get_social_cost_of_carbon()  # eg (default, INR/kg)
    maintenance_discount_rate = 0.05  # eg (fraction)
    maintenance_period = get_periodic_maintenance_frequency_years()  # eg (default, years)
    maintenance_design_life = 50  # eg (years)
    pwf = sum(1 / ((1 + maintenance_discount_rate) ** (i * maintenance_period)) for i in range(1, int(maintenance_design_life / maintenance_period) + 1))
    periodic_maintenance_carbon_cost = (
        (maintenance_concrete_kg * maintenance_concrete_emission_factor) +
        (maintenance_steel_kg * maintenance_steel_emission_factor)
    ) * maintenance_carbon_cost * pwf
    print("Periodic Maintenance Carbon Emission Cost:", periodic_maintenance_carbon_cost)  # INR

    # 8. Annual Routine Inspection Cost Calculation
    inspection_rate = get_annual_routine_inspection_cost_rate()  # eg (default, fraction)
    inspection_discount_rate = 0.05  # eg (fraction)
    inspection_design_life = 50  # eg (years)
    inspection_period = 1  # eg (annual)
    total_routine_inspection_cost = 0
    for item in user_materials:
        inspection_component = RoutineInspectionCost(
            quantity=item["quantity"],
            rate=inspection_rate,
            discount_rate=inspection_discount_rate,
            design_life=inspection_design_life,
            period=inspection_period
        )
        cost = inspection_component.calculate_cost()
        total_routine_inspection_cost += cost
    print("Total Routine Inspection Cost:", total_routine_inspection_cost)  # INR

    # 9. Repair and Rehabilitation Cost Calculation
    repair_cost_rate = get_repair_and_rehabilitation_cost_rate()  # eg (default, fraction)
    repair_period = get_periodic_maintenance_frequency_years()  # eg (default, years)
    repair_component = RepairAndRehabilitationCost(
        repair_cost_rate=repair_cost_rate,
        construction_cost=total_initial_construction_cost,
        discount_rate=discount_rate,
        period=repair_period,
        design_life=design_life
    )
    print("Repair and Rehabilitation Cost:", repair_component.calculate_cost())  # INR

    # 10. Demolition and Disposal Cost Calculation
    demolition_rate = get_demolition_cost_rate()  # eg (default, fraction)
    demolition_discount_rate = 0.05  # eg (fraction)
    demolition_design_life = 50  # eg (years)
    demolition_component = DemolitionCost(
        demolition_rate=demolition_rate,
        construction_cost=total_initial_construction_cost,
        discount_rate=demolition_discount_rate,
        design_life=demolition_design_life
    )
    print("Demolition and Disposal Cost:", demolition_component.calculate_cost())  # INR

    # 11. Recycling Cost Calculation
    scrap_value = get_scrap_value_structural_steel()  # eg (default, INR/MT)
    scrap_rate = get_structural_steel_scrap_rate()  # eg (default, fraction)
    recycling_discount_rate = 0.05  # eg (fraction)
    recycling_design_life = 50  # eg (years)

    # For demonstration, assuming user provides both quantity and unit
    user_input_steel_quantity = 15  # eg (user input, 15 MT)
    user_input_steel_unit = "MT"   # eg (user input, can be 'MT' or 'kg')

    # Convert all user input to kg
    if user_input_steel_unit.upper() == "MT":
        user_input_steel_quantity_kg = user_input_steel_quantity * 1000  # 1 MT = 1000 kg
    else:
        user_input_steel_quantity_kg = user_input_steel_quantity  # already in kg

    recycling_component = RecyclingCost(
        scrap_value=scrap_value,
        quantity=user_input_steel_quantity_kg,
        scrap_rate=scrap_rate,
        discount_rate=recycling_discount_rate,
        design_life=recycling_design_life
    )
    print("Recycling Cost (user-input steel only):", recycling_component.calculate_cost())  # INR

    # 12. Reconstruction Cost Calculation 
    demolition_cost = demolition_component.calculate_cost()  # eg (INR, use previously calculated demolition cost)
    reconstruction_cost = total_initial_construction_cost  # eg (INR)
    reconstruction_carbon_cost = total_carbon_emission_cost  # eg (INR)
    reconstruction_time_cost = time_cost_component.calculate_cost()  # eg (INR)
    reconstruction_roaduser_cost = road_user_cost_component.calculate_cost()  # eg (INR)
    reconstruction_rerouting_carbon_cost = additional_carbon_emission_component.calculate_cost()  # eg (INR)
    reconstruction_design_life = 50  # eg (years)
    reconstruction_discount_rate = 0.05  # eg (fraction)
    reconstruction_component = ReconstructionCost(
        demolition_cost=demolition_cost,
        reconstruction_cost=reconstruction_cost,
        reconstruction_carbon_cost=reconstruction_carbon_cost,
        reconstruction_time_cost=reconstruction_time_cost,
        reconstruction_roaduser_cost=reconstruction_roaduser_cost,
        reconstruction_rerouting_carbon_cost=reconstruction_rerouting_carbon_cost,
        design_life=reconstruction_design_life,
        discount_rate=reconstruction_discount_rate
    )
    print("Reconstruction Cost:", reconstruction_component.calculate_cost())  # INR











