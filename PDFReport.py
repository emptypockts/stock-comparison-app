from fpdf import FPDF
import json
from io import BytesIO
from datetime import datetime
import re
import os
import ast
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR,'ai_reports','DejaVuSans.ttf')


class PDFReport(FPDF):
    def __init__(self,ai_report):
        super().__init__()
        self.ai_report=ai_report
        self.add_font('DejaVu','',FONT_PATH)
        self.add_font('DejaVu', 'B', FONT_PATH)

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
        logo_path=f"{BASE_DIR}/public/assets/dahoncho.png"
        x_pos =(210-logo_width)/2
        self.image(logo_path,x=x_pos,w=logo_width)

    def generate(self):
      print('generating report now')
      if isinstance(self.ai_report, str):
        try:
          ai_json_report= json.loads(self.ai_report)
        except json.JSONDecodeError:
          try:
            py_obj = ast.literal_eval(self.ai_report)
            ai_json_report=py_obj
          except Exception as e:
            raise ValueError(f"error trying to parse json or python structure {e}")           
      else:
         print('proceeding now')
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
      self.output(f"{BASE_DIR}/ai_reports/{today}.pdf")
      pdf_buffer.seek(0)

      return pdf_buffer,today

if __name__=='__main__':
  report=[{'type': 'title', 'content': 'executive summary'}, {'type': 'paragraph', 'content': 'this report reviews the financial health, performance trends, and valuation insights for intel corp (intc).'}, {'type': 'title', 'content': 'financial trends analysis (annual)'}, {'type': 'paragraph', 'content': "intel's financial performance from 2021 to 2024 reveals a concerning trend. revenue shows a clear decline, peaking in 2021 at $79.02 billion and decreasing to $53.10 billion in 2024. net income has been highly volatile, swinging from a $19.87 billion profit in 2021 to a substantial loss of $18.76 billion in 2024."}, {'type': 'paragraph', 'content': 'a major area of concern is the free cash flow (fcf), which has gone from a positive $9.13 billion in 2021 to a negative -$15.66 billion in 2024, indicating a struggle to generate sufficient cash from operations.  while intel continues to pay dividends, the declining revenue, net income, and significantly negative free cash flow raise concerns about the sustainability of these payments. the dividend was significantly reduced in 2024 as compared to previous years.'}, {'type': 'paragraph', 'content': 'earnings per share (eps) follows the trend of net income, declining from $4.89 in 2021 to -$4.38 in 2024. return on assets (roa) mirrors the profitability issues, going from a healthy 12% in 2021 to a negative -1% in 2024, indicating inefficient asset utilization and losses.'}, {'type': 'bullets', 'content': ['declining performance: intel is facing significant challenges with declining revenue, profitability, and free cash flow.', 'dividend risk: the negative free cash flow puts the dividend at risk of further cuts or potential suspension.', 'turnaround needed: intel needs to execute a successful turnaround strategy to restore growth and profitability.']}, {'type': 'title', 'content': 'quarterly performance review'}, {'type': 'paragraph', 'content': "intel's quarterly performance reveals fluctuating but largely stable revenue, ranging between $12.7 billion and $13.3 billion. however, the company is currently unprofitable, as indicated by negative net income, eps, and roa in all reported quarters. the largest loss occurred in q3 2024. free cash flow is negative, although operating cash flow turned positive in the latest quarter (2025-03-29)."}, {'type': 'paragraph', 'content': 'total debt and current liabilities have increased overall during the period, reflecting a potentially concerning trend. the filing date for the most recent data, 2025-03-29, should be verified for accuracy.'}, {'type': 'title', 'content': 'intrinsic value analysis'}, {'type': 'paragraph', 'content': 'based on the provided valuation data, intel appears significantly overvalued. the dcf model suggests an intrinsic value of negative $51.91 compared to a current price of $20.14. the graham value is calculated as $0.00, also suggesting overvaluation. the estimated earnings growth for the next year is 5.0%, which is relatively low.'}, {'type': 'paragraph', 'content': "the current price does not offer a 30% safety margin for either the dcf or graham valuation models, indicating higher risk. this suggests that intel's current market price is not supported by its estimated intrinsic value or growth prospects, signaling a potentially risky investment from a value perspective."}, {'type': 'title', 'content': 'conclusion'}, {'type': 'paragraph', 'content': "in summary, intel faces significant financial challenges including declining revenue, negative free cash flow, and unprofitability. intrinsic value analysis suggests the stock is overvalued, and the negative fcf adds further risk. a turnaround strategy is needed to improve the company's financial health and restore investor confidence. a consistent value score of 3 further indicates mixed signals. the company maintains dividend payments, but their sustainability depends on improved financial performance and free cash flow."}]
  
 
  pdf = PDFReport(report)
  pdf_buffer=pdf.generate()
  
