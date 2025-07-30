import json
from pathlib import Path

from tungsten import SigmaAldrichSdsParser, SdsQueryFieldName, \
    SigmaAldrichFieldMapper

sds_parser = SigmaAldrichSdsParser()
sds_path = Path(r"Y:\normie\normstelle\ats_workflow\2 pdfparser\sds\sds.pdf")

# Convert PDF file to parsed data
with open(sds_path, "rb") as f:
    sds = sds_parser.parse_to_ghs_sds(f)

field_mapper = SigmaAldrichFieldMapper()

fields = [
    SdsQueryFieldName.PRODUCT_NAME,
    SdsQueryFieldName.PRODUCT_NUMBER,
    SdsQueryFieldName.CAS_NUMBER,
    SdsQueryFieldName.PRODUCT_BRAND,
    SdsQueryFieldName.RECOMMENDED_USE_AND_RESTRICTIONS,
    SdsQueryFieldName.SUPPLIER_ADDRESS,
    SdsQueryFieldName.SUPPLIER_TELEPHONE,
    SdsQueryFieldName.SUPPLIER_FAX,
    SdsQueryFieldName.EMERGENCY_TELEPHONE,
    SdsQueryFieldName.IDENTIFICATION_OTHER,
    SdsQueryFieldName.SUBSTANCE_CLASSIFICATION,
    SdsQueryFieldName.PICTOGRAM,
    SdsQueryFieldName.SIGNAL_WORD,
    SdsQueryFieldName.STATEMENTS,
    SdsQueryFieldName.HNOC_HAZARD,
]

# Serialize parsed data to JSON and dump to a file
with open(sds_path.stem + ".json", "w") as f:
    sds.dump(f)
    # Also print out mapped fields
    for field in fields:
        print(field.name, field_mapper.get_field(field, json.loads(sds.dumps())))