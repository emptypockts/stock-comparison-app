from fpdf import FPDF
import json
from io import BytesIO
from datetime import datetime
import re
import os
import ast
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]
ai_report_collections = db["aiTasks"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR,'ai_reports','DejaVuSans.ttf')


class PDFReport(FPDF):
    def __init__(self,task_id):
        super().__init__()
        report=ai_report_collections.find_one({
           "task_id":task_id
        })
        if not report or 'assistant' not in report:
           raise ValueError(f"my guy, check the task_id, i did not find any report with {task_id}")
        self.ai_report=report['assistant']
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
  task_id = "7b724346-7823-4116-93f2-53c4bd8cd913"
  
 
  pdf = PDFReport(task_id)
  pdf_buffer=pdf.generate()
  
