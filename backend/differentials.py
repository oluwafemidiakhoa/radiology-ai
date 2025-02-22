"""This dictionary covers advanced differential diagnosis considerations across
Radiology, Oncology, and Cardiology. Each major category includes subcategories,
detailed imaging descriptors, associated risk factors, relevant epidemiology,
and clinical/diagnostic correlations. This resource is intended for integration
into advanced AI diagnostic systems and should always be used in conjunction with
clinical evaluation and additional diagnostic testing.
"""

# Medical differential diagnosis dictionary
medical_differentials = {
    "Radiology": {
        "Pulmonary": {
            "Pneumonia": {
                "imaging_descriptors": ["Lobar consolidation", "Multifocal infiltrates", "Air bronchograms", "Ground-glass opacity"],
                "risk_factors": ["Advanced age", "Immunocompromise", "Chronic lung disease", "Smoking", "Aspiration"],
                "epidemiology": "High prevalence, particularly in winter months",
                "clinical_diagnostic_correlations": ["Fever", "Cough", "Purulent sputum", "Elevated WBC count", "Positive sputum culture", "CRP elevation"],
                "recommendations": ["Chest X-ray", "CT Chest (if X-ray is inconclusive)", "Sputum culture", "Blood cultures", "Antibiotic therapy (empiric then targeted)", "Supportive care (oxygen, hydration)", "Consider viral panel"]
            },
            "Pulmonary Embolism": {
                "imaging_descriptors": ["Wedge-shaped opacity (Hampton's hump)", "Vascular cutoff", "Enlarged pulmonary artery", "Right heart strain (RV/LV ratio > 1)", "Pleural effusion", "Mosaic attenuation pattern"],
                "risk_factors": ["Immobility", "Surgery", "Trauma", "Cancer", "Oral contraceptives", "Hormone replacement therapy", "Pregnancy", "Inherited thrombophilia"],
                "epidemiology": "Moderate prevalence, significant cause of morbidity and mortality",
                "clinical_diagnostic_correlations": ["Sudden onset dyspnea", "Chest pain", "Tachycardia", "Hypoxia", "D-dimer elevation", "Wells score assessment"],
                "recommendations": ["CT Pulmonary Angiography (CTPA)", "Ventilation/Perfusion (V/Q) scan (if CTPA is contraindicated)", "Pulmonary angiography (rarely used)", "Electrocardiogram (ECG)", "Echocardiogram (to assess right heart strain)", "Anticoagulation (LMWH, unfractionated heparin, DOACs)", "Thrombolysis (in severe cases)", "Embolectomy (rarely used)"]
            },
            "Lung Cancer": {
                "imaging_descriptors": ["Solitary pulmonary nodule", "Mass with irregular borders", "Hilar or mediastinal lymphadenopathy", "Pleural effusion", "Atelectasis", "Rib destruction"],
                "risk_factors": ["Smoking", "Radon exposure", "Asbestos exposure", "Family history", "Air pollution"],
                "epidemiology": "Leading cause of cancer death worldwide",
                "clinical_diagnostic_correlations": ["Chronic cough", "Hemoptysis", "Weight loss", "Shortness of breath", "Chest pain", "Fatigue"],
                "recommendations": ["Chest CT scan", "PET/CT scan", "Bronchoscopy with biopsy", "CT-guided biopsy", "Surgical resection", "Chemotherapy", "Radiation therapy", "Immunotherapy"]
            },
            "COPD (Chronic Obstructive Pulmonary Disease)": {
                "imaging_descriptors": ["Hyperinflation", "Flattened diaphragm", "Increased retrosternal air space", "Bullae", "Thickened bronchial walls"],
                "risk_factors": ["Smoking", "Alpha-1 antitrypsin deficiency", "Air pollution", "Occupational exposures"],
                "epidemiology": "Common chronic respiratory disease, increasing in prevalence",
                "clinical_diagnostic_correlations": ["Chronic cough", "Sputum production", "Shortness of breath", "Wheezing", "Decreased FEV1/FVC ratio on spirometry"],
                "recommendations": ["Pulmonary function tests (spirometry)", "Chest X-ray (to rule out other causes)", "CT scan (to assess emphysema and bronchiectasis)", "Bronchodilators (beta-agonists, anticholinergics)", "Inhaled corticosteroids", "Pulmonary rehabilitation", "Oxygen therapy (if hypoxic)"]

            }
        },
        "Neurological": {
            "Stroke": {
                "imaging_descriptors": ["Hyperdense vessel sign (acute thrombus)", "Loss of gray-white differentiation", "Early ischemic changes (sulcal effacement, cytotoxic edema)", "Diffusion restriction on MRI", "Hemorrhagic transformation"],
                "risk_factors": ["Hypertension", "Hyperlipidemia", "Diabetes mellitus", "Smoking", "Atrial fibrillation", "Carotid artery stenosis", "Family history"],
                "epidemiology": "High prevalence, major cause of disability and death",
                "clinical_diagnostic_correlations": ["Sudden onset neurological deficits (weakness, numbness, speech difficulty, visual disturbance)", "NIH Stroke Scale score", "FAST exam (Face, Arms, Speech, Time)"],
                "recommendations": ["CT scan of the brain (non-contrast)", "CT Angiography (CTA) of the head and neck", "MRI of the brain (DWI, ADC, FLAIR)", "ECG (to assess for atrial fibrillation)", "Blood glucose monitoring", "Thrombolysis (if eligible within time window)", "Mechanical thrombectomy (if large vessel occlusion)", "Antiplatelet therapy (aspirin)", "Blood pressure control", "Neurointensive care"]
            },
            "Brain Tumor": {
                "imaging_descriptors": ["Mass lesion with surrounding edema", "Enhancement with contrast", "Midline shift", "Hydrocephalus", "Intracranial hemorrhage"],
                "risk_factors": ["Genetic syndromes (Neurofibromatosis, Tuberous sclerosis)", "Exposure to ionizing radiation"],
                "epidemiology": "Relatively rare, but can be devastating",
                "clinical_diagnostic_correlations": ["Headaches", "Seizures", "Focal neurological deficits", "Papilledema", "Cognitive changes"],
                "recommendations": ["MRI of the brain with and without contrast", "Biopsy", "Surgical resection", "Radiation therapy", "Chemotherapy", "Steroids (to reduce edema)"]
            },
            "Multiple Sclerosis (MS)": {
                "imaging_descriptors": ["Ovoid, periventricular white matter lesions", "Dawson's fingers (lesions extending perpendicular to the ventricles)", "Enhancing lesions (active inflammation)", "Spinal cord lesions"],
                "risk_factors": ["Genetic predisposition", "Vitamin D deficiency", "Epstein-Barr virus infection", "Smoking"],
                "epidemiology": "More common in women and in temperate climates",
                "clinical_diagnostic_correlations": ["Optic neuritis", "Transverse myelitis", "Lhermitte's sign", "Fatigue", "Sensory disturbances", "Motor weakness"],
                "recommendations": ["MRI of the brain and spinal cord with and without contrast", "Lumbar puncture (to assess for oligoclonal bands)", "Visual evoked potentials (VEPs)", "Disease-modifying therapies (DMTs)", "Symptomatic treatment"]

            }
        },
        "Musculoskeletal":{
            "Fracture":{
                "imaging_descriptors":["Discontinuity of the bone cortex","Presence of fracture line", "Bone fragments displacement", "Soft tissue swelling"],
                "risk_factors":["Trauma", "Osteoporosis", "Age related bone changes", "Repetitive stress", "Underlying bone pathology"],
                "epidemiology":"Common, particularly in older adults and athletes",
                "clinical_diagnostic_correlations": ["Pain","Swelling", "Deformity", "Limited range of motion", "Tenderness"],
                "recommendations": ["X-Ray", "CT scan", "MRI", "Immobilization", "Pain management", "Surgery(if required)"]

            }
        }
    },
    "Oncology": {
        "Breast Cancer": {
            "imaging_descriptors": ["Mass with spiculated margins", "Microcalcifications", "Architectural distortion", "Nipple retraction", "Skin thickening", "Lymphadenopathy"],
            "risk_factors": ["Age", "Family history", "Genetic mutations (BRCA1, BRCA2)", "Early menarche, late menopause", "Nulliparity or late first pregnancy", "Hormone replacement therapy", "Obesity"],
            "epidemiology": "Most common cancer in women worldwide",
            "clinical_diagnostic_correlations": ["Palpable breast mass", "Nipple discharge", "Skin changes", "Lymph node enlargement"],
            "recommendations": ["Mammography", "Breast ultrasound", "MRI of the breast", "Biopsy (core needle biopsy, excisional biopsy)", "Staging (sentinel lymph node biopsy, axillary lymph node dissection)", "Surgery (lumpectomy, mastectomy)", "Radiation therapy", "Chemotherapy", "Hormone therapy", "Targeted therapy", "Immunotherapy"]
        },
        "Prostate Cancer": {
            "imaging_descriptors": ["Peripheral zone lesion", "Reduced diffusion on MRI", "Elevated choline/citrate ratio on MR spectroscopy", "Bone metastases"],
            "risk_factors": ["Age", "Family history", "African American ethnicity", "High-fat diet"],
            "epidemiology": "Most common cancer in men",
            "clinical_diagnostic_correlations": ["Elevated PSA level", "Urinary symptoms (frequency, urgency, nocturia)", "Bone pain (if metastatic)"],
            "recommendations": ["Prostate-specific antigen (PSA) testing", "Digital rectal exam (DRE)", "Transrectal ultrasound (TRUS) with biopsy", "MRI of the prostate", "Gleason score", "Active surveillance", "Radical prostatectomy", "Radiation therapy", "Hormone therapy", "Chemotherapy"]
        },
        "Colorectal Cancer": {
            "imaging_descriptors": ["Polypoid lesion", "Annular constricting lesion", "Bowel wall thickening", "Lymph node metastases", "Liver metastases", "Peritoneal implants"],
            "risk_factors": ["Age", "Family history", "Inflammatory bowel disease (IBD)", "Diet high in red and processed meat", "Smoking", "Obesity", "Alcohol consumption"],
            "epidemiology": "Third most common cancer worldwide",
            "clinical_diagnostic_correlations": ["Change in bowel habits", "Rectal bleeding", "Abdominal pain", "Weight loss", "Iron deficiency anemia"],
            "recommendations": ["Colonoscopy", "Flexible sigmoidoscopy", "Fecal occult blood test (FOBT)", "Fecal immunochemical test (FIT)", "CT colonography (virtual colonoscopy)", "Biopsy", "Surgical resection", "Chemotherapy", "Radiation therapy", "Targeted therapy", "Immunotherapy"]
        }
    },
    "Cardiology": {
        "Myocardial Infarction (MI)": {
            "imaging_descriptors": ["Regional wall motion abnormality", "Reduced ejection fraction", "Late gadolinium enhancement (scarring)", "Coronary artery stenosis or occlusion"],
            "risk_factors": ["Hypertension", "Hyperlipidemia", "Diabetes mellitus", "Smoking", "Family history", "Obesity", "Sedentary lifestyle"],
            "epidemiology": "Major cause of morbidity and mortality worldwide",
            "clinical_diagnostic_correlations": ["Chest pain", "Shortness of breath", "Sweating", "Nausea", "Vomiting", "ECG changes (ST-segment elevation, T-wave inversion)", "Elevated cardiac biomarkers (troponin)", "Killip Class"],
            "recommendations": ["Electrocardiogram (ECG)", "Cardiac biomarkers (troponin)", "Coronary angiography", "Percutaneous coronary intervention (PCI)", "Thrombolysis (if PCI is not available)", "Aspirin", "Clopidogrel", "Beta-blockers", "ACE inhibitors", "Statins", "Oxygen therapy"]
        },
        "Heart Failure": {
            "imaging_descriptors": ["Cardiomegaly", "Pulmonary edema", "Pleural effusion", "Left ventricular dilation", "Reduced ejection fraction", "Mitral regurgitation", "Tricuspid regurgitation"],
            "risk_factors": ["Hypertension", "Coronary artery disease", "Valvular heart disease", "Cardiomyopathy", "Diabetes mellitus", "Alcohol abuse", "Family history"],
            "epidemiology": "Increasing prevalence with aging population",
            "clinical_diagnostic_correlations": ["Shortness of breath", "Fatigue", "Swelling of ankles and feet", "Orthopnea", "Paroxysmal nocturnal dyspnea", "Elevated BNP or NT-proBNP"],
            "recommendations": ["Echocardiogram", "Electrocardiogram (ECG)", "Chest X-ray", "BNP or NT-proBNP measurement", "ACE inhibitors or ARBs", "Beta-blockers", "Diuretics", "Aldosterone antagonists", "Digoxin", "Sodium-glucose cotransporter 2 (SGLT2) inhibitors"]
        },
        "Arrhythmia": {
            "Atrial Fibrillation (AF)": {
                "imaging_descriptors": ["Absence of P waves", "Irregularly irregular rhythm"],
                "risk_factors": ["Age", "Hypertension", "Coronary artery disease", "Valvular heart disease", "Heart failure", "Hyperthyroidism", "Alcohol abuse", "Obesity", "Sleep apnea"],
                "epidemiology": "Most common sustained arrhythmia",
                "clinical_diagnostic_correlations": ["Palpitations", "Shortness of breath", "Fatigue", "Dizziness", "Chest pain", "Stroke"],
                "recommendations": ["Electrocardiogram (ECG)", "Holter monitor", "Event monitor", "Anticoagulation (warfarin, DOACs)", "Rate control (beta-blockers, calcium channel blockers, digoxin)", "Rhythm control (antiarrhythmic drugs, cardioversion, catheter ablation)"]
            }
        }
    }
}

# Evidence-based clinical guidelines
evidence_based_guidelines = {
    "ACR": {
        "LungRADS": {
            "Category 1": "No significant findings - routine follow-up",
            "Category 2": "Benign appearance - 12 month follow-up",
            "Category 3": "Probably benign - short-interval follow-up (e.g., 6 months)",
            "Category 4A": "Suspicious findings - consider biopsy",
            "Category 4B": "Highly suspicious findings - biopsy recommended",
            "Category 4X": "Highly suspicious findings with additional features (e.g., new or growing lesion) - biopsy mandatory"
        },
        "BI-RADS": {
            "Category 0": "Incomplete - need additional imaging evaluation",
            "Category 1": "Negative - routine screening",
            "Category 2": "Benign findings - routine screening",
            "Category 3": "Probably benign - short-interval follow-up (e.g., 6 months)",
            "Category 4A": "Low suspicion for malignancy - consider biopsy",
            "Category 4B": "Intermediate suspicion for malignancy - biopsy recommended",
            "Category 4C": "Moderate concern for malignancy - biopsy recommended",
            "Category 5": "Highly suggestive of malignancy - appropriate action should be taken",
            "Category 6": "Known biopsy-proven malignancy - appropriate action should be taken"
        }

    },
    "ESC": {
        "PE": {
            "Diagnosis": ["Wells Score", "D-Dimer testing", "CT Pulmonary Angiography (CTPA)", "Ventilation/Perfusion (V/Q) scan"],
            "Treatment": ["Anticoagulation (LMWH, unfractionated heparin, DOACs)", "Thrombolysis (in severe cases)", "Embolectomy (rarely used)", "IVC filter (in patients with contraindications to anticoagulation)"],
            "Prognosis": ["Pulmonary Embolism Severity Index (PESI)", "sPESI (simplified PESI)"]
        },
        "ACS": {
            "Diagnosis": ["Electrocardiogram (ECG)", "Cardiac biomarkers (troponin)", "Coronary angiography"],
            "Treatment": ["Aspirin", "Clopidogrel or ticagrelor", "Heparin", "Percutaneous coronary intervention (PCI)", "Coronary artery bypass grafting (CABG)", "Beta-blockers", "ACE inhibitors", "Statins"]
        }
    },
    "NCCN": {
        "Breast Cancer": {
            "Screening": ["Mammography", "Clinical breast exam", "Self-breast exam", "MRI (for high-risk individuals)"],
            "Treatment": ["Surgery (lumpectomy, mastectomy)", "Radiation therapy", "Chemotherapy", "Hormone therapy", "Targeted therapy", "Immunotherapy"]
        }
    }
}
