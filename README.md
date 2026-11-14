# Cloud Forensics NLP & XAI Pipeline

A real-time, production-grade cloud forensics pipeline that ingests server logs, extracts entities using Natural Language Processing, and flags security threats using Explainable AI.

## Features
* **Real-Time Ingestion:** Actively monitors network directories for incoming log drops using Python `watchdog` (PollingObserver for cloud compatibility).
* **NLP Parser:** Uses `SpaCy` to dynamically extract timestamps, users, and actions from raw text logs.
* **XAI Threat Detection:** Employs a `Scikit-Learn` Isolation Forest to detect behavioral anomalies and provide explainable alerts.
* **Forensic Validation:** Generates structured evidence reports successfully validated for import in Autopsy.

## Tech Stack
Python 3.14, SpaCy, Scikit-Learn, Pandas, Watchdog