# oncology_differentials.py

oncology_differentials = {
    "Breast Cancer": {
        "imaging_descriptors": [
            "Mass with spiculated margins",
            "Microcalcifications",
            "Architectural distortion",
            "Nipple retraction",
            "Skin thickening",
            "Lymphadenopathy",
            "Ductal irregularities"  // Added additional descriptor
        ],
        "risk_factors": [
            "Age",
            "Family history",
            "Genetic mutations (BRCA1, BRCA2)",
            "Early menarche, late menopause",
            "Nulliparity or late first pregnancy",
            "Hormone replacement therapy",
            "Obesity",
            "Alcohol consumption"  // New risk factor in some epidemiologic studies
        ],
        "epidemiology": "Most common cancer in women worldwide; increased incidence in high-risk groups",
        "clinical_diagnostic_correlations": [
            "Palpable breast mass",
            "Nipple discharge",
            "Skin changes",
            "Lymph node enlargement",
            "Breast pain"
        ],
        "recommendations": [
            "Mammography",
            "Breast ultrasound",
            "MRI of the breast",
            "Biopsy (core needle or excisional)",
            "Sentinel lymph node biopsy",
            "Surgical resection (lumpectomy or mastectomy)",
            "Radiation therapy",
            "Chemotherapy",
            "Hormone therapy",
            "Targeted therapy",
            "Immunotherapy",
            "Molecular subtyping (e.g., HER2, ER, PR status)"  // Enhanced recommendation
        ]
    },
    "Prostate Cancer": {
        "imaging_descriptors": [
            "Peripheral zone lesion",
            "Reduced diffusion on MRI",
            "Elevated choline/citrate ratio on MR spectroscopy",
            "Bone metastases",
            "Heterogeneous signal intensity"  // Added for more detailed imaging description
        ],
        "risk_factors": [
            "Age",
            "Family history",
            "African American ethnicity",
            "High-fat diet",
            "Obesity"
        ],
        "epidemiology": "Most common cancer in men; incidence increases with age",
        "clinical_diagnostic_correlations": [
            "Elevated PSA level",
            "Urinary symptoms (frequency, urgency, nocturia)",
            "Bone pain (if metastatic)",
            "Erectile dysfunction"
        ],
        "recommendations": [
            "Prostate-specific antigen (PSA) testing",
            "Digital rectal exam (DRE)",
            "Transrectal ultrasound (TRUS) with biopsy",
            "MRI of the prostate",
            "Gleason scoring",
            "Active surveillance",
            "Radical prostatectomy",
            "Radiation therapy",
            "Hormone therapy",
            "Chemotherapy",
            "Molecular profiling"  // Added for precision medicine approaches
        ]
    },
    "Colorectal Cancer": {
        "imaging_descriptors": [
            "Polypoid lesion",
            "Annular constricting lesion",
            "Bowel wall thickening",
            "Lymph node metastases",
            "Liver metastases",
            "Peritoneal implants",
            "Mucosal irregularities"  // New descriptor
        ],
        "risk_factors": [
            "Age",
            "Family history",
            "Inflammatory bowel disease (IBD)",
            "Diet high in red and processed meat",
            "Smoking",
            "Obesity",
            "Alcohol consumption"
        ],
        "epidemiology": "Third most common cancer worldwide; screening programs reduce mortality",
        "clinical_diagnostic_correlations": [
            "Change in bowel habits",
            "Rectal bleeding",
            "Abdominal pain",
            "Weight loss",
            "Iron deficiency anemia"
        ],
        "recommendations": [
            "Colonoscopy",
            "Flexible sigmoidoscopy",
            "Fecal occult blood test (FOBT)",
            "Fecal immunochemical test (FIT)",
            "CT colonography (virtual colonoscopy)",
            "Biopsy",
            "Surgical resection",
            "Chemotherapy",
            "Radiation therapy",
            "Targeted therapy",
            "Immunotherapy"
        ]
    }
}
