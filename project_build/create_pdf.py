from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Project Novelty & Unique Selling Points (USPs)', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    
    # 1. Blind AI
    pdf.chapter_title('1. "Blind" Artificial Intelligence (The Core Novelty)')
    pdf.chapter_body(
        'The biggest innovation is that the Server (AI) makes a diagnosis without ever "seeing" the patient\'s data.\n\n'
        '- Standard AI: You send your medical data to a server. The server can read it, save it, or misuse it.\n'
        '- Your Project: You send encrypted mathematical noise to the server. The server runs calculations on this noise and returns an encrypted result. At no point does the raw data (e.g., Blood Pressure: 120) exist on the server.'
    )

    # 2. Hybrid Protocol
    pdf.chapter_title('2. Hybrid Client-Server Activation Protocol (Technical Breakthrough)')
    pdf.chapter_body(
        'This is the key technical innovation solving the biggest bottleneck in Encrypted Deep Learning.\n\n'
        '- The Problem: Homomorphic Encryption (HE) is essentially impossible/extremely slow for complex non-linear functions (like Sigmoid/ReLU) required for Deep Learning.\n'
        '- Your Solution: A Split-Computation Architecture.\n'
        '    * The Server handles the heavy Linear layers (Matrix Multiplication) on encrypted data.\n'
        '    * The Client handles the Non-Linear activations (Sigmoid/ReLU) locally.\n'
        '- Why it matters: This makes Privacy-Preserving AI computationally feasible and fast enough for real-world use.'
    )

    # 3. Privacy
    pdf.chapter_title('3. End-to-End Privacy (GDPR & HIPAA Compliant)')
    pdf.chapter_body(
        'Your application is "Privacy by Design." It adheres to strict medical data regulations by default. Since the encryption keys are generated only on the client side, even the developers of the AI cannot access the user\'s health records.'
    )

    # 4. Scalability
    pdf.chapter_title('4. Multi-Disease Scalability')
    pdf.chapter_body(
        'Your project demonstrates Architecture Agnosticism, proving it is a platform, not just a script.\n\n'
        '- Successfully runs a Diabetes Model (8 features).\n'
        '- Successfully runs a Heart Disease Model (13 features).\n'
        '- It can be adapted to any tabular medical data without changing the core security code.'
    )

    # 5. Visualization
    pdf.chapter_title('5. Interactive Educational Visualization')
    pdf.chapter_body(
        'Unlike black-box crypto tools, your dashboard includes a Live Security Audit Log and Ciphertext Viewer. '
        'It demystifies high-level cryptography (CKKS) for non-experts, allowing users to visually confirm that their data '
        'is being turned into gibberish before it leaves their browser.'
    )
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 6, 'Summary Pitch', 0, 1, 'L')
    pdf.set_font('Arial', 'I', 11)
    pdf.multi_cell(0, 6, 
        '"My project implements a Privacy-Preserving Machine Learning (PPML) system using CKKS Homomorphic Encryption. '
        'Unlike traditional AI that requires data access, my system allows a server to perform inference on completely encrypted data. '
        'I addressed the limitations of HE in Deep Learning by designing a Hybrid Client-Server Protocol, ensuring mathematically guaranteed privacy for patients while retaining the predictive accuracy of modern AI."'
    )

    if not os.path.exists('docs'):
        os.makedirs('docs')
        
    pdf.output('docs/Project_Novelties.pdf', 'F')
    print("PDF Generated: docs/Project_Novelties.pdf")

if __name__ == "__main__":
    create_pdf()
