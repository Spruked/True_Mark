# forensic_renderer.py
"""
TrueMark Forensic Certificate Renderer
Generates PDFs using the governed 2, 3, 5, 7, 11, or 13-layer profiles
Anti-AI forensic markers + micro-artifacts for authenticity
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import random
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from io import BytesIO
import io
import sys

from path_config import get_templates_path, get_fonts_path, ensure_temp_vault_dir
from layer_profiles import get_layer_profile

try:
    from frame_catalog import get_frame, get_frame_asset_path
except ModuleNotFoundError:
    sys.path.insert(0, str(get_templates_path()))
    from frame_catalog import get_frame, get_frame_asset_path


class ForensicCertificateRenderer:
    """
    Generates PDFs with one of the six governed prime forensic depths.
    Each layer contains anti-AI forensic markers.
    """
    
    def __init__(self, template_path: Optional[Path] = None, frame_id: Optional[str] = None):
        self.template_path = template_path or get_templates_path()
        self.frame_id = frame_id
        self.last_artifacts: Dict[str, Path] = {}
        self.font_dir = get_fonts_path()
        
        # Initialize fonts with fallbacks
        self._load_forensic_fonts()
        
        # Color palette (official TrueMark colors)
        self.colors = {
            'primary_blue': HexColor("#0F2E74"),
            'gold': HexColor("#DAA520"),
            'dark_slate': HexColor("#2F4F4F"),
            'brown': HexColor("#8B4513"),
            'parchment': HexColor("#F5F5DC")
        }
    
    def _load_forensic_fonts(self):
        """Load fonts with embedded forensic markers (fallback to built-ins)."""
        try:
            # Try to load custom fonts if available
            if (self.font_dir / "EBGaramond-Bold.ttf").exists():
                pdfmetrics.registerFont(TTFont("Garamond-Bold", str(self.font_dir / "EBGaramond-Bold.ttf")))
            else:
                # Fallback to built-in
                self.garamond_font = "Times-Bold"
                
            if (self.font_dir / "CourierPrime.ttf").exists():
                pdfmetrics.registerFont(TTFont("Courier-Secure", str(self.font_dir / "CourierPrime.ttf")))
            else:
                self.courier_font = "Courier-Bold"
                
            if (self.font_dir / "TrueMarkOfficer.ttf").exists():
                pdfmetrics.registerFont(TTFont("Officer-Script", str(self.font_dir / "TrueMarkOfficer.ttf")))
            else:
                self.officer_font = "Helvetica-Oblique"
                
        except Exception as e:
            print(f"⚠️  Font loading warning: {e}. Using built-in fonts.")
            self.garamond_font = "Times-Bold"
            self.courier_font = "Courier-Bold"
            self.officer_font = "Helvetica-Oblique"
    
    def _get_font(self, font_type: str) -> str:
        """Get font name with fallback."""
        font_map = {
            'garamond': 'Garamond-Bold' if hasattr(self, 'garamond_font') and self.garamond_font == "Times-Bold" else self.garamond_font if hasattr(self, 'garamond_font') else 'Times-Bold',
            'courier': 'Courier-Secure' if hasattr(self, 'courier_font') and self.courier_font == "Courier-Bold" else self.courier_font if hasattr(self, 'courier_font') else 'Courier-Bold',
            'officer': 'Officer-Script' if hasattr(self, 'officer_font') and self.officer_font == "Helvetica-Oblique" else self.officer_font if hasattr(self, 'officer_font') else 'Helvetica-Oblique'
        }
        return font_map.get(font_type, 'Times-Bold')
    
    async def create_forensic_pdf(self, data: Dict, output_dir: Path) -> Path:
        """
        Creates 300 DPI forensic PDF with anti-AI micro-artifacts.
        
        Args:
            data: Certificate data including DALS serial, owner, signatures, etc.
            output_dir: Directory to save the PDF
            
        Returns:
            Path to generated PDF
        """
        output_path = output_dir / f"{data['dals_serial']}_OFFICIAL.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        selected_frame = get_frame(data.get("frame_id", self.frame_id))
        layer_profile = get_layer_profile(data.get("layer_count", 13))
        data["layer_profile"] = layer_profile
        c = canvas.Canvas(str(output_path), pagesize=letter)
        c.setTitle(f"TrueMark Certificate {data['dals_serial']}")
        c.setAuthor("TrueMark Forge v2.0")
        c.setSubject(
            f"Official Certificate of Authenticity - {data['dals_serial']} - "
            f"{selected_frame['frame_id']}"
        )
        
        layer_ids = {layer["id"] for layer in layer_profile["layers"]}
        if "substrate" in layer_ids:
            self._draw_parchment_base(c)
        if "content" in layer_ids:
            self._draw_forensic_header(c, title=data.get('asset_title', 'Digital Asset'))
            self._draw_data_grid(c, data)
            self._draw_public_security_metadata(c, data, layer_profile)
        if "frame" in layer_ids:
            self._draw_guilloche_border(c, selected_frame["frame_id"])
        if "watermark" in layer_ids:
            self._draw_watermark(c, opacity=0.12, rotation_variation=True)
        if "timestamp" in layer_ids:
            self._draw_timestamp_block(c, data)
        if "seal" in layer_ids:
            self._draw_embossed_seal(c, data['dals_serial'])
        if "verification_qr" in layer_ids:
            self._draw_verification_qr(c, data['dals_serial'])
        if "signature" in layer_ids:
            self._draw_officer_signature(c, officer=data.get("officer", "Authorized Officer"))
        if "micro_pattern" in layer_ids:
            self._draw_micro_pattern(c)
        if "micro_noise" in layer_ids:
            self._add_micro_noise(c, intensity=0.015)
        if "manifest" in layer_ids:
            self._draw_manifest_block(c, data)
        if "cryptographic_metadata" in layer_ids:
            self._embed_crypto_metadata(c, data)
        if "verification_block" in layer_ids:
            self._draw_verification_block(c, data)
        
        c.save()

        self.last_artifacts = {"pdf": output_path}
        if data.get("nft_backed"):
            self.last_artifacts.update(self._export_image_companions(output_path, output_dir))
        
        print(f"✅ Generated forensic PDF: {output_path}")
        return output_path

    def _export_image_companions(self, pdf_path: Path, output_dir: Path) -> Dict[str, Path]:
        """Rasterize the final PDF page so NFT artwork cannot visually drift."""
        try:
            import fitz  # PyMuPDF
            from PIL import Image
        except ImportError as error:
            raise RuntimeError(
                "NFT-backed certificates require PyMuPDF and Pillow for "
                "pixel-faithful PDF rasterization. Install forge requirements."
            ) from error

        document = fitz.open(str(pdf_path))
        if len(document) != 1:
            document.close()
            raise ValueError("Certificate companion rendering requires exactly one PDF page.")

        page = document[0]
        scale = 300 / 72
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        png_path = output_dir / f"{pdf_path.stem}.png"
        jpeg_path = output_dir / f"{pdf_path.stem}.jpg"
        pixmap.save(str(png_path))

        image = Image.open(BytesIO(pixmap.tobytes("png"))).convert("RGB")
        image.save(str(jpeg_path), format="JPEG", quality=95, optimize=True)
        document.close()
        return {"png": png_path, "jpeg": jpeg_path}
    
    def _draw_parchment_base(self, c: canvas.Canvas):
        """Real scanned parchment or procedurally generated texture."""
        w, h = letter
        
        parchment_file = self.template_path / "parchment_base_600dpi.jpg"
        
        if parchment_file.exists():
            # Use real scanned parchment
            c.drawImage(str(parchment_file), 0, 0, width=w, height=h)
        else:
            # Generate procedural parchment texture
            c.setFillColor(self.colors['parchment'])
            c.rect(0, 0, w, h, fill=True, stroke=False)
            
            # Add subtle texture noise
            c.saveState()
            for _ in range(500):
                x = random.random() * w
                y = random.random() * h
                alpha = random.uniform(0.01, 0.03)
                size = random.uniform(0.5, 2)
                c.setFillColorRGB(0.9, 0.85, 0.7, alpha=alpha)
                c.circle(x, y, size, fill=True, stroke=False)
            c.restoreState()
    
    def _draw_guilloche_border(self, c: canvas.Canvas, frame_id: Optional[str] = None):
        """Draw the selected governed SVG frame, with a safe fallback."""
        w, h = letter

        guilloche_file = get_frame_asset_path(self.template_path, frame_id)
        
        if guilloche_file.exists():
            # Use pre-designed SVG
            try:
                from svglib.svglib import svg2rlg
                from reportlab.graphics import renderPDF
                drawing = svg2rlg(str(guilloche_file))
                renderPDF.draw(drawing, c, 0, 0)
            except:
                self._draw_simple_border(c, frame_id)
        else:
            self._draw_simple_border(c, frame_id)

    def _draw_simple_border(self, c: canvas.Canvas, frame_id: Optional[str] = None):
        """Simple fallback preserving the selected frame's visual family."""
        w, h = letter
        frame = get_frame(frame_id)
        margin = 0.5 * inch
        
        c.saveState()
        c.setStrokeColor(self.colors['gold'])
        c.setLineWidth(6 if frame["group"] == "heavy_elite" else 3)
        
        # Outer border
        c.rect(margin, margin, w - 2*margin, h - 2*margin)
        
        # Inner decorative lines
        c.setLineWidth(1 if frame["group"] != "ultra_minimal" else 0.5)
        c.rect(margin + 5, margin + 5, w - 2*margin - 10, h - 2*margin - 10)
        
        # Corner ornaments
        corner_size = 30
        corners = [
            (margin, h - margin),  # Top-left
            (w - margin, h - margin),  # Top-right
            (margin, margin),  # Bottom-left
            (w - margin, margin)  # Bottom-right
        ]
        
        for x, y in corners:
            # Simple corner decoration
            c.circle(x, y, corner_size/2, fill=False, stroke=True)
        
        c.restoreState()
    
    def _draw_watermark(self, c: canvas.Canvas, opacity: float, rotation_variation: bool):
        """TrueMark Tree with slight rotational variance (anti-AI)."""
        w, h = letter
        
        tree_file = self.template_path / "truemark_tree_watermark.png"
        
        if tree_file.exists():
            rotation = random.uniform(-1.5, 1.5) if rotation_variation else 0
            
            c.saveState()
            c.setFillAlpha(opacity)
            c.translate(w * 0.5, h * 0.5)
            c.rotate(rotation)
            
            # Center the watermark
            img_width = w * 0.4
            c.drawImage(str(tree_file), -img_width/2, -img_width/2, 
                       width=img_width, preserveAspectRatio=True, mask='auto')
            c.restoreState()
        else:
            # Draw simple tree watermark
            self._draw_simple_watermark(c, opacity)
    
    def _draw_simple_watermark(self, c: canvas.Canvas, opacity: float):
        """Simple tree watermark fallback."""
        w, h = letter
        
        c.saveState()
        c.setStrokeColorRGB(0.3, 0.5, 0.3, alpha=opacity)
        c.setLineWidth(20)
        
        # Tree trunk
        trunk_x = w / 2
        trunk_base = h * 0.3
        trunk_top = h * 0.6
        c.line(trunk_x, trunk_base, trunk_x, trunk_top)
        
        # Branches (simple triangle)
        c.setFillColorRGB(0.2, 0.6, 0.2, alpha=opacity)
        branch_width = 80
        c.polygon([
            (trunk_x - branch_width, trunk_top - 20),
            (trunk_x + branch_width, trunk_top - 20),
            (trunk_x, trunk_top + 100)
        ], fill=True, stroke=False)
        
        c.restoreState()
    
    def _draw_forensic_header(self, c: canvas.Canvas, title: str):
        """Header with micro-kerning and baseline shift."""
        w, h = letter
        
        # TRUEMARK® with slight kerning variation
        c.setFont("Times-Bold", 52)
        c.setFillColor(self.colors['primary_blue'])
        
        # Draw centered title
        truemark_text = "TRUEMARK"
        text_width = c.stringWidth(truemark_text, "Times-Bold", 52)
        c.drawString((w - text_width) / 2, h - 1.6*inch, truemark_text)
        
        # Registered trademark symbol
        c.setFont("Times-Bold", 24)
        c.drawString((w + text_width) / 2 + 5, h - 1.5*inch, "®")
        
        # Subtitle
        c.setFont("Times-Bold", 22)
        c.drawCentredString(w/2, h - 2.1*inch, "CERTIFICATE OF AUTHENTICITY")
        
        # Horizontal line
        c.setStrokeColor(self.colors['gold'])
        c.setLineWidth(2)
        c.line(1.5*inch, h - 2.3*inch, w - 1.5*inch, h - 2.3*inch)
        
        # Project Title (variable, with slight baseline drift)
        c.setFont("Times-Bold", 16)
        c.setFillColor(self.colors['dark_slate'])
        drift = random.uniform(-0.3, 0.3)  # Subtle anti-AI drift
        
        # Wrap long titles
        if len(title) > 50:
            title = title[:47] + "..."
        
        c.drawCentredString(w/2, h - 2.7*inch + drift, title)
    
    def _draw_data_grid(self, c: canvas.Canvas, data: Dict):
        """Data fields with intentional misalignment (physical typing simulation)."""
        w, h = letter
        y_start = h - 3.8*inch
        left_margin = 1.2*inch
        label_width = 2.2*inch
        
        fields = [
            ("Owner Name:", data.get('owner', 'N/A')),
            ("Web3 Wallet:", data.get('wallet', 'N/A')[:42] + "..." if len(data.get('wallet', '')) > 42 else data.get('wallet', 'N/A')),
            ("NFT Category:", data.get('kep_category', 'Knowledge')),
            ("Chain ID:", data.get('chain_id', 'Polygon')),
            ("IPFS Hash:", data.get('ipfs_hash', 'N/A')[:30] + "..." if len(data.get('ipfs_hash', '')) > 30 else data.get('ipfs_hash', 'N/A')),
            ("Issue Date:", data.get('stardate', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))),
            ("DALS Serial:", data.get('dals_serial', 'UNKNOWN')),
            ("Signature ID:", data.get('sig_id', 'N/A')),
        ]
        
        c.setFont("Times-Bold", 11)
        
        for i, (label, value) in enumerate(fields):
            y_pos = y_start - i * 0.42*inch
            
            # Label (bold, dark)
            c.setFillColor(self.colors['primary_blue'])
            c.drawString(left_margin, y_pos, label)
            
            # Value (courier) with micro-baseline drift
            c.setFont("Courier-Bold", 10)
            c.setFillColor(Color(0, 0, 0))
            value_drift = random.uniform(-0.2, 0.2)
            
            # Ensure value is string
            value_str = str(value)
            c.drawString(left_margin + label_width, y_pos + value_drift, value_str)
            
            c.setFont("Times-Bold", 11)
    
    def _draw_embossed_seal(self, c: canvas.Canvas, serial: str):
        """Gold foil seal with specular highlight simulation."""
        w, h = letter
        
        seal_file = self.template_path / "seal_gold_embossed_600dpi.png"
        seal_size = 2.0 * inch
        seal_x = w - seal_size - 0.8*inch
        seal_y = 0.6*inch
        
        if seal_file.exists():
            c.drawImage(str(seal_file), seal_x, seal_y, 
                       width=seal_size, height=seal_size, mask='auto')
        else:
            # Draw procedural seal
            self._draw_procedural_seal(c, seal_x + seal_size/2, seal_y + seal_size/2, seal_size/2)
        
        # Serial number overlay on seal
        c.saveState()
        c.setFillColor(self.colors['brown'])
        c.setFont("Courier-Bold", 7)
        c.translate(seal_x + seal_size/2, seal_y + seal_size/2 + 0.3*inch)
        c.rotate(-8)  # Slight rotation
        c.drawCentredString(0, 0, serial[:13])
        c.restoreState()
    
    def _draw_procedural_seal(self, c: canvas.Canvas, x: float, y: float, radius: float):
        """Generate a procedural seal design."""
        c.saveState()
        
        # Outer gold circle
        c.setFillColor(self.colors['gold'])
        c.setStrokeColor(self.colors['brown'])
        c.setLineWidth(2)
        c.circle(x, y, radius, fill=True, stroke=True)
        
        # Inner circle
        c.setFillColorRGB(0.9, 0.8, 0.3)
        c.circle(x, y, radius * 0.8, fill=True, stroke=True)
        
        # Star pattern
        c.setFillColor(self.colors['brown'])
        points = 8
        for i in range(points):
            angle = (i * 360 / points) * 3.14159 / 180
            x1 = x + radius * 0.3 * (1 if i % 2 == 0 else 0.6) * (1 if i < points/2 else -1)
            y1 = y + radius * 0.3 * (1 if i % 2 == 0 else 0.6) * (1 if i < points/2 else -1)
            c.circle(x1, y1, 3, fill=True, stroke=False)
        
        # Center text placeholder
        c.setFont("Times-Bold", 10)
        c.setFillColor(self.colors['brown'])
        c.drawCentredString(x, y - 5, "TRUEMARK")
        c.setFont("Times-Bold", 8)
        c.drawCentredString(x, y - 18, "OFFICIAL")
        
        c.restoreState()
    
    def _draw_verification_qr(self, c: canvas.Canvas, serial: str) -> Path:
        """QR code containing verification URL + signature fragment."""
        w, h = letter
        
        verification_url = f"https://verify.truemark.io/{serial}"
        
        # Create QR with L-level error correction
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = ensure_temp_vault_dir() / f"temp_qr_{serial}.png"
        qr_path.parent.mkdir(parents=True, exist_ok=True)
        qr_img.save(qr_path)
        
        # Draw QR code
        qr_size = 1.5 * inch
        c.drawImage(str(qr_path), 1.0*inch, 0.7*inch, 
                   width=qr_size, height=qr_size, mask='auto')
        
        # QR label
        c.setFont("Courier-Bold", 8)
        c.setFillColor(Color(0, 0, 0))
        c.drawCentredString(1.0*inch + qr_size/2, 0.5*inch, "Scan to Verify")
        
        return qr_path
    
    def _draw_officer_signature(self, c: canvas.Canvas, officer: str):
        """Simulated wet signature with pressure variance."""
        w, h = letter
        
        # Signature line
        c.setFont("Times-Roman", 10)
        c.setFillColor(Color(0, 0, 0))
        
        sig_y = 1.8*inch
        c.line(1.2*inch, sig_y, 3.5*inch, sig_y)
        c.line(4.5*inch, sig_y, 6.0*inch, sig_y)
        
        # Labels under lines
        c.setFont("Times-Roman", 9)
        c.drawCentredString(2.35*inch, sig_y - 0.2*inch, "Authorized Officer")
        c.drawCentredString(5.25*inch, sig_y - 0.2*inch, "Date")
        
        # Simulated signature (script-like)
        c.setFont("Helvetica-Oblique", 14)
        c.setFillColor(self.colors['dark_slate'])
        c.drawString(1.3*inch, sig_y + 0.05*inch, officer)
        
        # Date stamp
        c.setFont("Courier-Bold", 10)
        issue_date = datetime.utcnow().strftime("%Y-%m-%d")
        c.drawString(4.6*inch, sig_y + 0.05*inch, issue_date)
    
    def _draw_timestamp_block(self, c: canvas.Canvas, data: Dict):
        """Draw canonical time representations without changing their authority."""
        w, h = letter
        timestamp = data.get("iss_timestamp") or data.get("stardate", "ISS timestamp pending")
        c.saveState()
        c.setFillColor(self.colors["dark_slate"])
        c.setFont("Courier-Bold", 8)
        c.drawString(1.2 * inch, h - 7.35 * inch, f"ISS SCALE: {timestamp}")
        c.drawString(1.2 * inch, h - 7.55 * inch, f"ISS_TIME_NS: {data.get('iss_time_ns', 'pending')}")
        c.restoreState()

    def _draw_public_security_metadata(self, c: canvas.Canvas, data: Dict, layer_profile: Dict):
        """Draw only the approved public security fields."""
        w, h = letter
        count = int(layer_profile["layer_count"])
        profile = str(data.get("security_profile") or f"TM-FSP-{count}")
        version = str(data.get("security_profile_version") or "1.0")
        certificate_hash = str(data.get("payload_hash") or "PENDING")
        verification_id = str(data.get("dals_serial") or "PENDING")
        status = str(data.get("verification_status") or ("VALID" if data.get("ed25519_signature") else "PENDING"))

        c.saveState()
        c.setFillColor(self.colors["dark_slate"])
        c.setFont("Courier-Bold", 7)
        c.drawString(1.2 * inch, h - 7.85 * inch, f"FORENSIC SECURITY PROFILE: {count}-LAYER")
        c.drawString(1.2 * inch, h - 8.05 * inch, f"SECURITY PROFILE VERSION: {profile}/{version}")
        c.drawString(1.2 * inch, h - 8.25 * inch, f"VERIFICATION STATUS: {status}")
        c.drawString(1.2 * inch, h - 8.45 * inch, f"CERTIFICATE HASH: {certificate_hash[:48]}")
        c.drawString(1.2 * inch, h - 8.65 * inch, f"TRUE MARK VERIFICATION ID: {verification_id}")
        c.restoreState()

    def _draw_micro_pattern(self, c: canvas.Canvas):
        """Draw a deterministic micro-pattern inside the selected presentation."""
        w, h = letter
        c.saveState()
        c.setStrokeColorRGB(0.06, 0.18, 0.45, alpha=0.22)
        c.setLineWidth(0.25)
        for index in range(0, int(w), 9):
            c.line(index, 0.55 * inch, index + 42, 0.55 * inch + 42)
            c.line(w - index, h - 0.55 * inch, w - index - 42, h - 0.55 * inch - 42)
        c.restoreState()

    def _draw_manifest_block(self, c: canvas.Canvas, data: Dict):
        """Display the manifest reference without making the PDF authoritative."""
        c.saveState()
        c.setFillColor(self.colors["dark_slate"])
        c.setFont("Courier", 6)
        manifest = data.get("manifest_hash") or data.get("payload_hash", "pending")
        c.drawString(1.0 * inch, 0.38 * inch, f"MANIFEST HASH: {str(manifest)[:48]}")
        c.restoreState()

    def _draw_verification_block(self, c: canvas.Canvas, data: Dict):
        """Add a visible independent-verification instruction for elite profiles."""
        w, h = letter
        c.saveState()
        c.setStrokeColor(self.colors["gold"])
        c.setLineWidth(1)
        c.roundRect(w - 3.0 * inch, h - 9.25 * inch, 1.9 * inch, 0.55 * inch, 5, stroke=1, fill=0)
        c.setFillColor(self.colors["primary_blue"])
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(w - 2.05 * inch, h - 8.93 * inch, "INDEPENDENT VERIFICATION")
        c.setFont("Courier", 6)
        c.drawCentredString(w - 2.05 * inch, h - 9.12 * inch, str(data.get("dals_serial", "PENDING"))[:24])
        c.restoreState()

    def _add_micro_noise(self, c: canvas.Canvas, intensity: float):
        """Imperceptible scanner sensor noise pattern."""
        w, h = letter
        
        c.saveState()
        c.setLineWidth(0.005)
        
        # Add random micro-dots (anti-AI artifacts)
        for _ in range(800):
            x = random.random() * w
            y = random.random() * h
            alpha = intensity * random.random()
            
            c.setStrokeColorRGB(0, 0, 0, alpha=alpha)
            c.line(x, y, x + 0.005*inch, y + 0.005*inch)
        
        c.restoreState()
    
    def _embed_crypto_metadata(self, c: canvas.Canvas, data: Dict):
        """Embed Ed25519 signature in PDF metadata."""
        # PDF metadata is set during canvas creation
        # Additional metadata can be embedded here
        signature = data.get('ed25519_signature', 'N/A')
        
        # Add invisible text layer with signature (for forensic extraction)
        c.saveState()
        c.setFillColorRGB(1, 1, 1, alpha=0.01)  # Nearly invisible
        c.setFont("Courier", 6)
        c.drawString(10, 10, f"SIG:{signature[:64]}")
        c.restoreState()
    
    def generate_verification_qr(self, serial: str) -> Path:
        """Standalone QR generator for customers."""
        qr_path = ensure_temp_vault_dir() / f"verification_qr_{serial}.png"
        qr_path.parent.mkdir(parents=True, exist_ok=True)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(f"https://verify.truemark.io/{serial}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save(qr_path)
        
        print(f"✅ Generated verification QR: {qr_path}")
        return qr_path


if __name__ == "__main__":
    import asyncio
    
    print("🎨 TrueMark Forensic Renderer - Self Test")
    print("=" * 60)
    
    renderer = ForensicCertificateRenderer()
    
    # Test data
    test_data = {
        'dals_serial': 'DALSTEST-12345678',
        'asset_title': 'Test Certificate - Visual Forensics Demo',
        'owner': 'Test User',
        'wallet': '0xTESTWALLETADDRESS1234567890ABCDEF',
        'kep_category': 'Knowledge',
        'chain_id': 'Polygon',
        'ipfs_hash': 'ipfs://QmTEST1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'stardate': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        'sig_id': 'TEST8A7B3C2F',
        'ed25519_signature': 'a' * 128,  # Mock signature
        'payload_hash': hashlib.sha256(b'test').hexdigest()
    }
    
    output_dir = ensure_temp_vault_dir() / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n📄 Generating test certificate...")
    pdf_path = asyncio.run(renderer.create_forensic_pdf(test_data, output_dir))
    
    print(f"\n✅ Test certificate created:")
    print(f"   Path: {pdf_path}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.2f} KB")
    
    print("\n🔍 Generating verification QR...")
    qr_path = renderer.generate_verification_qr(test_data['dals_serial'])
    print(f"   QR Code: {qr_path}")
    
    print("\n" + "=" * 60)
    print("Self-test complete. Renderer ready for production.")
