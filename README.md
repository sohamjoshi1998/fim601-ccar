# CCAR-Style Capital Forecasting and Stress Testing
This repository contains the dataset, outputs, and analysis code for a CCAR-style capital forecasting and stress testing project.  
The goal of this project is to model capital impacts under baseline and stress macroeconomic scenarios.

## Project Overview
This project focuses on:
- Credit loss forecasting across loan portfolios (retail / wholesale)
- Scenario-based stress testing using macroeconomic variables
- Capital ratio projection (e.g., CET1) & risk-weighted assets (RWA)
- Validation & sensitivity checks on key drivers

## Instructions
Follow the instructions in this document: 
[CCAR Project Guide (Google Doc)](https://docs.google.com/document/d/11qiZ6cXF36Enxflr_CQ6pEQFzm1bd5zGFF9_bbWGicM/edit?usp=sharing)

### Create virtual environment and install the requirements 

```bash
python3 -m venv venv-ccar
source venv-ccar/bin/activate
pip install -r requirements.txt

