from fpdf import FPDF
import json
from io import BytesIO
from datetime import datetime
import re

class PDFReport(FPDF):
    def __init__(self,ai_report):
        super().__init__()
        self.ai_report=ai_report
        self.add_font('DejaVu','','./ai_reports/DejavuSans.ttf')
        self.add_font('DejaVu', 'B', './ai_reports/DejaVuSans.ttf')

    def header(self):
        self.set_font("DejaVu","B",20)
        self.set_text_color(220, 220, 220)
        self.rect(0, 0, 210, 297, style='F')
        self.set_fill_color(0, 0, 0)
        title="dahoncho financial reports"
        width=self.get_string_width(title)+6
        self.set_x((210-width)/2)
        self.cell(width,20,title,align="C")
        self.ln(20)
    
    def section_title(self,title):
        self.set_font("DejaVu","B",12)
        self.set_text_color(180, 180, 180)
        width=self.get_string_width(title)+6
        self.set_x((210-width)/2)
        self.cell(width,20,title,align="L")
        self.ln(15)

    def section_body(self,ai_text):
        self.set_font("DejaVu","",11)
        self.set_text_color(150, 150, 150)
        self.multi_cell(180,5,ai_text)
        self.ln(2)

    def bullet_list(self,ai_items):
        self.set_font("DejaVu","",11)
        self.set_text_color(150, 150, 150)
        for item in ai_items:
            self.cell(5)
            self.multi_cell(170,7,f"- {item.strip()}",new_x="LMARGIN",new_y="NEXT")
    
    def footer(self):
        self.set_y(-20)
        logo_width=10
        logo_path="public/assets/dahoncho.png"
        x_pos =(210-logo_width)/2
        self.image(logo_path,x=x_pos,w=logo_width)

    def generate(self):
      if isinstance(self.ai_report, str):
        ai_json_report= json.loads(self.ai_report)
      else:
         ai_json_report=self.ai_report
      self.add_page()
      self.set_auto_page_break(auto=True,margin=25)
      for e in ai_json_report:
        if e['type']=="title":
            self.section_title(e['content'].strip())
        if e['type']=='paragraph':
            self.section_body(e['content'].strip())
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
  [
    {
      "content": "financial analysis report: intel corp. (intc)",
      "type": "title"
    },
    {
      "content": "this report provides a comprehensive financial analysis of intel corp. (intc), encompassing trend analysis, quarterly performance reviews, and intrinsic value assessments. the analysis utilizes data from 2021 to the most recent available quarter, including revenue, profitability, cash flow, and valuation metrics.",
      "type": "paragraph"
    },
    {
      "content": "1. executive summary",
      "type": "title"
    },
    {
      "content": "this report reviews the financial health, performance trends, and valuation insights for intel corp. (intc). key observations include declining revenue and profitability, negative free cash flow, and mixed valuation signals.",
      "type": "paragraph"
    },
    {
      "content": "2. financial trends analysis (annual)",
      "type": "title"
    },
    {
      "content": "intel's annual financial performance reveals a concerning downward trend across several key metrics. revenue has declined significantly from 79.024 billion in 2021 to 53.101 billion in 2024. net income has turned negative, with a loss of 18.756 billion in 2024. eps has followed suit, dropping from 4.89 to -4.38 over the same period.",
      "type": "paragraph"
    },
    {
      "content": [
        "revenue: declining trend from 2021 to 2024.",
        "net income & eps: significant decrease, resulting in a net loss by 2024.",
        "free cash flow (fcf): deteriorated significantly, with negative fcf in 2022, 2023 and 2024.",
        "dividends: continued dividend payments despite declining financial performance.",
        "assets & liabilities: total assets and liabilities have generally increased.",
        "return on assets (roa): decreased significantly, reflecting worsening profitability in relation to assets.",
        "r&d: sustained investment in r&d without immediate positive financial impact."
      ],
      "type": "bullets"
    },
    {
      "content": "3. quarterly performance review",
      "type": "title"
    },
    {
      "content": "a review of intel's quarterly performance indicates ongoing challenges. revenue saw slight fluctuations, with some periods of increase followed by decreases.  net income remains negative across all recent quarters, though the losses reduced in q1 2025. notably, operating cash flow turned positive in q1 2025 but free cash flow remains negative.",
      "type": "paragraph"
    },
    {
      "content": [
        "revenue: slight increase followed by decline in the most recent quarters.",
        "net income: negative across all periods, but improving in q1 2025.",
        "eps: mirrors the net income trend with negative values.",
        "operating cash flow: turned positive in q1 2025.",
        "free cash flow: negative in both reported periods.",
        "assets: fluctuated throughout the quarters.",
        "liabilities: increased steadily through q4 2024, then decreased in q1 2025.",
        "return on assets (roa): negative for all quarters.",
        "debt: increased steadily through q4 2024, before decreasing in q1 2025."
      ],
      "type": "bullets"
    },
    {
      "content": "4. intrinsic value analysis",
      "type": "title"
    },
    {
      "content": "intrinsic value analysis using both dcf and graham valuation methods suggest that intel's stock may be overvalued. the dcf model even resulted in a negative intrinsic value. the current market price is outside the 30% safety margin for both valuation models. the estimated earnings growth is 5.0%.",
      "type": "paragraph"
    },
    {
      "content": [
        "dcf valuation: suggests the stock might be overvalued, even indicating a negative intrinsic value.",
        "graham valuation: also suggests potential overvaluation.",
        "safety margin: the current price is not within the 30% safety margin.",
        "growth: low estimated earnings growth for the next year (5.0%)."
      ],
      "type": "bullets"
    },
    {
      "content": "conclusion",
      "type": "title"
    },
    {
      "content": "intel's financial performance presents a mixed picture with significant concerns. declining revenue, negative profitability, and negative free cash flow raise questions about its long-term financial sustainability. while the company continues to pay dividends, the sustainability of these payouts is uncertain given the current financial difficulties. valuation analysis suggests the stock may be overvalued. a 'value score' of 3 reflects the mixed signals. overall, a cautious approach is warranted, and further investigation is needed to determine if intel represents a viable investment opportunity. the company's valuation based on a simple revenue multiple appears reasonable, but it could be overvalued or undervalued depending on profit margins and growth expectations.",
      "type": "paragraph"
    }
  ]
  """
 
  pdf = PDFReport(report)
  pdf_buffer=pdf.generate()
  
