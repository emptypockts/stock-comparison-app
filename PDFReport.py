from fpdf import FPDF
import json
from io import BytesIO
from datetime import datetime
import re

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
      I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start.

add a ticker in the ticker field at the top of this page
```json
{
"title": "7 Powers Analysis of Intel Corporation (INTC)",
"content": "This report analyzes Intel Corporation (INTC) through the lens of Hamilton Helmer's 7 Powers framework. The analysis considers publicly available information as of today, October 26, 2023, and is subject to the limitations of relying on external sources. URL for Hamilton Helmer's 7 Powers : https://www.7powers.com/",

"type": "paragraph",
"content": "Intel, a semiconductor giant, has historically dominated the CPU market for PCs and servers. However, increasing competition and internal challenges have impacted its market position. This analysis aims to assess Intel's current competitive advantages and potential for future sustainable profitability using the 7 Powers framework." ,

"type": "title",
"content": "1. Scale Economies" ,

"type": "paragraph",
"content": "Scale economies exist when a company's unit costs decrease as its production volume increases. This stems from spreading fixed costs over a larger output. The semiconductor industry inherently benefits from scale economies due to the massive capital expenditures required for fabrication facilities (fabs)." ,

"type": "paragraph",
"content": "Intel possesses significant scale economies due to its large-scale manufacturing capabilities and substantial investments in R&D and fabrication facilities. Having its own fabs historically provided a cost advantage. However, reliance on internal manufacturing has proven to be a disadvantage recently compared to competitors like AMD that uses foundries as TSMC. This advantage is potentially weakening." ,

"type": "paragraph",
"content": "Conclusion: Intel currently possesses scale economies but its advantage is eroding because the technology of competitors is better than their internal technologies. URL used : https://www.intc.com/" ,

"type": "title",
"content": "2. Network Economies" ,

"type": "paragraph",
"content": "Network economies exist when the value of a product or service increases as more users adopt it. This creates a powerful advantage because new users benefit existing users, creating a virtuous cycle." ,

"type": "paragraph",
"content": "Intel benefits from indirect network effects. Its dominance in CPUs has created a large ecosystem of software developers and hardware manufacturers that optimize their products for Intel's architecture. This 'compatibility' factor encourages further adoption of Intel processors. However, the rise of ARM-based processors is challenging this advantage." ,

"type": "paragraph",
"content": "Conclusion: Intel possesses moderate network economies, primarily through its established ecosystem. However, this power is being challenged by the growth of alternative architectures like ARM. URL used : https://www.arm.com/" ,

"type": "title",
"content": "3. Counter Positioning" ,

"type": "paragraph",
"content": "Counter-positioning occurs when a newcomer adopts a new, superior business model that an established incumbent cannot easily replicate because it would damage their existing business. It's about doing something *different* that the incumbent is *unwilling* or *unable* to do." ,

"type": "paragraph",
"content": "AMD's successful shift to a fabless manufacturing model using TSMC is an example of counter-positioning. Intel, heavily invested in its own fabrication facilities, has been slower to adapt and has faced challenges in process technology. Moving away from internal manufacturing presents huge balance sheet issues and a change in their whole business model, which makes it difficult to do." ,

"type": "paragraph",
"content": "Conclusion: AMD's fabless model has created a degree of counter-positioning against Intel. Intel's historical commitment to its own fabs makes it difficult to fully embrace the foundry model without significant disruption. URL used : https://www.amd.com/",

"type": "title",
"content": "4. Switching Costs" ,

"type": "paragraph",
"content": "Switching costs are the costs (time, money, effort, or psychological) that a customer incurs when changing from one product or service to another. High switching costs can lock in customers and create a competitive advantage." ,

"type": "paragraph",
"content": "Switching costs for CPUs are relatively low for individual consumers. However, for enterprise customers (e.g., data centers), switching costs can be higher due to software compatibility, infrastructure changes, and testing requirements. These costs provide some stickiness for Intel." ,

"type": "paragraph",
"content": "Conclusion: Intel benefits from moderate switching costs, particularly in the enterprise segment. URL used: https://www.statista.com/statistics/183476/x86-market-share-of-intel-and-amd/" ,

"type": "title",
"content": "5. Branding" ,

"type": "paragraph",
"content": "A strong brand can create a perceived differentiation, command a price premium, and increase customer loyalty." ,

"type": "paragraph",
"content": "Intel possesses a strong brand reputation, particularly among older generations of computer users. The 'Intel Inside' campaign was highly successful in establishing brand recognition. However, the brand's power has diminished somewhat due to recent performance challenges and increased competition." ,

"type": "paragraph",
"content": "Conclusion: Intel's brand remains valuable, but its strength has weakened due to recent challenges. URL used : https://www.intel.com/content/www/us/en/newsroom/newsroom.html" ,

"type": "title",
"content": "6. Cornered Resource" ,

"type": "paragraph",
"content": "A cornered resource is preferential access to an asset that independently enhances value. This could be exclusive access to a key technology, a prime location, or a scarce natural resource." ,

"type": "paragraph",
"content": "Intel historically possessed a cornered resource in its advanced manufacturing process technology. This allowed them to produce more powerful and efficient chips than competitors. However, this advantage has eroded as competitors like TSMC have surpassed Intel in process technology leadership. Now it´s more a liability than an asset." ,

"type": "paragraph",
"content": "Conclusion: Intel's cornered resource in process technology has been lost, negatively impacting its competitive position. URL used : https://www.tomshardware.com/news/tsmc-vs-intel-node-comparison",

"type": "title",
"content": "7. Process Power" ,

"type": "paragraph",
"content": "Process power refers to unique organizational capabilities and routines that allow a company to operate more efficiently or effectively than its rivals. It's about *how* a company does things." ,

"type": "paragraph",
"content": "Intel's historical process power was rooted in its vertically integrated model and its ability to tightly control the design and manufacturing of its chips. However, recent challenges in process technology suggest that its internal processes have become less effective. The company is undergoing significant restructuring efforts to improve its operational efficiency." ,

"type": "paragraph",
"content": "Conclusion: Intel's process power is currently under pressure, and the company is actively working to improve its internal operations. URL used : https://www.intc.com/news-events/press-releases",

"type": "title",
"content": "Overall Conclusion",

"type": "paragraph",
"content": "Based on this 7 Powers analysis, Intel faces significant competitive challenges. Its scale economies and network economies are being threatened by competitors, and its cornered resource in process technology has been lost. While it retains some advantages in brand and switching costs, these are not sufficient to guarantee long-term sustainable profitability without significant improvements in its process technology and strategic direction. AMD has a significant advantage due to their fabless business model. Intel needs to regain technological leadership and adapt to the changing landscape of the semiconductor industry to regain its competitive edge. "
}
```
"""
  pdf = PDFReport(report)
  pdf_buffer=pdf.generate()
  
