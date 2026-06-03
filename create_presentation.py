import os
import textwrap
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
            fig.patch.set_facecolor('#0f0f13') # Premium deep slate black bg
            ax.set_facecolor('#0f0f13')
            
            # Lock coordinates to absolute 0.0 -> 1.0 range
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            
            # Hide spines and axes ticks
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            
            # Accent bottom bar
            ax.plot([0.00, 1.00], [0.01, 0.01], color='#9b51e0', transform=ax.transAxes, lw=4, alpha=0.9)
            
            # Decorative outer border
            border = patches.Rectangle((0.02, 0.02), 0.96, 0.96, linewidth=1, edgecolor='#3f3f46', facecolor='none', alpha=0.3, transform=ax.transAxes)
            ax.add_patch(border)
            
            # Slide header title
            if title_text:
                ax.text(0.08, 0.86, title_text, fontsize=24, fontweight='bold', color='#ffffff', family='sans-serif', transform=ax.transAxes)
                # Underline
                ax.plot([0.08, 0.92], [0.81, 0.81], color='#e051b8', transform=ax.transAxes, lw=1.5, alpha=0.7)
                
            return fig, ax

        # =========================================================================
        # SLIDE 1: Title Slide (Sleek and minimalist)
        # =========================================================================
        fig, ax = setup_slide(None)
        
        # Background gradient circle glow
        circle = patches.Circle((0.5, 0.5), 0.35, color='#9b51e0', alpha=0.05, transform=ax.transAxes)
        ax.add_patch(circle)
        
        # Main Title
        ax.text(0.5, 0.58, "APEX RETAIL AI", fontsize=44, fontweight='bold', color='#ffffff', 
                ha='center', va='center', family='sans-serif', transform=ax.transAxes)
        ax.text(0.5, 0.48, "Store Intelligence & Customer Conversion Platform", fontsize=18, color='#a0a0ab', 
                ha='center', va='center', family='sans-serif', transform=ax.transAxes)
        
        # Horizontal accent bar
        ax.plot([0.42, 0.58], [0.42, 0.42], color='#e051b8', transform=ax.transAxes, lw=2, alpha=0.8)
        
        # Metadata
        ax.text(0.5, 0.28, "Hackathon Submission Presentation", fontsize=13, color='#71717a', 
                ha='center', va='center', family='sans-serif', transform=ax.transAxes)
        ax.text(0.5, 0.22, "Developed by Anjali Tiwari", fontsize=12, color='#bb66ff', 
                ha='center', va='center', family='sans-serif', transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 2: The Business Problem (Clean, well-spaced list layout)
        # =========================================================================
        fig, ax = setup_slide("THE OFFLINE RETAIL BLIND SPOT")
        
        ax.text(0.08, 0.72, "Why Physical Retail Needs Online-Style Analytics:", fontsize=15, color='#a0a0ab', family='sans-serif', transform=ax.transAxes)
        
        points = [
            ("Offline Journey Blind Spot", "Physical stores operate with zero path visibility. Customer browsing paths, zone dwell times, and shelf engagements remain completely untracked."),
            ("Billing Queue Abandonment", "No analytical way to measure queue drop-offs. High abandonment rates at checkout go undetected due to a lack of queue monitoring."),
            ("Disconnection from POS Data", "Foot traffic is rarely correlated to transaction records. True checkout conversion rates cannot be calculated without time-window correlation."),
            ("Heavy Infrastructure Overhead", "Traditional camera analytics require complex database servers and dedicated GPU hardware, blocking fast, edge-based deployment.")
        ]
        
        y_pos = 0.60
        for head, desc in points:
            # Bullet header
            ax.text(0.08, y_pos, f"■  {head.upper()}", fontsize=13, fontweight='bold', color='#9b51e0', transform=ax.transAxes, family='sans-serif')
            # Wrapped description text directly below the header
            wrapped = "\n".join(textwrap.wrap(desc, width=95))
            ax.text(0.10, y_pos - 0.05, wrapped, fontsize=10.5, color='#e4e4e7', transform=ax.transAxes, family='sans-serif', linespacing=1.4)
            y_pos -= 0.14
            
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 3: System Architecture (Neat, clean boxes and labels)
        # =========================================================================
        fig, ax = setup_slide("END-TO-END SYSTEM ARCHITECTURE")
        
        stages = [
            ("CCTV Video Clips", "5 Stores, 3 Angles\n20 Mins Per Clip", "Entry, floor, and cash desk inputs"),
            ("Detection Layer", "YOLOv8 + Centroid\nTracking", "Excludes staff, flags re-entries"),
            ("Intelligence API", "FastAPI + SQLite\nAnalytics Engine", "Idempotent ingest & SQL calculations"),
            ("Live Dashboard", "Glassmorphic Web\nInterface", "Interactive heatmap & funnel charts")
        ]
        
        x_pos = 0.08
        for i, (title, header_desc, detail) in enumerate(stages):
            # Outer card container
            box = patches.FancyBboxPatch((x_pos, 0.36), 0.17, 0.30, boxstyle="round,pad=0.01", 
                                         linewidth=1, edgecolor='#3f3f46', facecolor='#18181b', alpha=0.9, transform=ax.transAxes)
            ax.add_patch(box)
            
            # Card accent top bar
            ax.plot([x_pos + 0.01, x_pos + 0.16], [0.64, 0.64], color='#9b51e0', transform=ax.transAxes, lw=2)
            
            # Title
            ax.text(x_pos + 0.085, 0.59, title, fontsize=12, fontweight='bold', color='#ffffff', ha='center', family='sans-serif', transform=ax.transAxes)
            # Header Desc
            ax.text(x_pos + 0.085, 0.50, header_desc, fontsize=10, color='#e4e4e7', ha='center', va='center', family='sans-serif', linespacing=1.3, transform=ax.transAxes)
            # Footer Detail
            ax.text(x_pos + 0.085, 0.40, detail, fontsize=8.5, color='#71717a', ha='center', va='center', family='sans-serif', transform=ax.transAxes)
            
            # Connecting Arrow (draw clean text-based arrow)
            if i < 3:
                ax.text(x_pos + 0.19, 0.50, "→", fontsize=20, color='#e051b8', ha='center', va='center', transform=ax.transAxes)
                
            x_pos += 0.22
            
        # Tech summary bar at bottom
        ax.text(0.08, 0.24, "TECHNOLOGY STACK:", fontsize=12, fontweight='bold', color='#9b51e0', family='sans-serif', transform=ax.transAxes)
        ax.text(0.24, 0.24, "Python 3.11  •  Ultralytics YOLOv8  •  FastAPI  •  SQLite3  •  HTML5/CSS3", fontsize=12, color='#ffffff', family='sans-serif', transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 4: Key Technical Solutions (Clean checkmarks, structured spacing)
        # =========================================================================
        fig, ax = setup_slide("KEY TECHNICAL SOLUTIONS")
        
        tech_points = [
            ("Time-Window Conversion Correlation", "Correlates a visitor's checkout events to a POS transaction strictly if a transaction occurred within a 5-minute window following their presence. Resolves transaction-buyer mapping without customer identity data."),
            ("Staff Exclusion Filter", "Excludes retail staff from customer conversion metrics using a color-histogram uniform classifier in the main floor tracking camera, tagging staff events with 'is_staff=true'."),
            ("Idempotent Ingestion Safeguard", "Enforces event deduplication on API ingest using SQLite's native 'INSERT OR IGNORE' primary key index, ensuring safe, duplicate-free metrics updates on network retries."),
            ("Self-Contained Edge Build", "Designed using serverless SQLite database, eliminating manual setup and service dependency issues on edge devices, allowing one-click Docker deployments.")
        ]
        
        y_pos = 0.68
        for head, desc in tech_points:
            # Checkmark
            ax.text(0.08, y_pos, "✔", fontsize=14, color='#27ae60', fontweight='bold', transform=ax.transAxes)
            # Header
            ax.text(0.11, y_pos, head, fontsize=13.5, fontweight='bold', color='#ffffff', transform=ax.transAxes, family='sans-serif')
            # Wrapped description text
            wrapped = "\n".join(textwrap.wrap(desc, width=95))
            ax.text(0.11, y_pos - 0.04, wrapped, fontsize=10.5, color='#a0a0ab', transform=ax.transAxes, family='sans-serif', linespacing=1.3)
            y_pos -= 0.155
            
        pdf.savefig(fig)
        plt.close(fig)

        # =========================================================================
        # SLIDE 5: Production Readiness & UX (Perfect columns alignment)
        # =========================================================================
        fig, ax = setup_slide("PRODUCTION READINESS & USER EXPERIENCE")
        
        # Left column (UI features)
        ax.text(0.08, 0.70, "LIVE DASHBOARD INTERFACE", fontsize=14, fontweight='bold', color='#9b51e0', family='sans-serif', transform=ax.transAxes)
        ui_features = [
            "100% viewport-contained single-page layout (no scrolling)",
            "Dynamic Real-Time zone heatmap overlays (frequency scale 0-100)",
            "Active Conversion Funnel tracking (Entry -> Visit -> Queue -> Purchase)",
            "Live operational logs and active alerts for queues and dead zones"
        ]
        y_pos = 0.61
        for f in ui_features:
            ax.text(0.08, y_pos, "•", color='#e051b8', fontsize=18, transform=ax.transAxes)
            wrapped = "\n".join(textwrap.wrap(f, width=42))
            ax.text(0.10, y_pos, wrapped, color='#ffffff', fontsize=11, transform=ax.transAxes, family='sans-serif', linespacing=1.3)
            y_pos -= 0.11

        # Right column (Production readiness)
        ax.text(0.52, 0.70, "PRODUCTION READINESS FEATURES", fontsize=14, fontweight='bold', color='#e051b8', family='sans-serif', transform=ax.transAxes)
        prod_features = [
            "Zero Setup Containerization (runs via 'docker compose up')",
            "Structured JSON logging tracing trace_id, store_id, and latency",
            "Graceful DB degradation mapping failures to HTTP 503 response",
            "High code coverage (>70% statement coverage in test suite)"
        ]
        y_pos = 0.61
        for f in prod_features:
            ax.text(0.52, y_pos, "•", color='#9b51e0', fontsize=18, transform=ax.transAxes)
            wrapped = "\n".join(textwrap.wrap(f, width=42))
            ax.text(0.54, y_pos, wrapped, color='#ffffff', fontsize=11, transform=ax.transAxes, family='sans-serif', linespacing=1.3)
            y_pos -= 0.11
            
        # Thank you note at bottom
        ax.text(0.5, 0.15, "Thank you!  Live Demo at: purplle-store-intelligence-xxm1.onrender.com", 
                fontsize=12, fontweight='bold', color='#27ae60', ha='center', transform=ax.transAxes, family='sans-serif')
            
        pdf.savefig(fig)
        plt.close(fig)
        
    print(f"Presentation created successfully at {pdf_path}!")

if __name__ == "__main__":
    create_presentation()
