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
            self.multi_cell(170,7,f"- {item}",new_x="LMARGIN",new_y="NEXT")
    
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
            self.bullet_list(e['content'].strip())
      
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
    "content": "intel (intc) - 7 powers analysis",
    "type": "title"
  },
  {
    "content": "analyzing intel (intc) through the lens of hamilton helmer's 7 powers reveals a complex picture. while intel once dominated the semiconductor industry, shifts in technology and increased competition have impacted its power profile. the assessment below uses publicly available information.",
    "type": "paragraph"
  },
  {
    "content": "1. scale economies",
    "type": "title"
  },
  {
    "content": "intel benefits from significant scale economies in manufacturing. massive fabrication plants ('fabs') require enormous capital investment, creating a barrier to entry. the cost per chip decreases as production volume increases.",
    "type": "paragraph"
  },
  {
    "content": "however, intel's recent struggles with process technology (e.g., 7nm delays) have eroded this advantage. competitors like tsmc (using advanced processes) are producing chips for amd and nvidia, challenging intel's cost leadership. these delays have impacted intel's ability to leverage its scale effectively.",
    "type": "paragraph"
  },
  {
    "content": "2. network economies",
    "type": "title"
  },
  {
    "content": "network effects are relatively weak for intel. while widespread adoption of intel processors creates a larger market for compatible software, this is primarily a 'one-sided' network effect. the value to users doesn't increase dramatically with each additional user, unlike 'two-sided' networks (e.g., social media).",
    "type": "paragraph"
  },
  {
    "content": "3. counter-positioning",
    "type": "title"
  },
  {
    "content": "counter-positioning is generally absent for intel. disruptive technologies and business models have bypassed intel rather than being directly confronted by them. competitors like arm have created power-efficient architectures for mobile devices that intel initially struggled to address, showcasing a failure to effectively counter-position against disruptive innovations.",
    "type": "paragraph"
  },
  {
    "content": "4. switching costs",
    "type": "title"
  },
  {
    "content": "switching costs exist, but are not overwhelmingly strong. for consumers, switching to a different cpu architecture requires a new motherboard and potentially new ram. for enterprise customers, re-architecting systems for different processors involves significant effort and expense. however, cloud computing and virtualization technologies have reduced these switching costs to some extent. compatibility issues and software optimization also factor into these costs.",
    "type": "paragraph"
  },
  {
    "content": "5. branding",
    "type": "title"
  },
  {
    "content": "intel possesses a strong brand, built over decades of dominance in the pc market. the 'intel inside' campaign established high consumer recognition. however, the brand's strength has diminished somewhat in recent years due to increased competition and perceived technological stagnation. amd's resurgence has offered credible alternatives.",
    "type": "paragraph"
  },
  {
    "content": "6. cornered resource",
    "type": "title"
  },
  {
    "content": "intel holds some cornered resources, primarily in the form of intellectual property and manufacturing expertise. patents related to chip design and manufacturing processes provide a degree of exclusivity. however, the increasing importance of specialized chip designs (e.g., gpus, ai accelerators) and the rise of foundries like tsmc have reduced the value of intel's cornered resources relative to the broader semiconductor landscape.",
    "type": "paragraph"
  },
  {
    "content": "7. process power",
    "type": "title"
  },
  {
    "content": "process power is limited for intel. while intel has internal processes for chip design and manufacturing, these haven't consistently delivered superior performance or efficiency compared to competitors. recent execution issues in process technology advancements have weakened any process power advantage.",
    "type": "paragraph"
  },
  {
    "content": "nvidia (nvda) - 7 powers analysis",
    "type": "title"
  },
  {
    "content": "nvidia (nvda) exhibits a stronger profile across several of helmer's 7 powers compared to intel. its focus on specialized processors (gpus) for gaming, data centers, and automotive applications has created defensible advantages. the assessment below uses publicly available information.",
    "type": "paragraph"
  },
  {
    "content": "1. scale economies",
    "type": "title"
  },
  {
    "content": "nvidia benefits from scale economies in gpu design and manufacturing, although less directly than intel in manufacturing. nvidia outsources its manufacturing to foundries like tsmc, allowing it to focus on design and architecture. the cost of developing advanced gpu architectures is substantial, favoring companies with high sales volumes to amortize these costs.",
    "type": "paragraph"
  },
  {
    "content": "2. network economies",
    "type": "title"
  },
  {
    "content": "nvidia exhibits moderate network effects. the cuda platform, used for parallel computing on nvidia gpus, creates a developer ecosystem. the more developers who use cuda, the more valuable it becomes, leading to increased adoption and a larger pool of skilled programmers. this increases the attractiveness of nvidia gpus for machine learning and other compute-intensive tasks.",
    "type": "paragraph"
  },
  {
    "content": "3. counter-positioning",
    "type": "title"
  },
  {
    "content": "nvidia has demonstrated counter-positioning capabilities. they adapted their gpu technology, originally designed for gaming, to address the emerging markets of ai and data centers. this involved significant investment in software (cuda) and specialized hardware, creating a strong position in these new areas, challenging established players in the traditional cpu market. this allows nvidia to operate in high-growth segments that established players struggle to adapt to quickly.",
    "type": "paragraph"
  },
  {
    "content": "4. switching costs",
    "type": "title"
  },
  {
    "content": "switching costs are significant for nvidia, especially in enterprise applications. companies that have invested in cuda-based software and infrastructure face high costs to switch to alternative platforms. the expertise and libraries built around cuda create a vendor lock-in effect.",
    "type": "paragraph"
  },
  {
    "content": "5. branding",
    "type": "title"
  },
  {
    "content": "nvidia possesses a strong brand, particularly among gamers and ai researchers. the geforce brand is synonymous with high-performance gaming gpus, and the tesla brand is well-recognized in the data center market. this strong brand recognition helps nvidia command premium prices and maintain market share.",
    "type": "paragraph"
  },
  {
    "content": "6. cornered resource",
    "type": "title"
  },
  {
    "content": "nvidia's cornered resources include its gpu architecture, cuda platform, and deep expertise in parallel computing. these assets are difficult for competitors to replicate and provide a sustainable competitive advantage.",
    "type": "paragraph"
  },
  {
    "content": "7. process power",
    "type": "title"
  },
  {
    "content": "nvidia exhibits strong process power. its ability to consistently design high-performance gpus and effectively manage its relationship with manufacturing partners like tsmc gives it a competitive edge. this includes optimizing designs for specific manufacturing processes and collaborating closely with foundries to improve performance and efficiency.",
    "type": "paragraph"
  },
  {
    "content": "vistra energy (vst) - 7 powers analysis",
    "type": "title"
  },
  {
    "content": "vistra energy (vst), an integrated retail electricity and power generation company, presents a unique case study when analyzed through the 7 powers framework. the analysis below leverages publicly available information.",
    "type": "paragraph"
  },
  {
    "content": "1. scale economies",
    "type": "title"
  },
  {
    "content": "vistra achieves scale economies through its large generation fleet and retail operations. spreading fixed costs of power plants and customer acquisition across a large base reduces per-unit costs. efficient dispatch of power from its diverse generation assets also contributes to cost advantages.",
    "type": "paragraph"
  },
  {
    "content": "2. network economies",
    "type": "title"
  },
  {
    "content": "network effects are generally weak for vistra. electricity is a commodity, and the value to a customer doesn't increase significantly with more customers on vistra's network. however, some minor network effects may exist related to smart grid technologies and demand response programs, where aggregated customer participation can improve grid stability.",
    "type": "paragraph"
  },
  {
    "content": "3. counter-positioning",
    "type": "title"
  },
  {
    "content": "counter-positioning is potentially relevant as the energy industry transitions to renewables. vistra, with its legacy fossil fuel generation assets, may find it challenging to rapidly adapt to a decentralized, renewable-powered grid. competitors focused solely on renewable energy may have a counter-positioning advantage.",
    "type": "paragraph"
  },
  {
    "content": "4. switching costs",
    "type": "title"
  },
  {
    "content": "switching costs for retail electricity customers are relatively low, especially in deregulated markets. customers can easily switch providers, making customer retention a key challenge. however, vistra can increase switching costs through bundled services, loyalty programs, and long-term contracts.",
    "type": "paragraph"
  },
  {
    "content": "5. branding",
    "type": "title"
  },
  {
    "content": "branding plays a moderate role for vistra. in competitive retail markets, a strong brand can differentiate vistra from competitors and attract customers. however, electricity is largely viewed as a commodity, so brand strength is less critical than price and reliability.",
    "type": "paragraph"
  },
  {
    "content": "6. cornered resource",
    "type": "title"
  },
  {
    "content": "vistra's cornered resources include its existing power generation fleet, particularly in regions with limited transmission capacity. these assets provide a competitive advantage in meeting local demand. however, the increasing availability of renewable energy and distributed generation is eroding the value of this cornered resource.",
    "type": "paragraph"
  },
  {
    "content": "7. process power",
    "type": "title"
  },
  {
    "content": "vistra's process power lies in its ability to efficiently operate its generation fleet and manage its retail operations. this includes optimizing fuel procurement, minimizing downtime, and effectively managing customer acquisition and retention. expertise in navigating regulatory environments is also critical.",
    "type": "paragraph"
  }
]
  """
 
  pdf = PDFReport(report)
  pdf_buffer=pdf.generate()
  
