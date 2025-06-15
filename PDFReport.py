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
  report=[{'type': 'title', 'content': 'executive summary'}, {'type': 'paragraph', 'content': 'this report reviews the financial health, performance trends, and valuation insights for intel corp (intc).'}, {'type': 'title', 'content': 'financial trends analysis (annual)'}, {'type': 'paragraph', 'content': "intel's revenue has been declining significantly from 2021 to 2024, peaking at $79.02 billion in 2021 and decreasing to $53.10 billion in 2024. profitability has deteriorated substantially, with net income dropping from $19.87 billion in 2021 to a loss of -$18.76 billion in 2024. consequently, return on assets (roa) declined from 12% to -1%, and eps fell from $4.89 to -$4.38."}, {'type': 'paragraph', 'content': 'free cash flow (fcf) has shifted from $9.13 billion in 2021 to -$15.66 billion in 2024, indicating potential challenges in funding operations and investments. while intel continues to pay dividends, the sustainability is questionable given the negative fcf and net income. dividend payments have decreased from $5.64 billion in 2021 to $1.60 billion in 2024.'}, {'type': 'paragraph', 'content': 'assets have increased from 168.41 billion in 2021 to 196.49 billion in 2024, while liabilities have also increased from 73.02 billion to 91.45 billion. the cash balance has fluctuated but remains significant, increasing from 4.83 billion in 2021 to 8.25 billion in 2024.'}, {'type': 'bullets', 'content': ['declining revenue and profitability indicate potential issues with competitiveness, market share, or increased costs.', "large negative fcf raises concerns about the company's ability to fund operations, r&d, and dividend payments without relying on external financing.", "dividend payments may be at risk of being reduced or suspended if the financial situation doesn't improve.", 'increased liabilities mean intel has more debt.']}, {'type': 'title', 'content': 'quarterly performance review'}, {'type': 'paragraph', 'content': "intel's quarterly revenue saw a slight increase from q1 2024 (12.72b) to q3 2024 (13.28b) but decreased in q1 2025 (12.67b). net income has been negative across all reported quarters, worsening significantly in q3 2024 (-16.64b). eps (basic and diluted) mirrors the net income trend, with significant losses in q3 2024. roa is negative across all quarters."}, {'type': 'paragraph', 'content': 'operating cash flow was negative in q1 2024 but turned positive in q1 2025. free cash flow is negative in both reported quarters, driven by capital expenditures. assets fluctuated but ended lower in q1 2025 compared to q1 2024. liabilities current increased from q1 2024 to q3 2024 but decreased in q1 2025. total debt increased steadily through q4 2024 but decreased in q1 2025.'}, {'type': 'bullets', 'content': ['revenue is fluctuating.', 'profitability is weak, with significant net losses.', 'free cash flow is negative, driven by capital expenditures.', 'financial health shows fluctuations in assets and liabilities.']}, {'type': 'title', 'content': 'intrinsic value analysis'}, {'type': 'paragraph', 'content': "both the dcf and graham valuations suggest intel might be overvalued. the dcf model indicates a negative intrinsic value, and the graham model suggests a value of zero. the current market price of $20.14 is substantially higher than both the dcf and graham intrinsic values, and it's not within the 30% safety margin for either model, suggesting a higher risk. the estimated earnings growth for the next year is 5.0%, which is relatively low."}, {'type': 'title', 'content': 'conclusion'}, {'type': 'paragraph', 'content': 'intel is facing significant financial challenges, including declining revenue, negative income and fcf, and an overvalued stock price based on dcf and graham valuations. its value score indicates it is not strongly aligned with value investing principles due to profitability and cash flow concerns. a deeper look is necessary before any investment decisions are made.'}]
  
 
  pdf = PDFReport(report)
  pdf_buffer=pdf.generate()
  
