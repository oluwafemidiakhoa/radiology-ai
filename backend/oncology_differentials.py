# oncology_differentials.py
# Advanced Oncology Differential Diagnosis Dictionary
# This file outlines detailed imaging descriptors, risk factors, epidemiology, clinical correlations,
# and recommendations for major cancers with the latest insights from recent literature.

oncology_differentials = {
    "Breast Cancer": {
        "imaging_descriptors": [
            "Mass with spiculated margins",
            "Microcalcifications",
            "Architectural distortion",
            "Nipple retraction",
            "Skin thickening",
            "Lymphadenopathy",
<<<<<<< HEAD
            "Ductal irregularities"  # Added for subtle presentations
=======
            "Ductal irregularities"  # Added additional descriptor
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
        ],
        "risk_factors": [
            "Age",
            "Family history",
            "Genetic mutations (BRCA1, BRCA2)",
            "Early menarche, late menopause",
            "Nulliparity or late first pregnancy",
            "Hormone replacement therapy",
            "Obesity",
<<<<<<< HEAD
            "Alcohol consumption"
        ],
        "epidemiology": "Most common cancer in women worldwide; incidence is increasing in high-risk populations.",
=======
            "Alcohol consumption"  # New risk factor in some studies
        ],
        "epidemiology": "Most common cancer in women worldwide; increased incidence in high-risk populations.",
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
        "clinical_diagnostic_correlations": [
            "Palpable breast mass",
            "Nipple discharge",
            "Skin changes",
            "Lymph node enlargement",
            "Breast pain"
        ],
        "recommendations": [
            "Mammography and digital breast tomosynthesis",
            "Breast ultrasound",
            "MRI of the breast for high-risk screening",
            "Image-guided core needle biopsy",
            "Sentinel lymph node biopsy for staging",
            "Surgical resection (lumpectomy/mastectomy)",
            "Radiation therapy",
            "Chemotherapy",
            "Hormone therapy",
            "Targeted therapy",
            "Immunotherapy",
<<<<<<< HEAD
            "Molecular subtyping (HER2, ER, PR testing)"
        ],
        "recent_research": "Emerging liquid biopsy techniques and AI-enhanced imaging are revolutionizing early detection and personalized treatment.",
        "ml_insights": "Machine learning models now accurately predict tumor receptor status from imaging alone."
=======
            "Molecular subtyping (e.g., HER2, ER, PR status)"  # Enhanced recommendation
        ]
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
    },
    "Prostate Cancer": {
        "imaging_descriptors": [
            "Peripheral zone lesion",
            "Reduced diffusion on MRI",
            "Elevated choline/citrate ratio on MR spectroscopy",
            "Bone metastases",
<<<<<<< HEAD
            "Heterogeneous signal intensity"
=======
            "Heterogeneous signal intensity"  # Added advanced imaging descriptor
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
        ],
        "risk_factors": [
            "Age",
            "Family history",
            "African American ethnicity",
            "High-fat diet",
            "Obesity"
        ],
<<<<<<< HEAD
        "epidemiology": "Most common cancer in men; risk increases significantly with age.",
=======
        "epidemiology": "Most common cancer in men; incidence increases with age.",
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
        "clinical_diagnostic_correlations": [
            "Elevated PSA",
            "Urinary symptoms (frequency, urgency, nocturia)",
            "Bone pain (in metastatic cases)",
            "Erectile dysfunction"
        ],
        "recommendations": [
            "PSA testing",
            "Digital rectal exam (DRE)",
            "Transrectal ultrasound (TRUS) with biopsy",
            "MRI of the prostate",
            "Gleason scoring for risk stratification",
            "Active surveillance for low-risk disease",
            "Radical prostatectomy",
            "Radiation therapy",
            "Hormone therapy",
            "Chemotherapy",
<<<<<<< HEAD
            "Molecular profiling for targeted treatment"
        ],
        "recent_research": "Advances in multiparametric MRI and genomic classifiers are refining risk stratification.",
        "ml_insights": "Deep learning algorithms can now segment prostate lesions with high precision, aiding in biopsy targeting."
=======
            "Molecular profiling"  # For precision medicine approaches
        ]
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
    },
    "Colorectal Cancer": {
        "imaging_descriptors": [
            "Polypoid lesion",
            "Annular constricting lesion",
            "Bowel wall thickening",
            "Lymph node metastases",
            "Liver metastases",
            "Peritoneal implants",
<<<<<<< HEAD
            "Mucosal irregularities"  # Added descriptor for early malignant changes
=======
            "Mucosal irregularities"  # New descriptor
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
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
<<<<<<< HEAD
        "epidemiology": "Third most common cancer worldwide; screening programs have significantly reduced mortality.",
=======
        "epidemiology": "Third most common cancer worldwide; effective screening reduces mortality.",
>>>>>>> fdb8a77d1c25ad26320d8cd34c99ed2dca317300
        "clinical_diagnostic_correlations": [
            "Altered bowel habits",
            "Rectal bleeding",
            "Abdominal pain",
            "Weight loss",
            "Iron deficiency anemia"
        ],
        "recommendations": [
            "Colonoscopy as the gold standard",
            "Flexible sigmoidoscopy",
            "Fecal occult blood test (FOBT)",
            "Fecal immunochemical test (FIT)",
            "CT colonography",
            "Biopsy for histopathological confirmation",
            "Surgical resection",
            "Chemotherapy",
            "Radiation therapy",
            "Targeted therapy",
            "Immunotherapy"
        ],
        "recent_research": "AI-driven colonoscopy is emerging to improve adenoma detection rates.",
        "ml_insights": "Advanced algorithms now assist in detecting subtle mucosal changes that may indicate early neoplasia."
    }
}
