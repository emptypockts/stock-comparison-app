from fpdf import FPDF
import json
from io import BytesIO
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self,ai_report):
        super().__init__()
        self.ai_report=ai_report
    def header(self):
        self.set_font("Helvetica","B",20)
        self.set_text_color(220, 220, 220)
        self.rect(0, 0, 210, 297, style='F')
        self.set_fill_color(0, 0, 0)
        title="dahoncho financial reports"
        width=self.get_string_width(title)+6
        self.set_x((210-width)/2)
        self.cell(width,20,title,align="C")
        self.ln(20)
    
    def section_title(self,title):
        self.set_font("Helvetica","B",12)
        self.set_text_color(180, 180, 180)
        width=self.get_string_width(title)+6
        self.set_x((210-width)/2)
        self.cell(width,20,title,align="L")
        self.ln(15)

    def section_body(self,ai_text):
        self.set_font("Helvetica","",11)
        self.set_text_color(150, 150, 150)
        self.multi_cell(180,5,ai_text)
        self.ln(2)

    def bullet_list(self,ai_items):
        self.set_font("Helvetica","",11)
        self.set_text_color(150, 150, 150)
        for item in ai_items:
            self.cell(5)
            self.multi_cell(170,7,f"- {item}",new_x="LMARGIN",new_y="NEXT")
    
    def footer(self):
        self.set_y(-20)
        logo_width=10
        logo_path="public/assets/dahoncho.png"
        x_pos =(210-logo_width)/2
        self.image(logo_path,x=x_pos,w=logo_width)

    def generate(self):
      cleaned_report = self.ai_report.replace("```","").replace("json","").strip().lower()
      ai_json_report = json.loads(cleaned_report)
      self.add_page()
      self.set_auto_page_break(auto=True,margin=25)
      for e in ai_json_report:
        if e['type']=="title":
            self.section_title(e['content'])
        if e['type']=='paragraph':
            self.section_body(e['content'])
        if e['type']=='bullets':
            self.bullet_list(e['content'])
      
      pdf_buffer= BytesIO()
      self.output(pdf_buffer)
      today= str(datetime.now()).replace(':','_')
      self.output(f"ai_reports/{today}.pdf")
      pdf_buffer.seek(0)

      return pdf_buffer,today

if __name__=='__main__':
  report="""
      ```json
  [
    {
      "type": "title",
      "content": "Executive Summary"
    },
    {
      "type": "paragraph",
      "content": "This report reviews the financial health, performance trends, and valuation insights for NVIDIA (nvda) and Meta Platforms (meta)."
    },
    {
      "type": "title",
      "content": "Financial Trends Analysis (Annual)"
    },
    {
      "type": "paragraph",
      "content": "Nvidia (NVDA) has demonstrated substantial growth from 2023 to 2025. Revenue more than quadrupled, indicating strong demand. Net income, EPS, and free cash flow (FCF) have also increased dramatically, showcasing improved profitability and operating efficiency. Return on Assets has substantially increased, and the company maintains improving financial health with cash holdings increasing faster than liabilities. NVDA consistently pays dividends, although the amounts are relatively small compared to its earnings."
    },
    {
      "type": "paragraph",
      "content": "Meta Platforms (META) has shown steady revenue growth from 2022 to 2024. Net income and EPS have increased, showcasing improved profitability. Return on assets has decreased slightly. META's free cash flow (FCF) is strong, and it maintains a substantial cash balance, managing its liabilities effectively. META recently initiated paying dividends."
    },
    {
      "type": "paragraph",
      "content": "NVDA's revenue and earnings growth have been more explosive than META's in recent years. Both companies are profitable. META returns capital to shareholders through dividends. Both companies appear to be in good financial health. NVDA is growing more quickly, while META is returning more value to shareholders."        
    },
    {
      "type": "title",
      "content": "Quarterly Performance Review"
    },
    {
      "type": "paragraph",
      "content": "Nvidia (NVDA) shows a strong growth trend in revenue from $26.04B to $35.08B over the last three quarters, with increasing net income and EPS. The ROA is improving from 19.3% to 20.1%, suggesting more efficient asset utilization. Free Cash Flow is strong, and dividend payments have fluctuated, increasing significantly in recent quarters. Liabilities have increased, but assets are growing faster. Overall, NVDA exhibits strong growth in revenue, profitability, and efficient asset management."
    },
    {
      "type": "paragraph",
      "content": "Meta (META) demonstrates consistent revenue growth from $36.46B to $42.31B over the last four quarters, with increasing net income and EPS. The ROA is relatively stable. Free Cash Flow is positive, but decreased in the most recent quarter. Consistent dividend payments are made. Liabilities are increasing, but assets are growing faster. Overall, META shows consistent growth in revenue and net income, with stable asset management."
    },
    {
      "type": "paragraph",
      "content": "Both companies demonstrate strong growth, with NVDA showing more rapid revenue growth. NVDA has a significantly higher and improving ROA compared to META. META shows more consistent growth trends and dividend payments. Both companies are in good financial health, with assets growing faster than liabilities. Both NVDA and META display positive financial performance. NVDA exhibits higher growth and profitability (ROA), while META demonstrates more consistent growth and stable asset management."
    },
    {
      "type": "title",
      "content": "Intrinsic Value Analysis"
    },
    {
      "type": "paragraph",
      "content": "Based on the provided data, NVIDIA's current market price ($141.72) is significantly higher than its estimated intrinsic value according to both DCF ($36.09) and Graham ($14.48) valuation models.  The current price is well above the 30% safety margin for both models. NVIDIA has a very strong estimated earnings growth rate (33.97%) for the next year, which could justify a higher valuation if it materializes."
    },
    {
      "type": "paragraph",
      "content": "Meta's current market price ($697.71) is substantially above both its DCF ($360.18) and Graham ($192.13) intrinsic value estimates. The current price is far beyond the 30% safety margin for both valuation models. Meta's estimated earnings growth (10.44%) is positive but lower than that of NVIDIA."
    },
    {
      "type": "bullets",
      "content": [
        "Based purely on these intrinsic value calculations, neither stock appears undervalued. The current prices are significantly higher than the estimated intrinsic values generated by the DCF and Graham models.",
        "NVIDIA stands out with a much higher projected earnings growth rate (33.97%) compared to Meta (10.44%).",
        "Neither stock's current price falls within the 30% safety margin of either valuation model."
      ]
    },
    {
      "type": "paragraph",
      "content": "These valuations are based on the provided data and model assumptions. High growth rates, like NVIDIA's, are not guaranteed. A margin of safety is intended to provide a buffer against errors in valuation and unforeseen risks."
    },
    {
      "type": "title",
      "content": "Conclusion"
    },
    {
      "type": "paragraph",
      "content": "NVIDIA and Meta Platforms both demonstrate positive financial performance, though with differing characteristics. NVIDIA shows explosive growth and higher profitability but appears overvalued based on DCF and Graham valuations. Meta exhibits consistent growth, strong financial health, and has initiated dividends, but also appears overvalued by intrinsic value metrics. Investors should consider the high growth potential of NVIDIA against the more consistent profile of Meta, while carefully evaluating the margin of safety given the current market prices relative to estimated intrinsic values."
    }
  ]"""
  pdf = PDFReport(report)
  pdf_buffer=pdf.generate()
  
