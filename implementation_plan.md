# Phase 6: E-filing Integration Implementation Plan

## Goal Description
Implement the final step of the tax filing process: generating filled PDF tax forms and simulating the e-filing submission to the IRS.

## User Review Required
- **PDF Engine**: Using `reportlab` for generating PDFs from scratch (or overlaying text on templates). For simplicity, we will generate a summary PDF.
- **Submission**: Mock submission endpoint since we cannot actually file taxes.

## Proposed Changes

### Backend Dependencies
#### [MODIFY] [requirements.txt](file:///d:/final%20year%20project/tax-fluent-chat/backend/requirements.txt)
- Add `reportlab`.

### PDF Service
#### [NEW] [pdf_generator.py](file:///d:/final%20year%20project/tax-fluent-chat/backend/app/services/pdf_generator.py)
- Service to generate a PDF summary of the tax return.
- Function: `generate_tax_return_pdf(user_data, tax_data)`.

### Form Filler Agent
#### [NEW] [form_filler.py](file:///d:/final%20year%20project/tax-fluent-chat/backend/app/autogen_agents/form_filler.py)
- AutoGen agent that reviews the final data and "approves" it for generation.

### API Endpoints
#### [NEW] [filing.py](file:///d:/final%20year%20project/tax-fluent-chat/backend/app/api/filing.py)
- Endpoint `POST /api/filing/submit`: Simulates submission, triggers PDF generation, returns success status and PDF URL.

### Frontend
#### [MODIFY] [Filings.vue](file:///d:/final%20year%20project/tax-fluent-chat/src/pages/Filings.vue)
- Add "E-File Now" button.
- Show submission status and download link.

## Verification Plan
### Automated Tests
- Test PDF generation service.
- Test submission endpoint.

### Manual Verification
- Click "E-File Now" in the frontend and verify a PDF is downloaded and success message appears.
