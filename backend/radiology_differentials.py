# radiology_differentials.py

radiology_differentials = {
    "Pulmonary": {
        "Pneumonia": {
            "imaging_descriptors": [
                "Lobar consolidation",
                "Multifocal infiltrates",
                "Air bronchograms",
                "Ground-glass opacity",
                "Interstitial thickening"  // Added advanced descriptor for atypical or viral pneumonia
            ],
            "risk_factors": [
                "Advanced age",
                "Immunocompromise",
                "Chronic lung disease",
                "Smoking",
                "Aspiration",
                "Recent viral infection"  // New risk factor post-COVID-19 era
            ],
            "epidemiology": "High prevalence, particularly in winter months; recent studies highlight increased incidence in post-viral settings",
            "clinical_diagnostic_correlations": [
                "Fever",
                "Cough",
                "Purulent sputum",
                "Elevated WBC count",
                "Positive sputum culture",
                "CRP elevation",
                "Procalcitonin levels"  // Added laboratory marker for bacterial infection
            ],
            "recommendations": [
                "Chest X-ray",
                "CT Chest (if inconclusive or for suspected viral pneumonia)",
                "Sputum culture",
                "Blood cultures",
                "Empiric then targeted antibiotic therapy",
                "Supportive care (oxygen, hydration)",
                "Consider viral panel or PCR testing for influenza/COVID-19"  // Enhanced recommendations
            ]
        },
        "Pulmonary Embolism": {
            "imaging_descriptors": [
                "Wedge-shaped opacity (Hampton's hump)",
                "Vascular cutoff",
                "Enlarged pulmonary artery",
                "Right heart strain (RV/LV ratio > 1)",
                "Pleural effusion",
                "Mosaic attenuation pattern",
                "Filling defects on CTPA"  // Added descriptor for CT pulmonary angiography
            ],
            "risk_factors": [
                "Immobility",
                "Surgery",
                "Trauma",
                "Cancer",
                "Oral contraceptives",
                "Hormone replacement therapy",
                "Pregnancy",
                "Inherited thrombophilia"
            ],
            "epidemiology": "Moderate prevalence; a leading cause of preventable mortality in hospitalized patients",
            "clinical_diagnostic_correlations": [
                "Sudden onset dyspnea",
                "Chest pain",
                "Tachycardia",
                "Hypoxia",
                "D-dimer elevation",
                "Wells score assessment"
            ],
            "recommendations": [
                "CT Pulmonary Angiography (CTPA)",
                "Ventilation/Perfusion (V/Q) scan (if CTPA contraindicated)",
                "Pulmonary angiography (rarely used)",
                "ECG",
                "Echocardiogram (to assess right heart strain)",
                "Anticoagulation (LMWH, unfractionated heparin, DOACs)",
                "Thrombolysis (in severe cases)",
                "Embolectomy (rarely used)"
            ]
        },
        "Lung Cancer": {
            "imaging_descriptors": [
                "Solitary pulmonary nodule",
                "Mass with irregular borders",
                "Hilar or mediastinal lymphadenopathy",
                "Pleural effusion",
                "Atelectasis",
                "Rib destruction",
                "Ground-glass opacity with spiculation"  // Added descriptor for early adenocarcinoma
            ],
            "risk_factors": [
                "Smoking",
                "Radon exposure",
                "Asbestos exposure",
                "Family history",
                "Air pollution",
                "Previous lung infections"  // New risk factor noted in some studies
            ],
            "epidemiology": "Leading cause of cancer death worldwide; molecular subtyping now guides management",
            "clinical_diagnostic_correlations": [
                "Chronic cough",
                "Hemoptysis",
                "Weight loss",
                "Shortness of breath",
                "Chest pain",
                "Fatigue"
            ],
            "recommendations": [
                "Chest CT scan",
                "PET/CT scan",
                "Bronchoscopy with biopsy",
                "CT-guided biopsy",
                "Surgical resection",
                "Chemotherapy",
                "Radiation therapy",
                "Immunotherapy",
                "Molecular profiling"  // Added for targeted therapy options
            ]
        },
        "COPD (Chronic Obstructive Pulmonary Disease)": {
            "imaging_descriptors": [
                "Hyperinflation",
                "Flattened diaphragm",
                "Increased retrosternal air space",
                "Bullae",
                "Thickened bronchial walls",
                "Emphysematous changes with centrilobular patterns"  // Added advanced imaging finding
            ],
            "risk_factors": [
                "Smoking",
                "Alpha-1 antitrypsin deficiency",
                "Air pollution",
                "Occupational exposures"
            ],
            "epidemiology": "Common chronic respiratory disease; increasing in prevalence globally",
            "clinical_diagnostic_correlations": [
                "Chronic cough",
                "Sputum production",
                "Shortness of breath",
                "Wheezing",
                "Decreased FEV1/FVC ratio on spirometry"
            ],
            "recommendations": [
                "Pulmonary function tests (spirometry)",
                "Chest X-ray (to rule out other causes)",
                "CT scan (to assess emphysema and bronchiectasis)",
                "Bronchodilators (beta-agonists, anticholinergics)",
                "Inhaled corticosteroids",
                "Pulmonary rehabilitation",
                "Oxygen therapy (if hypoxic)"
            ]
        }
    }
}
