from fpdf import FPDF
import json

class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica","B",20)
        self.set_text_color(33,37,41)
        title="dahoncho financial reports"
        width=self.get_string_width(title)+6
        self.set_x((210-width)/2)
        self.cell(width,20,title,align="C")
        self.ln(10)
    
    def section_title(self,title):
        self.set_font("Helvetica","B",12)
        self.set_fill_color(200, 220, 255)
        self.set_text_color(52,58,64)
        width=self.get_string_width(title)+6
        self.set_x((210-width)/2)
        self.cell(width,20,title,align="L")
        self.ln(15)

    def section_body(self,text):
        self.set_font("Helvetica","",11)
        self.set_text_color(33,37,41)
        self.multi_cell(180,5,text)
        self.ln(2)

    def bullet_list(self,items):
        self.set_font("Helvetica","",11)
        for item in items:
            self.cell(5)
            self.multi_cell(150,7,f"- {item}",new_x="LMARGIN",new_y="NEXT")
    
    def footer(self):
        self.set_y(-20)
        logo_width=10
        logo_path="public/assets/dahoncho.png"
        x_pos =(210-logo_width)/2
        self.image(logo_path,x=x_pos,w=logo_width)



ai_report= """
```json
[
  {
    "type": "title",
    "content": "Executive Summary"
  },
  {
    "type": "paragraph",
    "content": "This report reviews the financial health, performance trends, and valuation insights for Palantir Technologies Inc. (PLTR) and American Express Company (AXP). The analysis encompasses annual trends, quarterly performance, and intrinsic value assessments using Discounted Cash Flow (DCF) and Graham's valuation methods."
  },
  {
    "type": "title",
    "content": "Financial Trends Analysis (Annual)"
  },
  {
    "type": "paragraph",
    "content": "Palantir (PLTR) has exhibited strong revenue growth, increasing from $1.54 billion in 2021 to $2.87 billion in 2024. Profitability has significantly improved, with net income shifting from a loss of -$520 million in 2021 to a profit of $462 million in 2024.  Free Cash Flow (FCF) is positive and trending upward, reaching $1.14 billion in 2024. The company maintains a strong cash position, indicating solid financial health. PLTR does not currently pay dividends."
  },
  {
    "type": "paragraph",
    "content": "American Express (AXP) demonstrates consistent revenue growth, from $43.15 billion in 2021 to $65.95 billion in 2024.  It maintains consistent profitability with net income increasing from $8.06 billion in 2021 to $10.13 billion in 2024. AXP generates substantial FCF, with $12.14 billion in 2024. AXP pays a dividend, with annual payments of approximately $1.45 - $2.00 billion. While the company has significant cash reserves, it also carries substantial liabilities."
  },
  {
    "type": "title",
    "content": "Quarterly Performance Review"
  },
  {
    "type": "paragraph",
    "content": "PLTR's quarterly revenue has shown consistent growth from $634M (2024-03) to $884M (2025-03).  Net Income and Earnings Per Share (EPS) are trending upward, and Return on Assets (ROA) has improved. Free Cash Flow is robust and increasing.  Assets are growing faster than liabilities.  Investment in Research and Development has also increased."
  },
  {
    "type": "paragraph",
    "content": "AXP's quarterly revenue fluctuates but remains relatively stable around $9.3B to $9.8B.  Net Income and EPS are generally strong. ROA is stable. Free Cash Flow is substantial, but has decreased slightly in the last year. The company continues to comfortably cover dividend payments. Assets and Liabilities are both very large and growing at a similar pace."
  },
  {
    "type": "title",
    "content": "Intrinsic Value Analysis"
  },
  {
    "type": "paragraph",
    "content": "Based on DCF and Graham valuations, PLTR appears significantly overvalued relative to its current market price. It has strong projected earnings growth for the next year. The current price is far above the 30% safety margin level, indicating higher risk. AXP also appears overvalued based on DCF and Graham valuations. The projected earnings growth for the next year is positive.  The current price is above the 30% safety margin level."
  },
  {
    "type": "title",
    "content": "Conclusion"
  },
  {
    "type": "paragraph",
    "content": "AXP presents a more stable profile with consistent profitability and dividend payouts, making it potentially more attractive to long-term value investors.  However, it exhibits slower growth compared to PLTR and shows signs of overvaluation. PLTR demonstrates higher growth potential but carries greater risk due to its relatively recent profitability and overvaluation based on intrinsic value calculations.  Both companies have strengths and weaknesses depending on investment strategy and risk tolerance."
  }
]
```
"""
cleaned_report = ai_report.replace("```","").replace("json","").strip().lower()
ai_json_report = json.loads(cleaned_report)


    



pdf = PDFReport()
pdf.add_page()
pdf.set_auto_page_break(auto=True,margin=5)

for e in ai_json_report:
    if e['type']=="title":
        pdf.section_title(e['content'])
    if e['type']=='paragraph':
        pdf.section_body(e['content'])
    if e['type']=='bullets':
        pdf.bullet_list(e['content'])

pdf.footer()
pdf.output(r'ai_reports/test.pdf')