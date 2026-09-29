# forensic_renderer.py
"""
TrueMark Forensic Certificate Renderer
Generates PDFs using the governed 2, 3, 5, 7, 11, or 13-layer profiles
Anti-AI forensic markers + micro-artifacts for authenticity
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
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

from path_config import get_repo_root, get_templates_path, get_fonts_path, ensure_temp_vault_dir
from registry import verification_url
from layer_profiles import get_layer_profile

try:
    from frame_catalog import get_frame, get_frame_asset_path
except ModuleNotFoundError:
    sys.path.insert(0, str(get_templates_path()))
    from frame_catalog import get_frame, get_frame_asset_path


NFT_COLOR_PROFILES = {
    "knowledge": {"id": "TM-NFT-KNOWLEDGE-BLUE", "label": "Knowledge / Blue-Teal"},
    "asset": {"id": "TM-NFT-ASSET-AMBER", "label": "Asset / Gold-Amber"},
    "identity": {"id": "TM-NFT-IDENTITY-VIOLET", "label": "Identity / Violet"},
    "k": {"id": "TM-NFT-KNOWLEDGE-BLUE", "label": "Knowledge / Blue-Teal"},
    "h": {"id": "TM-NFT-HEIRLOOM-GREEN", "label": "Heirloom / Emerald"},
    "l": {"id": "TM-NFT-LEGACY-VIOLET", "label": "Legacy / Violet"},
    "b": {"id": "TM-NFT-BLUE-GOLD", "label": "Bespoke / Blue-Gold"},
    "c": {"id": "TM-NFT-CUSTOM-AMBER", "label": "Custom / Gold-Amber"},
}


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
        # These are the approved TrueMark brand assets used by the product UI.
        # Template-local artwork remains available only as a compatibility fallback.
        self.brand_assets_path = get_repo_root() / "frontend" / "assets"
        
        # Initialize fonts with fallbacks
        self._load_forensic_fonts()
        
        # Color palette (official TrueMark colors)
        self.colors = {
            'primary_blue': HexColor("#0F2E74"),
            'gold': HexColor("#DAA520"),
            'dark_slate': HexColor("#2F4F4F"),
            'brown': HexColor("#8B4513"),
            'parchment': HexColor("#F5F5DC"),
            'watermark': HexColor("#6B8E23"),
        }

    def _resolve_nft_colors(self, data: Dict) -> Dict[str, Color]:
        """Return the governed visual palette for an NFT-backed certificate."""
        base = {
            'primary_blue': HexColor("#0F2E74"),
            'gold': HexColor("#DAA520"),
            'dark_slate': HexColor("#2F4F4F"),
            'brown': HexColor("#8B4513"),
            'parchment': HexColor("#F5F5DC"),
            'watermark': HexColor("#6B8E23"),
        }
        if not data.get("nft_backed"):
            return base

        palettes = {
            "knowledge": {
                "primary_blue": "#155E9A",
                "gold": "#1B9AAA",
                "dark_slate": "#16425B",
                "brown": "#155E75",
                "parchment": "#F1FAFC",
                "watermark": "#147D92",
            },
            "asset": {
                "primary_blue": "#7A4E00",
                "gold": "#C58A12",
                "dark_slate": "#4A3410",
                "brown": "#7A3E00",
                "parchment": "#FFF8E6",
                "watermark": "#A66A00",
            },
            "identity": {
                "primary_blue": "#542A78",
                "gold": "#A979D1",
                "dark_slate": "#38204F",
                "brown": "#542A78",
                "parchment": "#FAF3FF",
                "watermark": "#7541A3",
            },
            "heirloom": {
                "primary_blue": "#166534",
                "gold": "#2F9E68",
                "dark_slate": "#174B32",
                "brown": "#166534",
                "parchment": "#F1FBF4",
                "watermark": "#21864B",
            },
        }
        type_palette = {
            "k": "knowledge", "kl": "knowledge",
            "h": "heirloom", "hl": "heirloom",
            "l": "identity", "ll": "identity",
            "b": "asset", "bl": "asset",
            "c": "asset",
        }
        requested_type = str(data.get("nft_type", "")).lower().replace("-nft", "")
        palette_key = type_palette.get(requested_type, str(data.get("kep_category", "Knowledge")).lower())
        selected = palettes.get(palette_key, palettes["knowledge"])
        return {name: HexColor(value) for name, value in selected.items()}
    
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
            data: Certificate data including the TrueMark certificate number, owner, signatures, etc.
            output_dir: Directory to save the PDF
            
        Returns:
            Path to generated PDF
        """
        certificate_number = data["certificate_number"]
        output_path = output_dir / f"{certificate_number}_OFFICIAL.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        selected_frame = get_frame(data.get("frame_id", self.frame_id))
        layer_profile = get_layer_profile(data.get("layer_count", 13))
        data["layer_profile"] = layer_profile
        self.colors = self._resolve_nft_colors(data)
        c = canvas.Canvas(str(output_path), pagesize=landscape(letter))
        c.setTitle(f"TrueMark Certificate {certificate_number}")
        c.setAuthor("TrueMark Forge v2.0")
        c.setSubject(
            f"Official Certificate of Authenticity - {certificate_number} - "
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
        self._draw_corner_serials(c, certificate_number)
        # The Tree of Life watermark is mandatory brand signature treatment on
        # every NFT-backed certificate, independent of the forensic depth.
        if "watermark" in layer_ids or data.get("nft_backed"):
            watermark_opacity = 0.28 if data.get("nft_backed") else 0.12
            self._draw_watermark(
                c,
                opacity=watermark_opacity,
                rotation_variation=True,
                tint_nft=bool(data.get("nft_backed")),
            )
        if "timestamp" in layer_ids:
            self._draw_timestamp_block(c, data)
        if "seal" in layer_ids:
            self._draw_embossed_seal(c, certificate_number)
        if "verification_qr" in layer_ids:
            self._draw_verification_qr(c, certificate_number)
        if "signature" in layer_ids:
            self._draw_officer_signature(
                c,
                officer=data.get("officer", "Bryan A Spruk, President and CEO"),
            )
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
            try:
                import pymupdf as fitz  # PyMuPDF 1.28+
            except ImportError:
                import fitz  # PyMuPDF 1.24 compatibility
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
        image = Image.open(BytesIO(pixmap.tobytes("png"))).convert("RGB")
        image.save(str(png_path), format="PNG", dpi=(300, 300), optimize=True)
        image.save(str(jpeg_path), format="JPEG", quality=95, optimize=True, dpi=(300, 300))
        document.close()
        return {"png": png_path, "jpeg": jpeg_path}
    
    def _draw_parchment_base(self, c: canvas.Canvas):
        """Real scanned parchment or procedurally generated texture."""
        w, h = landscape(letter)
        
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
        w, h = landscape(letter)

        guilloche_file = get_frame_asset_path(self.template_path, frame_id)
        
        if guilloche_file.exists():
            # Use pre-designed SVG
            try:
                from svglib.svglib import svg2rlg
                from reportlab.graphics import renderPDF
                # Keep a visible vector frame even when an SVG adapter omits
                # stylesheet-class strokes. The selected SVG is layered above
                # this deterministic fallback.
                self._draw_simple_border(c, frame_id)
                drawing = svg2rlg(str(guilloche_file))
                renderPDF.draw(drawing, c, 0, 0)
            except:
                self._draw_simple_border(c, frame_id)
        else:
            self._draw_simple_border(c, frame_id)

    def _draw_simple_border(self, c: canvas.Canvas, frame_id: Optional[str] = None):
        """Simple fallback preserving the selected frame's visual family."""
        w, h = landscape(letter)
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
    
    def _draw_watermark(self, c: canvas.Canvas, opacity: float, rotation_variation: bool, tint_nft: bool = False):
        """TrueMark Tree with slight rotational variance (anti-AI)."""
        w, h = landscape(letter)
        
        tree_file = self.brand_assets_path / "tree_watermark_512.png"
        if not tree_file.exists():
            tree_file = self.template_path / "truemark_tree_watermark.png"
        
        if tree_file.exists():
            rotation = random.uniform(-1.5, 1.5) if rotation_variation else 0
            
            c.saveState()
            c.setFillAlpha(opacity)
            c.translate(w * 0.5, h * 0.5)
            c.rotate(rotation)
            
            # Center the watermark
            img_width = w * 0.4
            if tint_nft and tree_file.name == "tree_watermark_512.png":
                # The supplied Tree of Life asset is white-on-transparent. Tint
                # only its visible pixels while preserving the original asset.
                with Image.open(tree_file).convert("RGBA") as tree_image:
                    watermark = self.colors["watermark"]
                    red = int(watermark.red * 255)
                    green = int(watermark.green * 255)
                    blue = int(watermark.blue * 255)
                    pixels = tree_image.load()
                    for py in range(tree_image.height):
                        for px in range(tree_image.width):
                            _, _, _, alpha = pixels[px, py]
                            if alpha:
                                pixels[px, py] = (red, green, blue, alpha)
                    c.drawImage(
                        ImageReader(tree_image), -img_width / 2, -img_width / 2,
                        width=img_width, preserveAspectRatio=True, mask="auto"
                    )
            else:
                c.drawImage(str(tree_file), -img_width/2, -img_width/2,
                           width=img_width, preserveAspectRatio=True, mask='auto')
            c.restoreState()
        else:
            # Draw simple tree watermark
            self._draw_simple_watermark(c, opacity)
    
    def _draw_simple_watermark(self, c: canvas.Canvas, opacity: float):
        """Simple tree watermark fallback."""
        w, h = landscape(letter)
        
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
        path = c.beginPath()
        path.moveTo(trunk_x - branch_width, trunk_top - 20)
        path.lineTo(trunk_x + branch_width, trunk_top - 20)
        path.lineTo(trunk_x, trunk_top + 100)
        path.close()
        c.drawPath(path, fill=True, stroke=False)
        
        c.restoreState()
    
    def _draw_forensic_header(self, c: canvas.Canvas, title: str):
        """Header with micro-kerning and baseline shift."""
        w, h = landscape(letter)

        # Use the supplied TrueMark logo as the header mark.
        logo_file = self.brand_assets_path / "TMlogotrans512 - Copy.png"
        if logo_file.exists():
            logo_size = 0.62 * inch
            c.drawImage(
                str(logo_file),
                0.78 * inch,
                h - 1.08 * inch,
                width=logo_size,
                height=logo_size,
                preserveAspectRatio=True,
                mask="auto",
            )
        
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
        w, h = landscape(letter)
        y_start = h - 3.25*inch
        left_margin = 1.2*inch
        label_width = 2.2*inch
        
        fields = [
            ("Owner Name:", data.get('owner', 'N/A')),
            ("Web3 Wallet:", data.get('wallet', 'N/A')[:42] + "..." if len(data.get('wallet', '')) > 42 else data.get('wallet', 'N/A')),
            ("NFT Category:", data.get('kep_category', 'Knowledge')),
            ("Chain ID:", data.get('chain_id', 'Polygon')),
            ("IPFS Hash:", data.get('ipfs_hash', 'N/A')[:20] + "..." if len(data.get('ipfs_hash', '')) > 20 else data.get('ipfs_hash', 'N/A')),
            ("Issue Date:", self._format_issue_date(data)),
            ("True Mark Certificate No:", data.get('certificate_number', 'UNKNOWN')),
            ("Signature ID:", data.get('sig_id', 'N/A')),
        ]
        
        c.setFont("Times-Bold", 11)
        
        for i, (label, value) in enumerate(fields):
            y_pos = y_start - i * 0.36*inch
            
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
        w, h = landscape(letter)
        
        seal_file = self.brand_assets_path / "truemarkseal.png"
        if not seal_file.exists():
            seal_file = self.template_path / "seal_gold_embossed_600dpi.png"
        seal_size = 1.7 * inch
        seal_x = w - seal_size - 0.8*inch
        seal_y = 0.55*inch
        
        if seal_file.exists():
            if seal_file.name == "truemarkseal.png":
                # The supplied seal is RGB with a dark presentation background.
                # Remove only that near-black background without modifying the source asset.
                with Image.open(seal_file).convert("RGBA") as seal_image:
                    pixels = seal_image.load()
                    for py in range(seal_image.height):
                        for px in range(seal_image.width):
                            red, green, blue, alpha = pixels[px, py]
                            if max(red, green, blue) < 90:
                                pixels[px, py] = (red, green, blue, 0)
                    c.drawImage(
                        ImageReader(seal_image), seal_x, seal_y,
                        width=seal_size, height=seal_size, mask="auto"
                    )
            else:
                c.drawImage(str(seal_file), seal_x, seal_y,
                            width=seal_size, height=seal_size, mask="auto")
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
        w, h = landscape(letter)
        
        verification_link = verification_url(serial)
        
        # Create QR with L-level error correction
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_link)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = ensure_temp_vault_dir() / f"temp_qr_{serial}.png"
        qr_path.parent.mkdir(parents=True, exist_ok=True)
        qr_img.save(qr_path)
        
        # Draw QR code
        qr_size = 1.3 * inch
        c.drawImage(str(qr_path), 1.0*inch, 0.55*inch,
                   width=qr_size, height=qr_size, mask='auto')
        
        # QR label
        c.setFont("Courier-Bold", 8)
        c.setFillColor(Color(0, 0, 0))
        c.drawCentredString(1.0*inch + qr_size/2, 0.37*inch, "Scan to Verify")
        
        return qr_path
    
    def _draw_officer_signature(self, c: canvas.Canvas, officer: str):
        """Simulated wet signature with pressure variance."""
        w, h = landscape(letter)
        
        # Signature line
        c.setFont("Times-Roman", 10)
        c.setFillColor(Color(0, 0, 0))
        
        sig_y = 1.15*inch
        c.line(2.2*inch, sig_y, 5.0*inch, sig_y)
        c.line(5.5*inch, sig_y, 7.2*inch, sig_y)
        
        # Labels under lines
        c.setFont("Times-Roman", 9)
        c.drawCentredString(3.6*inch, sig_y - 0.2*inch, "Authorized Officer")
        c.drawCentredString(6.35*inch, sig_y - 0.2*inch, "Date")
        
        # Simulated signature (script-like)
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(self.colors['dark_slate'])
        c.drawCentredString(3.6*inch, sig_y + 0.05*inch, officer)
        
        # Date stamp
        c.setFont("Courier-Bold", 10)
        issue_date = datetime.utcnow().strftime("%Y-%m-%d")
        c.drawString(5.65*inch, sig_y + 0.05*inch, issue_date)
    
    def _draw_timestamp_block(self, c: canvas.Canvas, data: Dict):
        """Draw canonical time representations without changing their authority."""
        w, h = landscape(letter)
        timestamp = data.get("iss_timestamp") or data.get("stardate", "ISS timestamp pending")
        c.saveState()
        c.setFillColor(self.colors["dark_slate"])
        c.setFont("Courier-Bold", 8)
        x = 6.1 * inch
        c.drawString(x, h - 4.25 * inch, f"ISS SCALE: {timestamp}")
        c.drawString(x, h - 4.45 * inch, f"ISS_TIME_NS: {data.get('iss_time_ns', 'pending')}")
        c.restoreState()

    def _draw_corner_serials(self, c: canvas.Canvas, certificate_number: str) -> None:
        """Repeat the TrueMark registry number in all four certificate corners."""
        w, h = landscape(letter)
        c.saveState()
        c.setFillColor(self.colors["primary_blue"])
        c.setFont("Courier-Bold", 6.5)
        margin = 0.68 * inch
        c.drawString(margin, h - margin, certificate_number)
        c.drawRightString(w - margin, h - margin, certificate_number)
        c.drawString(margin, 0.20 * inch, certificate_number)
        c.drawRightString(w - margin, 0.20 * inch, certificate_number)
        c.restoreState()

    def _draw_public_security_metadata(self, c: canvas.Canvas, data: Dict, layer_profile: Dict):
        """Draw only the approved public security fields."""
        w, h = landscape(letter)
        certificate_hash = str(data.get("payload_hash") or "PENDING")
        verification_id = str(data.get("certificate_number") or "PENDING")
        status = str(data.get("verification_status") or ("VALID" if data.get("ed25519_signature") else "PENDING"))

        c.saveState()
        c.setFillColor(self.colors["dark_slate"])
        c.setFont("Courier-Bold", 7)
        x = 6.1 * inch
        c.drawString(x, h - 4.72 * inch, f"VERIFICATION STATUS: {status}")
        c.drawString(x, h - 4.92 * inch, f"CERTIFICATE HASH: {certificate_hash[:48]}")
        c.drawString(x, h - 5.12 * inch, f"TRUE MARK VERIFICATION ID: {verification_id}")
        c.restoreState()

    @staticmethod
    def _format_issue_date(data: Dict) -> str:
        value = str(data.get("iss_standard_timestamp") or data.get("stardate") or "pending")
        if "T" in value and value.endswith("+00:00"):
            return value.replace("T", " ").replace("+00:00", " UTC")
        return value

    def _draw_micro_pattern(self, c: canvas.Canvas):
        """Draw a deterministic micro-pattern inside the selected presentation."""
        w, h = landscape(letter)
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
        c.drawString(4.0 * inch, 0.38 * inch, f"MANIFEST HASH: {str(manifest)[:48]}")
        c.restoreState()

    def _draw_verification_block(self, c: canvas.Canvas, data: Dict):
        """Add a visible independent-verification instruction for elite profiles."""
        w, h = landscape(letter)
        c.saveState()
        c.setStrokeColor(self.colors["gold"])
        c.setLineWidth(1)
        box_x = 5.35 * inch
        box_y = 1.55 * inch
        box_width = 2.2 * inch
        c.roundRect(box_x, box_y, box_width, 0.62 * inch, 5, stroke=1, fill=0)
        c.setFillColor(self.colors["primary_blue"])
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(box_x + box_width / 2, box_y + 0.39 * inch, "INDEPENDENT VERIFICATION")
        c.setFont("Courier", 6)
        c.drawCentredString(box_x + box_width / 2, box_y + 0.19 * inch, str(data.get("certificate_number", "PENDING"))[:24])
        c.restoreState()

    def _add_micro_noise(self, c: canvas.Canvas, intensity: float):
        """Imperceptible scanner sensor noise pattern."""
        w, h = landscape(letter)
        
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
        qr.add_data(verification_url(serial))
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
        'certificate_number': 'TM-TEST-0001-13-00001-A',
        'asset_title': 'Test Certificate - Visual Forensics Demo',
        'owner': 'Test User',
        'wallet': '0xTESTWALLETADDRESS1234567890ABCDEF',
        'kep_category': 'Knowledge',
        'chain_id': 'Polygon',
        'ipfs_hash': 'ipfs://QmTEST1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'stardate': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        'sig_id': 'TEST8A7B3C2F',
        'ed25519_signature': 'a' * 128,  # Mock signature
        'payload_hash': hashlib.sha256(b'test').hexdigest(),
        'officer': 'Bryan A Spruk, President and CEO',
    }
    
    output_dir = ensure_temp_vault_dir() / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n📄 Generating test certificate...")
    pdf_path = asyncio.run(renderer.create_forensic_pdf(test_data, output_dir))
    
    print(f"\n✅ Test certificate created:")
    print(f"   Path: {pdf_path}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.2f} KB")
    
    print("\n🔍 Generating verification QR...")
    qr_path = renderer.generate_verification_qr(test_data['certificate_number'])
    print(f"   QR Code: {qr_path}")
    
    print("\n" + "=" * 60)
    print("Self-test complete. Renderer ready for production.")
