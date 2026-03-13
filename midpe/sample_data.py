"""
sample_data/synthetic_documents.py
Realistic synthetic document text for all 8 document types.
Used for demos and portfolio presentation.
"""

SAMPLES = {
    "invoice": {
        "filename": "Nexus_Tech_Invoice_INV-2024-00847.pdf",
        "text": """
TAX INVOICE

Nexus Tech Solutions Pty Ltd
ABN: 12 345 678 901
123 Innovation Drive, Sydney NSW 2000
Phone: +61 2 9000 1234 | accounts@nexustech.com.au
www.nexustech.com.au

Invoice Number: INV-2024-00847
Invoice Date: 15/03/2024
Due Date: 14/04/2024

Bill To:
Meridian Consulting Group Pty Ltd
Level 8, 45 Business Park Avenue
Melbourne VIC 3000
ABN: 98 765 432 109
Contact: Sarah Chen | s.chen@meridiancg.com.au

Description                             Qty    Unit Price       Amount
Cloud Infrastructure Setup & Config      1      $4,500.00     $4,500.00
API Integration Services (REST/GraphQL)  3        $800.00     $2,400.00
Technical Documentation & Handover       1        $600.00       $600.00
Monthly Support Retainer (March 2024)    1        $950.00       $950.00

Subtotal:                                                      $8,450.00
GST (10%):                                                       $845.00
Total Amount Due:                                              $9,295.00

Payment Terms: Net 30
Bank: Commonwealth Bank of Australia | BSB: 062-000 | Account: 1234 5678
Reference: INV-2024-00847
""",
        "problem": "Manual invoice entry taking 8–12 mins per document",
        "solution_time_ms": 340,
    },

    "bank_statement": {
        "filename": "ANZ_Bank_Statement_March2024.pdf",
        "text": """
ANZ Bank
Account Statement

Account Holder: Meridian Consulting Group Pty Ltd
Account Number: XXXX XXXX XXXX 4521
BSB: 012-455
Statement Period: 01/03/2024 to 31/03/2024
Statement Date: 01/04/2024

Opening Balance: $42,850.75

Date          Description                          Debit        Credit       Balance
01/03/2024    Opening Balance                                                42,850.75
03/03/2024    Client Payment - Zenith Corp                      15,000.00    57,850.75
05/03/2024    Office Rent - March 2024              4,200.00                 53,650.75
07/03/2024    ATO BAS Payment                       8,750.00                 44,900.75
10/03/2024    PAYG Wages - Staff                   18,500.00                 26,400.75
12/03/2024    Client Payment - Apex Industries                  22,000.00    48,400.75
15/03/2024    Software Subscriptions                  420.00                 47,980.75
18/03/2024    Client Payment - Orbit Ltd                        11,500.00    59,480.75
20/03/2024    Supplier Payment - IT Services          3,200.00               56,280.75
22/03/2024    Utility Bills                            890.00                55,390.75
25/03/2024    Client Payment - Nextech                          18,000.00    73,390.75
28/03/2024    Insurance Premium                      1,250.00                72,140.75
31/03/2024    Bank Fees                                 22.00                72,118.75

Closing Balance: $72,118.75
Total Credits: $66,500.00
Total Debits: $37,232.00
""",
        "problem": "Reconciling 200+ transactions monthly across multiple statements",
        "solution_time_ms": 520,
    },

    "purchase_order": {
        "filename": "PO-2024-0392_Orbit_Technologies.pdf",
        "text": """
PURCHASE ORDER

PO Number: PO-2024-0392
PO Date: 20/03/2024
Delivery Date: 05/04/2024

From (Buyer):
Meridian Consulting Group Pty Ltd
Level 8, 45 Business Park Avenue
Melbourne VIC 3000
Procurement Contact: James Wilson | j.wilson@meridiancg.com.au

Vendor / Supplier:
Orbit Technologies Pty Ltd
88 Tech Valley Road, Brisbane QLD 4000
Vendor Code: V-00241
Contact: Lisa Pham | sales@orbittech.com.au

Ship To:
Meridian Consulting Group - IT Department
Level 8, 45 Business Park Avenue, Melbourne VIC 3000

Item Code    Description                          Qty    Unit Cost       Total
IT-LPT-001   Dell XPS 15 Laptop (i7, 32GB RAM)    5      $2,850.00    $14,250.00
IT-MON-002   Dell 27" 4K Monitor                  5        $650.00     $3,250.00
IT-KBD-003   Logitech MX Keys Keyboard             5        $180.00       $900.00
IT-MSE-004   Logitech MX Master 3 Mouse            5        $120.00       $600.00
IT-DOK-005   CalDigit TS4 Thunderbolt Dock         5        $420.00     $2,100.00

Subtotal:                                                               $21,100.00
GST (10%):                                                               $2,110.00
Order Total:                                                            $23,210.00

Approved By: Michael Torres — CFO, Meridian Consulting Group
Approval Date: 20/03/2024

Delivery Terms: DDP Melbourne
Payment Terms: 30 days from delivery and invoice
""",
        "problem": "Matching POs to invoices and deliveries manually, error-prone at volume",
        "solution_time_ms": 290,
    },

    "contract": {
        "filename": "Service_Agreement_Nexus_Meridian_2024.pdf",
        "text": """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of the 1st day of January 2024 ("Effective Date")

BETWEEN:
Nexus Tech Solutions Pty Ltd (ABN: 12 345 678 901), a company incorporated in New South Wales, Australia, with its registered office at 123 Innovation Drive, Sydney NSW 2000 ("Service Provider")

AND

Meridian Consulting Group Pty Ltd (ABN: 98 765 432 109), a company incorporated in Victoria, Australia, with its registered office at Level 8, 45 Business Park Avenue, Melbourne VIC 3000 ("Client")

WHEREAS the Service Provider wishes to provide, and the Client wishes to receive, certain technology services on the terms and conditions set out in this Agreement.

1. SERVICES
The Service Provider agrees to deliver cloud infrastructure management, API development, and technical support services as detailed in Schedule A.

2. TERM
This Agreement shall commence on the Effective Date and continue for a period of 12 months, unless earlier terminated in accordance with clause 8.
Termination Date: 31st December 2024

3. FEES AND PAYMENT
The Client shall pay the Service Provider a monthly retainer of $9,500.00 (plus GST) payable within 30 days of invoice.

4. CONFIDENTIALITY
Each party agrees to maintain the confidentiality of the other party's Confidential Information.

5. INTELLECTUAL PROPERTY
All work product created under this Agreement shall remain the property of the Client upon full payment.

6. LIMITATION OF LIABILITY
The Service Provider's total liability shall not exceed the fees paid in the preceding 3 months.

7. INDEMNIFICATION
Each party shall indemnify the other against claims arising from its own negligence or wilful misconduct.

8. TERMINATION
Either party may terminate this Agreement with 30 days written notice.

9. GOVERNING LAW
This Agreement shall be governed by the laws of the State of Victoria, Australia.

10. FORCE MAJEURE
Neither party shall be liable for delays caused by circumstances beyond its reasonable control.

IN WITNESS WHEREOF the parties have executed this Agreement.

SIGNED for Nexus Tech Solutions Pty Ltd:
Name: David Park | Title: CEO | Date: 01/01/2024

SIGNED for Meridian Consulting Group Pty Ltd:
Name: Michael Torres | Title: CFO | Date: 01/01/2024
""",
        "problem": "Manually tracking contract dates, clauses, and renewal obligations",
        "solution_time_ms": 410,
    },

    "salary_slip": {
        "filename": "Payslip_Sarah_Chen_March2024.pdf",
        "text": """
SALARY SLIP / PAY STUB
Meridian Consulting Group Pty Ltd
ABN: 98 765 432 109 | payroll@meridiancg.com.au

Pay Period: March 2024 (01/03/2024 – 31/03/2024)
Payment Date: 28/03/2024

Employee Name:     Sarah Chen
Employee ID:       EMP-0042
Department:        Strategy & Consulting
Designation:       Senior Consultant
Tax File Number:   XXX-XXX-XXX

EARNINGS                                   Amount
Basic Pay                                  $7,500.00
House Rent Allowance (HRA)                 $1,500.00
Transport Allowance                          $300.00
Performance Bonus (Q1 Target Met)          $1,200.00
Overtime (8 hours @ $75/hr)                  $600.00
Gross Earnings:                           $11,100.00

DEDUCTIONS                                 Amount
Income Tax (PAYG Withholding)              $2,890.00
Superannuation (11%)                       $1,221.00
Professional Membership Fee                  $120.00
Health Insurance (Medibank)                  $180.00
Total Deductions:                          $4,411.00

NET SALARY (Take Home):                    $6,689.00

Bank: ANZ Bank | BSB: 012-455 | Account: XXXX XXXX 7821
""",
        "problem": "Payroll processing for 80+ staff involving manual data checks each month",
        "solution_time_ms": 270,
    },

    "utility_bill": {
        "filename": "AGL_Electricity_March2024.pdf",
        "text": """
AGL Energy Ltd
Electricity Bill

Account ID: AGL-9823-4410
Customer Name: Meridian Consulting Group Pty Ltd
Service Address: Level 8, 45 Business Park Avenue, Melbourne VIC 3000
Bill Number: BILL-20240401-882

Billing Period: 01/03/2024 to 31/03/2024
Bill Date: 01/04/2024
Due Date: 22/04/2024

METER DETAILS
Meter Number: VIC-E-00441892
Previous Reading (01/03/2024):  84,210 kWh
Current Reading  (31/03/2024):  85,872 kWh
Units Consumed:                  1,662 kWh

CHARGES BREAKDOWN
Peak Usage        (1,100 kWh @ $0.2850/kWh):    $313.50
Off-Peak Usage      (562 kWh @ $0.1650/kWh):     $92.73
Supply Charge       (31 days @ $1.0500/day):      $32.55
Renewable Energy Tariff:                           $15.00
Subtotal:                                         $453.78
GST (10%):                                         $45.38
Amount Due:                                       $499.16

Payment Options: BPAY Biller Code 87432 | Ref: 9823441022
Direct Debit, Credit Card, or Online at agl.com.au
""",
        "problem": "Tracking and coding utility bills across 12 office locations monthly",
        "solution_time_ms": 195,
    },

    "application_form": {
        "filename": "Credit_Application_Form_OrbitTech.pdf",
        "text": """
TRADE CREDIT APPLICATION FORM
Meridian Consulting Group Pty Ltd — Accounts Department
Form Number: TCA-2024-0087

SECTION A: APPLICANT DETAILS
Applicant Name: Orbit Technologies Pty Ltd
Trading Name: Orbit Tech
ABN: 55 123 987 654
Date of Incorporation: 15/06/2018
Business Type: Private Company

SECTION B: CONTACT INFORMATION
Registered Address: 88 Tech Valley Road, Brisbane QLD 4000
Postal Address: PO Box 4421, Brisbane QLD 4001
Contact Person: Lisa Pham
Title: Accounts Manager
Phone: +61 7 3000 9988
Email: l.pham@orbittech.com.au
Website: www.orbittech.com.au

SECTION C: CREDIT REQUEST
Credit Limit Requested: $50,000.00
Payment Terms Requested: 30 days
Purpose: Purchase of IT hardware and services

SECTION D: BANK REFERENCE
Bank Name: Westpac Banking Corporation
Branch: Brisbane CBD
BSB: 034-002
Account Number: XXXX XXXX 3307

SECTION E: TRADE REFERENCES
Reference 1: Delta Systems Pty Ltd | Contact: Tom Reid | Ph: +61 7 3100 5544
Reference 2: Apex Solutions | Contact: Jenny Wu | Ph: +61 7 3200 6612

DECLARATION
I/We declare the information provided is true and correct.
Authorised Signature: Lisa Pham — Accounts Manager
Date: 20/03/2024

For Office Use Only:
Application Reference: REF-2024-0087
Received By: James Wilson | Date Received: 22/03/2024
""",
        "problem": "Manual data entry from application forms into CRM, taking 20+ min each",
        "solution_time_ms": 380,
    },

    "report": {
        "filename": "Q1_Financial_Performance_Report_2024.pdf",
        "text": """
MERIDIAN CONSULTING GROUP PTY LTD
Q1 FINANCIAL PERFORMANCE REPORT
January – March 2024

Prepared By: Michael Torres, CFO
Prepared For: Board of Directors
Report Date: 05/04/2024
Fiscal Year: FY2024

EXECUTIVE SUMMARY
Meridian Consulting Group achieved strong revenue growth in Q1 2024, recording total revenue of $1.24M against a target of $1.1M, representing a 12.7% outperformance. EBITDA margins improved to 28.4% compared to 24.1% in Q1 2023.

TABLE OF CONTENTS
1. Revenue Analysis
2. Cost Breakdown
3. Client Performance
4. Pipeline Overview
5. Recommendations

1. REVENUE ANALYSIS
Total Revenue Q1 2024:        $1,240,000
Total Revenue Q1 2023:          $980,000
YoY Growth:                        26.5%

Revenue by Service Line:
Strategy Consulting:            $620,000  (50%)
Technology Advisory:            $372,000  (30%)
Training & Workshops:           $248,000  (20%)

2. COST BREAKDOWN
Staff Costs:                    $620,000
Overhead & Office:               $89,000
Marketing:                       $42,000
Technology & Tools:              $38,000
Total Costs:                    $789,000
EBITDA:                         $451,000

3. RECOMMENDATIONS
- Increase Technology Advisory headcount by 2 FTEs (Q2 priority)
- Launch Brisbane office in Q3 2024
- Renegotiate supplier contracts for potential $18,000 annual saving

Appendix A: Detailed GL Report
Appendix B: Client Revenue Breakdown
""",
        "problem": "Manually extracting KPIs from lengthy board reports for dashboard updates",
        "solution_time_ms": 460,
    },
}
