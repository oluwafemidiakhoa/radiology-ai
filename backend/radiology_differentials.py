# radiology_differentials.py
# Advanced Radiology Differential Diagnosis Dictionary
# This module contains detailed diagnostic considerations for pulmonary and neurological conditions
# encountered in radiology, with additional keys for recent research and AI integration.

radiology_differentials = {
    "Pulmonary": {
        "Pneumonia": {
            "imaging_descriptors": [
                "Lobar consolidation",
                "Multifocal infiltrates",
                "Air bronchograms",
                "Ground-glass opacity",
                "Interstitial thickening"  # Advanced descriptor for atypical/viral pneumonia
            ],
            "risk_factors": [
                "Advanced age",
                "Immunocompromise",
                "Chronic lung disease",
                "Smoking",
                "Aspiration",
                "Recent viral infection"  # Post-COVID-19 observations
            ],
            "epidemiology": "High prevalence in winter; emerging evidence suggests increased rates post-viral infections.",
            "clinical_diagnostic_correlations": [
                "Fever",
                "Cough",
                "Purulent sputum",
                "Elevated WBC count",
                "Positive sputum culture",
                "CRP and procalcitonin elevation"
            ],
            "recommendations": [
                "Chest X-ray as initial imaging",
                "CT Chest for inconclusive cases or suspected atypical pneumonia",
                "Sputum and blood cultures",
                "Empiric antibiotic therapy with adjustment based on culture results",
                "Supportive care (oxygen supplementation, hydration)",
                "PCR testing for viral pathogens (influenza, COVID-19)"
            ],
            "recent_research": "Recent studies indicate the utility of AI-enhanced CT imaging to differentiate bacterial from viral pneumonia.",
            "ml_insights": "Integration of deep learning models has improved classification accuracy by up to 15% in recent trials."
        },
        "Pulmonary Embolism": {
            "imaging_descriptors": [
                "Wedge-shaped opacity (Hampton's hump)",
                "Vascular cutoff",
                "Enlarged pulmonary artery",
                "Right heart strain (RV/LV ratio > 1)",
                "Pleural effusion",
                "Mosaic attenuation pattern",
                "Filling defects on CT Pulmonary Angiography"
            ],
            "risk_factors": [
                "Immobility",
                "Recent surgery",
                "Trauma",
                "Malignancy",
                "Oral contraceptives",
                "Hormone replacement therapy",
                "Pregnancy",
                "Inherited thrombophilia"
            ],
            "epidemiology": "Moderate prevalence; a leading cause of preventable in-hospital mortality.",
            "clinical_diagnostic_correlations": [
                "Sudden onset dyspnea",
                "Pleuritic chest pain",
                "Tachycardia",
                "Hypoxia",
                "Elevated D-dimer",
                "High Wells score"
            ],
            "recommendations": [
                "CT Pulmonary Angiography (CTPA) as first-line imaging",
                "Ventilation/Perfusion (V/Q) scan if CTPA is contraindicated",
                "ECG and echocardiogram for cardiac assessment",
                "Immediate initiation of anticoagulation",
                "Consider thrombolytic therapy for massive embolism",
                "Embolectomy in refractory cases"
            ],
            "recent_research": "AI-driven analysis of CTPA images has shown promising results in early PE detection.",
            "ml_insights": "Deep learning segmentation algorithms have improved clot detection and quantification."
        },
        "Lung Cancer": {
            "imaging_descriptors": [
                "Solitary pulmonary nodule",
                "Mass with irregular borders",
                "Hilar/mediastinal lymphadenopathy",
                "Pleural effusion",
                "Atelectasis",
                "Rib destruction",
                "Ground-glass opacity with spiculation"  # Indicative of early adenocarcinoma
            ],
            "risk_factors": [
                "Smoking",
                "Radon exposure",
                "Asbestos exposure",
                "Family history",
                "Air pollution",
                "Prior lung infections"
            ],
            "epidemiology": "Leading cause of cancer death globally; molecular profiling is increasingly important.",
            "clinical_diagnostic_correlations": [
                "Chronic cough",
                "Hemoptysis",
                "Unintentional weight loss",
                "Dyspnea",
                "Chest pain",
                "Fatigue"
            ],
            "recommendations": [
                "Contrast-enhanced CT scan of the chest",
                "PET/CT scan for metabolic evaluation",
                "Bronchoscopy with biopsy for tissue diagnosis",
                "CT-guided percutaneous biopsy",
                "Surgical resection when indicated",
                "Multimodal treatment (chemotherapy, radiation, immunotherapy)",
                "Molecular profiling for targeted treatment"
            ],
            "recent_research": "Recent advances in liquid biopsy and AI-based image analysis are revolutionizing early lung cancer detection.",
            "ml_insights": "Hybrid CNN architectures have achieved significant improvements in nodule classification accuracy."
        },
        "COPD": {
            "imaging_descriptors": [
                "Hyperinflation",
                "Flattened diaphragm",
                "Increased retrosternal air space",
                "Bullae formation",
                "Thickened bronchial walls",
                "Centrilobular emphysema"
            ],
            "risk_factors": [
                "Smoking",
                "Alpha-1 antitrypsin deficiency",
                "Air pollution",
                "Occupational exposures"
            ],
            "epidemiology": "One of the most prevalent chronic respiratory diseases, with a growing global burden.",
            "clinical_diagnostic_correlations": [
                "Chronic productive cough",
                "Exertional dyspnea",
                "Wheezing",
                "Reduced FEV1/FVC ratio"
            ],
            "recommendations": [
                "Spirometry for pulmonary function testing",
                "Chest X-ray for initial assessment",
                "CT scan for detailed parenchymal evaluation",
                "Bronchodilator therapy",
                "Inhaled corticosteroids for frequent exacerbators",
                "Pulmonary rehabilitation",
                "Supplemental oxygen therapy when indicated"
            ],
            "recent_research": "Integration of AI with spirometry data has enhanced early detection and monitoring of COPD progression.",
            "ml_insights": "Predictive models now provide personalized risk assessments based on imaging and clinical data."
        }
    },
    "Neurological": {
        "Stroke": {
            "imaging_descriptors": [
                "Hyperdense vessel sign (acute thrombus)",
                "Loss of gray-white differentiation",
                "Sulcal effacement, cytotoxic edema",
                "Diffusion restriction on MRI",
                "Hemorrhagic transformation"
            ],
            "risk_factors": [
                "Hypertension",
                "Hyperlipidemia",
                "Diabetes mellitus",
                "Smoking",
                "Atrial fibrillation",
                "Carotid artery stenosis",
                "Family history"
            ],
            "epidemiology": "Very high prevalence; one of the leading causes of long-term disability and death.",
            "clinical_diagnostic_correlations": [
                "Sudden onset neurological deficits",
                "NIH Stroke Scale assessment",
                "FAST exam (Face, Arms, Speech, Time)"
            ],
            "recommendations": [
                "Non-contrast CT of the brain as initial imaging",
                "CT Angiography (CTA) for vascular assessment",
                "MRI with DWI for early detection of ischemia",
                "ECG for cardiac rhythm evaluation",
                "Glucose monitoring",
                "Thrombolytic therapy if within the treatment window",
                "Mechanical thrombectomy for large vessel occlusion",
                "Antiplatelet therapy and blood pressure control"
            ],
            "recent_research": "Recent trials emphasize the benefits of endovascular thrombectomy in select patient populations.",
            "ml_insights": "AI algorithms can now rapidly quantify infarct volume and predict functional outcomes."
        },
        "Brain Tumor": {
            "imaging_descriptors": [
                "Mass lesion with surrounding edema",
                "Contrast enhancement",
                "Midline shift",
                "Hydrocephalus",
                "Intracranial hemorrhage"
            ],
            "risk_factors": [
                "Genetic syndromes (e.g., Neurofibromatosis, Tuberous sclerosis)",
                "Exposure to ionizing radiation"
            ],
            "epidemiology": "Relatively rare but with high clinical impact when present.",
            "clinical_diagnostic_correlations": [
                "Headaches",
                "Seizures",
                "Focal neurological deficits",
                "Papilledema",
                "Cognitive decline"
            ],
            "recommendations": [
                "MRI of the brain with and without contrast",
                "Surgical biopsy or resection",
                "Radiation therapy",
                "Chemotherapy",
                "Adjunctive steroid therapy to reduce edema"
            ],
            "recent_research": "Advanced imaging biomarkers are emerging to predict tumor aggressiveness.",
            "ml_insights": "Deep learning models have improved segmentation accuracy for brain tumors, aiding in surgical planning."
        },
        "Multiple Sclerosis (MS)": {
            "imaging_descriptors": [
                "Ovoid periventricular lesions",
                "Dawson's fingers (lesions perpendicular to ventricles)",
                "Enhancing lesions indicating active inflammation",
                "Spinal cord lesions"
            ],
            "risk_factors": [
                "Genetic predisposition",
                "Vitamin D deficiency",
                "Epstein-Barr virus infection",
                "Smoking"
            ],
            "epidemiology": "Higher incidence in women and in temperate climates.",
            "clinical_diagnostic_correlations": [
                "Optic neuritis",
                "Transverse myelitis",
                "Lhermitte's sign",
                "Chronic fatigue",
                "Sensory and motor deficits"
            ],
            "recommendations": [
                "MRI of the brain and spinal cord with and without contrast",
                "Lumbar puncture for oligoclonal bands",
                "Visual evoked potentials (VEPs)",
                "Initiate disease-modifying therapies (DMTs)",
                "Symptomatic management for spasticity and pain"
            ],
            "recent_research": "Novel biomarkers and advanced MRI sequences are being integrated for earlier diagnosis.",
            "ml_insights": "Machine learning has enabled automated lesion segmentation and volumetric analysis in MS patients."
        }
    },
    "Musculoskeletal": {
        "Fracture": {
            "imaging_descriptors": [
                "Discontinuity of the bone cortex",
                "Visible fracture line",
                "Displacement of bone fragments",
                "Associated soft tissue swelling"
            ],
            "risk_factors": [
                "Trauma",
                "Osteoporosis",
                "Age-related degeneration",
                "Repetitive stress",
                "Underlying bone pathology"
            ],
            "epidemiology": "Very common in elderly populations and athletes.",
            "clinical_diagnostic_correlations": [
                "Localized pain",
                "Swelling",
                "Deformity",
                "Limited range of motion",
                "Tenderness at the injury site"
            ],
            "recommendations": [
                "Plain X-ray for initial assessment",
                "CT scan for complex fracture delineation",
                "MRI if soft tissue injury is suspected",
                "Immobilization (casting or splinting)",
                "Analgesia and pain management",
                "Surgical fixation for unstable fractures"
            ],
            "recent_research": "Innovative 3D imaging and AI-driven fracture detection are improving diagnostic accuracy.",
            "ml_insights": "Deep neural networks now assist radiologists by highlighting subtle fracture lines that may be missed on plain films."
        }
    }
}
