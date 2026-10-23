# WasteVision: AI for a Cleaner Future

WasteVision is a Streamlit waste-sorting assistant. Upload a photo to compare it against seven material categories with pretrained CLIP zero-shot image classification, then review relative scores and practical disposal guidance. The dashboard tracks scans, category counts, and recent activity for the current session.

## Run locally

Python 3.10 or newer is recommended. From the project directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead. PyTorch installation can vary by operating system and hardware; if the standard install fails, use the appropriate command from the official PyTorch installation selector, then install the remaining requirements.

The first analysis downloads `openai/clip-vit-base-patch32` from Hugging Face, so internet access is needed initially. The model is cached for the Streamlit process. Scans are kept in session state and are not persisted after the session ends.

## Using the app

1. Upload a JPG, JPEG, PNG, or WEBP image up to 10 MB.
2. Review the preview and select **Analyze this item**.
3. Review the leading category, top three relative scores, and disposal guidance.
4. Compare session scans in the category chart and recent activity list.
5. Open **Sorting guide** in the sidebar for category-specific handling notes.

The categories are plastic, paper and cardboard, glass, metal, organic, electronic, and mixed/other. Results are model estimates, not calibrated probabilities or disposal guarantees. Local waste collection rules vary; consult your local authority. Use authorized e-waste and battery collection points.

## Project structure

- `app.py`: Streamlit dashboard, image validation, session history, chart, and guide
- `src/classifier.py`: cached pretrained CLIP pipeline and category normalization
- `src/guidance.py`: disposal recommendations by category
- `requirements.txt`: Python dependencies
- `sample_images/`: optional local demo images (empty in the starter)
- `docs/PROJECT_PLAN.md`: original demo plan and roadmap

## Limitations

CLIP may misclassify composite, damaged, obscured, or unfamiliar items. It classifies the overall image rather than detecting multiple objects. Scores are relative to the candidate labels supplied to the model and should not be read as calibrated confidence. No sample predictions are fabricated when no local demo images are available.
