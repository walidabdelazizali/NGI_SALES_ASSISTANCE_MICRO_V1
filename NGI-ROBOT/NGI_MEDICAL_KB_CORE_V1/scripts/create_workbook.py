# This script creates the NGI_MEDICAL_KB_CORE_V1 Excel workbook with the required sheets and header rows.
import os
from openpyxl import Workbook

# Define absolute paths
project_folder = r"C:\NGI-ROBOT\NGI_MEDICAL_KB_CORE_V1"
workbook_folder = os.path.join(project_folder, "workbook")
workbook_path = os.path.join(workbook_folder, "NGI_MEDICAL_KB_CORE_V1.xlsx")

# Sheet names
sheet_names = [
    "README",
    "PLAN_MASTER",
    "AREA_OF_COVERAGE",
    "NETWORK_MASTER",
    "NETWORK_SPECIAL_PROVIDERS",
    "GROUP_DECLARATION_RULES",
    "INDIVIDUAL_DECLARATION_RULES",
    "PRE_EXISTING_RULES",
    "INPATIENT_BENEFITS",
    "OUTPATIENT_BENEFITS",
    "PREVENTIVE_VACCINES",
    "ADDITIONAL_BENEFITS",
    "TRAVEL_EMERGENCY_ASSIST",
    "MATERNITY",
    "ALIASES"
]

# Create workbook and sheets
wb = Workbook()
# Remove the default sheet
default_sheet = wb.active
wb.remove(default_sheet)

# Add all required sheets with a header row
for name in sheet_names:
    ws = wb.create_sheet(title=name)
    ws.append(["HEADER"])  # Placeholder header row

# Save workbook to the exact path
wb.save(workbook_path)
print(f"Workbook created at: {workbook_path}")
