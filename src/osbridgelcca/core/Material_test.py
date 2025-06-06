#Material Test

import copy

# Base template for material costs
MATERIAL_COSTS_TEMPLATE = {
    "concrete": {
        "units": ["cum", "kg"],
        "types": {
            "M15": {"cum": 0.0, "kg": 0.0},
            "M20": {"cum": 0.0, "kg": 0.0},
            "M25": {"cum": 0.0, "kg": 0.0},
            "M30": {"cum": 0.0, "kg": 0.0},
            "M35": {"cum": 0.0, "kg": 0.0},
            "M40": {"cum": 0.0, "kg": 0.0},
            "M45": {"cum": 0.0, "kg": 0.0},
            "M50": {"cum": 0.0, "kg": 0.0},
        }
    },
    "steel": {
        "units": ["MT", "kg"],
        "types": {
            "E 165(Fe 290)": {"MT": 0.0, "kg": 0.0},
            "E 250(Fe 410W)A": {"MT": 0.0, "kg": 0.0},
            "E 250(Fe 410W)B": {"MT": 0.0, "kg": 0.0},
            "E 250(Fe 410)C": {"MT": 0.0, "kg": 0.0},
            "E 300(Fe 440)": {"MT": 0.0, "kg": 0.0},
            "E 350(Fe 490)": {"MT": 0.0, "kg": 0.0},
            "E 410(Fe 540)": {"MT": 0.0, "kg": 0.0},
            "E 450(Fe 570)D": {"MT": 0.0, "kg": 0.0},
        }
    },
    "mastic asphalt": {
        "units": ["sqm"],
        "types": {
            "default": {"sqm": 0.0}
        }
    },
    "paint": {
        "units": ["ltr"],
        "types": {
            "white/yellow": {"ltr": 0.0},
            "primer_epoxy": {"ltr": 0.0},
            "oil": {"ltr": 0.0},
            "alluminium": {"ltr": 0.0}
        }
    },
    "paver blocks": {
        "units": ["sqm"],
        "types": {
            "default": {"sqm": 0.0}
        }
    },
}


def get_material_cost_template():
    return copy.deepcopy(MATERIAL_COSTS_TEMPLATE)

# Basic accessors
def get_materials(material_costs):
    return list(material_costs.keys())

def get_submaterials(material_costs, material):
    return list(material_costs.get(material, {}).get("types", {}).keys())

def get_units(material_costs, material):
    return material_costs.get(material, {}).get("units", [])

def get_material_cost(material_costs, material, submaterial, unit):
    return material_costs.get(material, {}).get("types", {}).get(submaterial, {}).get(unit, None)

# Safe setter: returns True on success, False if invalid keys
def set_material_cost(material_costs, material, submaterial, unit, cost):
    types = material_costs.get(material, {}).get("types", {})
    if submaterial in types and unit in types[submaterial]:
        types[submaterial][unit] = cost
        return True
    return False

# Validation helpers (good for UI input validation)
def is_valid_material(material_costs, material):
    return material in material_costs

def is_valid_submaterial(material_costs, material, submaterial):
    return submaterial in material_costs.get(material, {}).get("types", {})

def is_valid_unit(material_costs, material, unit):
    return unit in material_costs.get(material, {}).get("units", [])

# UI-friendly utility: returns all (material, submaterial, unit) combinations
def get_all_material_unit_combinations(material_costs):
    combinations = []
    for material, data in material_costs.items():
        for sub, units in data.get("types", {}).items():
            for unit in units:
                combinations.append((material, sub, unit))
    return combinations
