import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches

def create_presentation():
    # Setup PDF Pages backend
    pdf_path = "/Users/anjalitiwari/Desktop/Purplle Tech Challenge/Apex_Retail_AI_Presentation.pdf"
    
    with PdfPages(pdf_path) as pdf:
        # Helper to setup a standard presentation slide axis
        def setup_slide(title_text):
            fig, ax = plt.subplots(figsize=(13.33, 7.5)) # 16:9 Aspect Ratio
            fig.patch.set_facecolor('#0b0b0f') # Slate dark bg
            ax.set_facecolor('#0b0b0f')
            
            # Hide axes
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            
            # Add decorative border line or logo indicators
            rect = patches.Rectangle((0.02, 0.02), 0.96, 0.96, linewidth=1, edgecolor='#bb66ff', facecolor='none', alpha=0.3)
            ax.add_patch(rect)
            
            # Slide header title
            if title_text:
                ax.text(0.06, 0.88, title_text, fontsize=28, fontweight='bold', color='#ffffff', family='sans-serif')
                # Underline
                ax.plot([0.06, 0.94], [0.83, 0.83], color='#ff4df0', transform=ax.transAxes, lw=2, alpha=0.8)
                
            return fig, ax

        # =========================================================================
        # SLIDE 1: Title Slide
        # =========================================================================
        fig, ax = setup_slide(None)
        
        # Center gradient simulation
        circle = patches.Circle((0.5, 0.5), 0.4, color='#bb66ff', alpha=0.08, transform=ax.transAxes)
        ax.add_patch(circle)
        
        ax.text(0.5, 0.58, "APEX RETAIL AI", fontsize=48, fontweight='black', color='#ffffff', 
                ha='center', va='center', family='sans-serif')
        ax.text(0.5, 0.48, "Store Intelligence & Customer Conversion Platform", fontsize=18, fontweight='light', color='#d8b4fe', 
                ha='center', va='center', family='sans-serif')
        
        # Line separator
        ax.plot([0.35, 0.65], [0.42, 0.42], color='#ff4df0', transform=ax.transAxes, lw=1.5)
        
        ax.text(0.5, 0.32, "Hackathon Submission Presentation", fontsize=14, color='#8e8e93', 
                ha='center', va='center', family='sans-serif')
        ax.text(0.5, 0.25, "Developed by Anjali Tiwari", fontsize=12, color='#bb66ff', 
                ha='center', va='center', family='sans-serif')
        
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 2: The Business Problem
        # =========================================================================
        fig, ax = setup_slide("THE OFFLINE RETIAL BLIND SPOT")
        
        ax.text(0.06, 0.72, "Why Physical Retail Needs Online-Style Analytics:", fontsize=18, fontweight='semibold', color='#bb66ff')
        
        points = [
            ("No Path Visibility", "Physical stores have historically operated as a data blind spot. Customer journeys, zone dwells, and browsing paths remain completely untracked."),
            ("Checkout Drop-offs", "No systematic way to quantify how many shoppers enter the billing queue but abandon it due to long wait times."),
            ("Disconnect from Sales", "Total foot traffic is rarely linked back to POS transaction records, making it impossible to compute exact shopper conversion rates."),
            ("Inflexible Infrastructure", "Existing tracking solutions require heavy database setup and proprietary hardware, leading to complex and expensive deployments.")
        ]
        
        y_pos = 0.56
        for idx, (head, desc) in enumerate(points):
            # Bullet marker
            ax.text(0.06, y_pos, "•", fontsize=20, color='#ff4df0', fontweight='bold')
            # Point header
            ax.text(0.09, y_pos, head + " :", fontsize=15, fontweight='bold', color='#ffffff')
            # Description text
            ax.text(0.09 + (len(head) * 0.013) + 0.02, y_pos, desc, fontsize=12, color='#8e8e93', wrap=True)
            y_pos -= 0.11
            
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 3: System Architecture
        # =========================================================================
        fig, ax = setup_slide("END-TO-END SYSTEM ARCHITECTURE")
        
        # Draw 4 boxes for the flow chart
        stages = [
            ("CCTV Video Clips", "5 stores, 3 angles\n20 mins per clip"),
            ("Detection Layer", "YOLOv8 Core +\nRe-ID Tracking"),
            ("Intelligence API", "FastAPI + SQLite\nMetrics & Funnels"),
            ("Live Dashboard", "Glassmorphic UI\nHeatmaps & Alerts")
        ]
        
        x_pos = 0.08
        for i, (title, desc) in enumerate(stages):
            # Box
            box = patches.FancyBboxPatch((x_pos, 0.35), 0.16, 0.30, boxstyle="round,pad=0.02", 
                                         linewidth=1.5, edgecolor='#bb66ff', facecolor='#14141c', alpha=0.8)
            ax.add_patch(box)
            
            # Title
            ax.text(x_pos + 0.08, 0.56, title, fontsize=13, fontweight='bold', color='#ffffff', ha='center')
            # Description
            ax.text(x_pos + 0.08, 0.44, desc, fontsize=10, color='#8e8e93', ha='center', va='center')
            
            # Arrow to next (except last)
            if i < 3:
                ax.annotate("", xy=(x_pos + 0.19, 0.50), xytext=(x_pos + 0.22, 0.50),
                            arrowprops=dict(arrowstyle="<-", color='#ff4df0', lw=1.5))
                
            x_pos += 0.23
            
        # Architecture details at bottom
        ax.text(0.06, 0.22, "Key Technologies Used :", fontsize=14, fontweight='bold', color='#bb66ff')
        ax.text(0.28, 0.22, "Python 3.11  |  Ultralytics YOLOv8  |  FastAPI  |  SQLite3  |  HTML5 & Vanilla CSS", fontsize=14, color='#ffffff')
        
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 4: Key Technical Solutions
        # =========================================================================
        fig, ax = setup_slide("KEY TECHNICAL SOLUTIONS")
        
        tech_points = [
            ("Strict Time Correlation", "Correlates a visitor's checkout events to a POS transaction strictly if a transaction occurred within a 5-minute window following their presence. Resolves transaction-buyer mapping without customer identity data."),
            ("Intelligent Staff Filter", "Excludes retail staff from customer conversion metrics using a color-histogram uniform classifier in the main floor tracking camera, tagging staff events with 'is_staff=true'."),
            ("Idempotency Safeguard", "Enforces event deduplication on API ingest using SQLite's native 'INSERT OR IGNORE' primary key index, ensuring safe, duplicate-free metrics updates on network retries."),
            ("Self-Contained Edge Build", "Designed using serverless SQLite database, eliminating manual setup and service dependency issues on edge devices, allowing one-click Docker deployments.")
        ]
        
        y_pos = 0.68
        for head, desc in tech_points:
            # Bullet marker
            ax.text(0.06, y_pos, "✔", fontsize=16, color='#39ff14')
            # Header
            ax.text(0.09, y_pos, head, fontsize=15, fontweight='bold', color='#ffffff')
            # Text
            ax.text(0.09, y_pos - 0.05, desc, fontsize=11, color='#8e8e93', wrap=True)
            y_pos -= 0.155
            
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 5: Production Readiness & UX
        # =========================================================================
        fig, ax = setup_slide("PRODUCTION READINESS & LIVE DASHBOARD")
        
        # Left column (UI features)
        ax.text(0.06, 0.70, "Live Glassmorphic Dashboard", fontsize=18, fontweight='semibold', color='#bb66ff')
        ui_features = [
            "100% viewport-contained single-page layout (no scrolling)",
            "Dynamic Real-Time zone heatmap overlays (frequency scale 0-100)",
            "Active Conversion Funnel tracking Entry -> Zone Visit -> Queue -> Purchase",
            "Live operational logs and active alerts for queues and dead zones"
        ]
        y_pos = 0.60
        for f in ui_features:
            ax.text(0.06, y_pos, "•", color='#ff4df0', fontsize=18)
            ax.text(0.08, y_pos, f, color='#ffffff', fontsize=12)
            y_pos -= 0.08

        # Right column (Production readiness)
        ax.text(0.52, 0.70, "Production Readiness Metrics", fontsize=18, fontweight='semibold', color='#ff4df0')
        prod_features = [
            "Zero Setup Containerization (runs via 'docker compose up')",
            "Structured JSON logging tracing trace_id, store_id, latency, etc.",
            "Graceful DB degradation mapping failures to HTTP 503 response",
            "High code coverage (>70% statement coverage in test suite)"
        ]
        y_pos = 0.60
        for f in prod_features:
            ax.text(0.52, y_pos, "•", color='#bb66ff', fontsize=18)
            ax.text(0.54, y_pos, f, color='#ffffff', fontsize=12)
            y_pos -= 0.08
            
        # Thank you note at bottom
        ax.text(0.5, 0.15, "Thank you! Live Demo at: purplle-store-intelligence-xxm1.onrender.com", 
                fontsize=13, fontweight='bold', color='#39ff14', ha='center', transform=ax.transAxes)
            
        pdf.savefig(fig)
        plt.close(fig)
        
    print(f"Presentation created successfully at {pdf_path}!")

if __name__ == "__main__":
    create_presentation()
