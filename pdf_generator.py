import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Color palette
COFFEE_BROWN = colors.HexColor("#3D1F0D")
COFFEE_MEDIUM = colors.HexColor("#6B3A2A")
COFFEE_LIGHT = colors.HexColor("#C4956A")
COFFEE_CREAM = colors.HexColor("#F5ECD7")
COFFEE_GOLD = colors.HexColor("#D4A853")
DARK_TEXT = colors.HexColor("#1A1A1A")
GRAY_TEXT = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#F0F0F0")
WHITE = colors.white
ACCENT_GREEN = colors.HexColor("#4A7C59")


def register_fonts():
    """Register Noto fonts with full Cyrillic support."""
    noto_base = "/usr/share/fonts/truetype/noto/"
    pdfmetrics.registerFont(TTFont("NotoSans", noto_base + "NotoSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("NotoSans-Bold", noto_base + "NotoSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("NotoSans-Italic", noto_base + "NotoSans-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("NotoSans-BoldItalic", noto_base + "NotoSans-BoldItalic.ttf"))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily(
        "NotoSans",
        normal="NotoSans",
        bold="NotoSans-Bold",
        italic="NotoSans-Italic",
        boldItalic="NotoSans-BoldItalic"
    )


def get_styles():
    styles = getSampleStyleSheet()

    custom_styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="NotoSans-Bold",
            fontSize=32,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=38,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName="NotoSans",
            fontSize=14,
            textColor=COFFEE_CREAM,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName="NotoSans",
            fontSize=11,
            textColor=COFFEE_LIGHT,
            alignment=TA_CENTER,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName="NotoSans-Bold",
            fontSize=18,
            textColor=COFFEE_BROWN,
            spaceBefore=20,
            spaceAfter=10,
            leading=22,
        ),
        "subsection_header": ParagraphStyle(
            "subsection_header",
            fontName="NotoSans-Bold",
            fontSize=13,
            textColor=COFFEE_MEDIUM,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body_text": ParagraphStyle(
            "body_text",
            fontName="NotoSans",
            fontSize=10,
            textColor=DARK_TEXT,
            spaceAfter=4,
            leading=15,
            alignment=TA_JUSTIFY,
        ),
        "bullet_item": ParagraphStyle(
            "bullet_item",
            fontName="NotoSans",
            fontSize=10,
            textColor=DARK_TEXT,
            spaceAfter=3,
            leading=14,
            leftIndent=15,
            bulletIndent=0,
        ),
        "highlight_text": ParagraphStyle(
            "highlight_text",
            fontName="NotoSans-Bold",
            fontSize=11,
            textColor=COFFEE_MEDIUM,
            spaceAfter=4,
        ),
        "tag_text": ParagraphStyle(
            "tag_text",
            fontName="NotoSans",
            fontSize=9,
            textColor=COFFEE_BROWN,
            alignment=TA_CENTER,
        ),
        "footer_text": ParagraphStyle(
            "footer_text",
            fontName="NotoSans",
            fontSize=8,
            textColor=GRAY_TEXT,
            alignment=TA_CENTER,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="NotoSans-Italic",
            fontSize=9,
            textColor=GRAY_TEXT,
            spaceAfter=4,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value",
            fontName="NotoSans-Bold",
            fontSize=16,
            textColor=COFFEE_GOLD,
            alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label",
            fontName="NotoSans",
            fontSize=9,
            textColor=GRAY_TEXT,
            alignment=TA_CENTER,
        ),
        "week_header": ParagraphStyle(
            "week_header",
            fontName="NotoSans-Bold",
            fontSize=11,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
        "post_idea": ParagraphStyle(
            "post_idea",
            fontName="NotoSans",
            fontSize=9,
            textColor=DARK_TEXT,
            leading=13,
        ),
        "post_hook": ParagraphStyle(
            "post_hook",
            fontName="NotoSans-Italic",
            fontSize=9,
            textColor=COFFEE_MEDIUM,
            leading=13,
        ),
    }
    return custom_styles


def add_page_background(canvas, doc):
    """Add subtle background and footer to each page."""
    canvas.saveState()
    width, height = A4

    # Subtle top bar
    canvas.setFillColor(COFFEE_BROWN)
    canvas.rect(0, height - 8, width, 8, fill=1, stroke=0)

    # Footer
    canvas.setFillColor(COFFEE_CREAM)
    canvas.rect(0, 0, width, 25, fill=1, stroke=0)
    canvas.setFillColor(GRAY_TEXT)
    canvas.setFont("NotoSans", 8)
    canvas.drawCentredString(width / 2, 9, f"CoffeeStrategy.ru — Маркетинговая стратегия | Стр. {doc.page}")

    canvas.restoreState()


def build_cover_page(story, brief_data, report_id, styles):
    """Build professional cover page."""
    width, height = A4

    # Cover background table
    cover_data = [[""]]
    cover_table = Table(cover_data, colWidths=[width - 4 * cm], rowHeights=[height * 0.45])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COFFEE_BROWN),
        ("TOPPADDING", (0, 0), (-1, -1), 60),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 40),
    ]))
    story.append(cover_table)

    # Coffee shop name on cover
    story.append(Spacer(1, -height * 0.45 + 1 * cm))

    # Title block
    title_data = [
        [Paragraph("МАРКЕТИНГОВАЯ", styles["cover_title"])],
        [Paragraph("СТРАТЕГИЯ", styles["cover_title"])],
        [Spacer(1, 0.3 * cm)],
        [Paragraph(f"для кофейни «{brief_data.get('coffee_name', '')}»", styles["cover_subtitle"])],
        [Spacer(1, 0.2 * cm)],
        [Paragraph(f"{brief_data.get('location', '')}", styles["cover_meta"])],
    ]
    title_table = Table(title_data, colWidths=[width - 4 * cm])
    title_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COFFEE_BROWN),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(title_table)

    story.append(Spacer(1, 1.5 * cm))

    # Info cards
    date_str = datetime.now().strftime("%d %B %Y")
    info_data = [
        [
            Paragraph(f"<b>Дата создания</b><br/>{date_str}", styles["body_text"]),
            Paragraph(f"<b>ID отчёта</b><br/>#{report_id}", styles["body_text"]),
            Paragraph(f"<b>Тип заведения</b><br/>{brief_data.get('coffee_type', '—')}", styles["body_text"]),
            Paragraph(f"<b>Ценовой сегмент</b><br/>{brief_data.get('price_range', '—')}", styles["body_text"]),
        ]
    ]
    info_table = Table(info_data, colWidths=[(width - 4 * cm) / 4] * 4)
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COFFEE_CREAM),
        ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(info_table)

    story.append(Spacer(1, 1 * cm))

    # What's inside
    story.append(Paragraph("Что включено в этот отчёт:", styles["subsection_header"]))
    contents = [
        ("01", "Анализ целевой аудитории", "Детальные портреты клиентов, инсайты и карта пути покупателя"),
        ("02", "Визуальный брендинг", "Цветовая палитра, типографика, архетип бренда и концепции"),
        ("03", "Контент-план на месяц", "16+ идей постов с хуками для Instagram, VK и Telegram"),
        ("04", "Хэштег-стратегия", "Подобранные хэштеги по категориям для максимального охвата"),
        ("05", "KPI и метрики", "Конкретные цели и показатели для отслеживания роста"),
    ]
    for num, title, desc in contents:
        row_data = [[
            Paragraph(f"<b>{num}</b>", styles["highlight_text"]),
            Paragraph(f"<b>{title}</b><br/><font size='9' color='#555555'>{desc}</font>", styles["body_text"]),
        ]]
        row_table = Table(row_data, colWidths=[1.2 * cm, width - 4 * cm - 1.2 * cm])
        row_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, COFFEE_LIGHT),
        ]))
        story.append(row_table)

    story.append(PageBreak())


def build_audience_section(story, audience, styles):
    """Build audience analysis section."""
    width, height = A4
    story.append(Paragraph("01 — Анализ целевой аудитории", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=2, color=COFFEE_BROWN, spaceAfter=15))

    primary = audience.get("primary_segment", {})
    secondary = audience.get("secondary_segment", {})

    # Primary segment card
    story.append(Paragraph("Основной сегмент", styles["subsection_header"]))

    P = lambda t, s: Paragraph(str(t) if t else '—', styles[s])
    PB = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
    seg_data = [
        [P("Параметр", "highlight_text"), P("Значение", "highlight_text")],
        [PB("Название сегмента"), P(primary.get("name", "—"), "body_text")],
        [PB("Возраст"), P(primary.get("age_range", "—"), "body_text")],
        [PB("Гендерное соотношение"), P(primary.get("gender_split", "—"), "body_text")],
        [PB("Уровень дохода"), P(primary.get("income_level", "—"), "body_text")],
        [PB("Образ жизни"), P(primary.get("lifestyle", "—"), "body_text")],
        [PB("Кофейные привычки"), P(primary.get("coffee_habits", "—"), "body_text")],
    ]

    seg_table = Table(seg_data, colWidths=[5 * cm, width - 4 * cm - 5 * cm])
    seg_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COFFEE_BROWN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, COFFEE_CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
        ("FONTNAME", (0, 1), (0, -1), "NotoSans-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(seg_table)
    story.append(Spacer(1, 0.5 * cm))

    # Values
    values = primary.get("values", [])
    if values:
        story.append(Paragraph("Ценности аудитории:", styles["subsection_header"]))
        val_cells = [[Paragraph(v, styles["tag_text"]) for v in values]]
        col_w = (width - 4 * cm) / max(len(values), 1)
        val_table = Table(val_cells, colWidths=[col_w] * len(values))
        val_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COFFEE_CREAM),
            ("GRID", (0, 0), (-1, -1), 1, COFFEE_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROUNDEDCORNERS", [5]),
        ]))
        story.append(val_table)
        story.append(Spacer(1, 0.5 * cm))

    # Decision factors
    factors = primary.get("decision_factors", [])
    if factors:
        story.append(Paragraph("Факторы принятия решения:", styles["subsection_header"]))
        for i, f in enumerate(factors, 1):
            story.append(Paragraph(f"• {f}", styles["bullet_item"]))
        story.append(Spacer(1, 0.4 * cm))

    # Secondary segment
    if secondary:
        story.append(Paragraph("Вторичный сегмент", styles["subsection_header"]))
        sec_data = [
            [Paragraph(f"<b>{secondary.get('name', '—')}</b>", styles["highlight_text"])],
            [Paragraph(f"Возраст: {secondary.get('age_range', '—')}", styles["body_text"])],
            [Paragraph(secondary.get("description", ""), styles["body_text"])],
            [Paragraph(f"<b>Возможность:</b> {secondary.get('opportunity', '')}", styles["body_text"])],
        ]
        sec_table = Table(sec_data, colWidths=[width - 4 * cm])
        sec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COFFEE_CREAM),
            ("LEFTPADDING", (0, 0), (-1, -1), 15),
            ("RIGHTPADDING", (0, 0), (-1, -1), 15),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINERIGHT", (0, 0), (0, -1), 4, COFFEE_GOLD),
        ]))
        story.append(sec_table)
        story.append(Spacer(1, 0.5 * cm))

    # Customer journey
    journey = audience.get("customer_journey", {})
    if journey:
        story.append(Paragraph("Карта пути клиента", styles["subsection_header"]))
        journey_data = [
            [P("Этап", "highlight_text"), P("Описание", "highlight_text")],
            [PB("Осведомлённость"), P(journey.get("awareness", "—"), "body_text")],
            [PB("Рассмотрение"), P(journey.get("consideration", "—"), "body_text")],
            [PB("Покупка"), P(journey.get("purchase", "—"), "body_text")],
            [PB("Лояльность"), P(journey.get("loyalty", "—"), "body_text")],
        ]
        j_table = Table(journey_data, colWidths=[4 * cm, width - 4 * cm - 4 * cm])
        j_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COFFEE_MEDIUM),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, COFFEE_CREAM]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTNAME", (0, 1), (0, -1), "NotoSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(j_table)
        story.append(Spacer(1, 0.5 * cm))

    # Pain points & insights
    pain_points = audience.get("pain_points", [])
    key_insights = audience.get("key_insights", [])

    if pain_points or key_insights:
        col_data = [[
            [Paragraph("Боли аудитории", styles["subsection_header"])] +
            [Paragraph(f"• {p}", styles["bullet_item"]) for p in pain_points],
            [Paragraph("Ключевые инсайты", styles["subsection_header"])] +
            [Paragraph(f"• {i}", styles["bullet_item"]) for i in key_insights],
        ]]
        # Flatten for table
        pain_content = [Paragraph("Боли аудитории", styles["subsection_header"])] + \
                       [Paragraph(f"• {p}", styles["bullet_item"]) for p in pain_points]
        insight_content = [Paragraph("Ключевые инсайты", styles["subsection_header"])] + \
                          [Paragraph(f"• {i}", styles["bullet_item"]) for i in key_insights]

        two_col = [[pain_content, insight_content]]
        two_table = Table(two_col, colWidths=[(width - 4 * cm) / 2 - 0.3 * cm] * 2)
        two_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#FFF5F5")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F5FFF8")),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
        ]))
        story.append(two_table)

    story.append(PageBreak())


def build_branding_section(story, branding, styles):
    """Build branding section."""
    width, height = A4
    story.append(Paragraph("02 — Визуальный брендинг", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=2, color=COFFEE_BROWN, spaceAfter=15))

    # Brand archetype & tagline
    arch_data = [
        [
            Paragraph(f"<b>Архетип бренда</b><br/><font size='14' color='#6B3A2A'>{branding.get('brand_archetype', '—')}</font>",
                      styles["body_text"]),
            Paragraph(f"<b>Слоган</b><br/><font size='12' color='#3D1F0D'><i>\"{branding.get('tagline', '—')}\"</i></font>",
                      styles["body_text"]),
        ]
    ]
    arch_table = Table(arch_data, colWidths=[(width - 4 * cm) / 2] * 2)
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), COFFEE_CREAM),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FDF8F0")),
        ("GRID", (0, 0), (-1, -1), 1, COFFEE_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 0.6 * cm))

    # Color palette
    palette = branding.get("color_palette", {})
    if palette:
        story.append(Paragraph("Цветовая палитра", styles["subsection_header"]))
        color_names = ["primary", "secondary", "accent", "background"]
        color_labels = ["Основной", "Вторичный", "Акцент", "Фон"]
        color_cells = []
        for cn, cl in zip(color_names, color_labels):
            val = palette.get(cn, "—")
            color_cells.append(Paragraph(f"<b>{cl}</b><br/>{val}", styles["tag_text"]))

        col_table = Table([color_cells], colWidths=[(width - 4 * cm) / 4] * 4)
        col_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COFFEE_CREAM),
            ("GRID", (0, 0), (-1, -1), 1, COFFEE_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(col_table)

        if palette.get("rationale"):
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(f"<i>{palette['rationale']}</i>", styles["caption"]))
        story.append(Spacer(1, 0.5 * cm))

    # Typography
    typography = branding.get("typography", {})
    if typography:
        story.append(Paragraph("Типографика", styles["subsection_header"]))
        PB2 = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
        typo_data = [
            [PB2("Заголовки"), Paragraph(typography.get("heading_font", "—"), styles['body_text'])],
            [PB2("Основной текст"), Paragraph(typography.get("body_font", "—"), styles['body_text'])],
            [PB2("Обоснование"), Paragraph(typography.get("rationale", "—"), styles['body_text'])],
        ]
        typo_table = Table(typo_data, colWidths=[4 * cm, width - 4 * cm - 4 * cm])
        typo_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, COFFEE_CREAM]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTNAME", (0, 0), (0, -1), "NotoSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(typo_table)
        story.append(Spacer(1, 0.5 * cm))

    # Brand voice
    brand_voice = branding.get("brand_voice", {})
    if brand_voice:
        story.append(Paragraph("Голос бренда", styles["subsection_header"]))
        voice_data = [
            [
                Paragraph(f"<b>Тон:</b> {brand_voice.get('tone', '—')}<br/><b>Стиль:</b> {brand_voice.get('style', '—')}",
                          styles["body_text"]),
            ]
        ]
        voice_table = Table(voice_data, colWidths=[width - 4 * cm])
        voice_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COFFEE_CREAM),
            ("LEFTPADDING", (0, 0), (-1, -1), 15),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINELEFT", (0, 0), (0, -1), 4, COFFEE_GOLD),
        ]))
        story.append(voice_table)
        story.append(Spacer(1, 0.4 * cm))

        do_list = brand_voice.get("do", [])
        dont_list = brand_voice.get("dont", [])
        if do_list or dont_list:
            do_content = [Paragraph("<b>Делать:</b>", styles["subsection_header"])] + \
                         [Paragraph(f"✓ {d}", styles["bullet_item"]) for d in do_list]
            dont_content = [Paragraph("<b>Не делать:</b>", styles["subsection_header"])] + \
                           [Paragraph(f"✗ {d}", styles["bullet_item"]) for d in dont_list]
            two_col = [[do_content, dont_content]]
            two_table = Table(two_col, colWidths=[(width - 4 * cm) / 2 - 0.3 * cm] * 2)
            two_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F5FFF8")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FFF5F5")),
                ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ]))
            story.append(two_table)
            story.append(Spacer(1, 0.5 * cm))

    # Visual concepts
    concepts = branding.get("visual_concepts", [])
    if concepts:
        story.append(Paragraph("Визуальные концепции", styles["subsection_header"]))
        for i, c in enumerate(concepts, 1):
            story.append(Paragraph(f"{i}. {c}", styles["body_text"]))
        story.append(Spacer(1, 0.4 * cm))

    # Logo & interior
    logo_dir = branding.get("logo_direction", "")
    interior = branding.get("interior_mood", "")
    if logo_dir or interior:
        PB3 = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
        extra_data = []
        if logo_dir:
            extra_data.append([PB3("Направление логотипа"), Paragraph(logo_dir, styles['body_text'])])
        if interior:
            extra_data.append([PB3("Атмосфера интерьера"), Paragraph(interior, styles['body_text'])])
        extra_table = Table(extra_data, colWidths=[5 * cm, width - 4 * cm - 5 * cm])
        extra_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COFFEE_CREAM, WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTNAME", (0, 0), (0, -1), "NotoSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(extra_table)

    story.append(PageBreak())


def build_content_plan_section(story, content_plan, styles):
    """Build content plan section."""
    width, height = A4
    story.append(Paragraph("03 — Контент-план на месяц", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=2, color=COFFEE_BROWN, spaceAfter=15))

    # Strategy overview
    overview = content_plan.get("strategy_overview", "")
    if overview:
        story.append(Paragraph(overview, styles["body_text"]))
        story.append(Spacer(1, 0.5 * cm))

    # Platforms
    platforms = content_plan.get("platforms", {})
    if platforms:
        story.append(Paragraph("Платформы и частота публикаций", styles["subsection_header"]))
        PBP = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
        PP = lambda t: Paragraph(str(t) if t else '—', styles['body_text'])
        plat_data = [[PBP("Платформа"), PBP("Приоритет"), PBP("Частота"), PBP("Лучшее время")]]
        platform_names = {"instagram": "Instagram", "vkontakte": "ВКонтакте", "telegram": "Telegram"}
        for key, name in platform_names.items():
            p = platforms.get(key, {})
            if p:
                times = ", ".join(p.get("best_times", []))
                plat_data.append([PP(name), PP(p.get("priority", "—")), PP(p.get("posting_frequency", "—")), PP(times)])

        plat_table = Table(plat_data, colWidths=[3.5 * cm, 3 * cm, 5 * cm, width - 4 * cm - 11.5 * cm])
        plat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COFFEE_BROWN),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, COFFEE_CREAM]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(plat_table)
        story.append(Spacer(1, 0.5 * cm))

    # Content pillars
    pillars = content_plan.get("content_pillars", [])
    if pillars:
        story.append(Paragraph("Контентные пиллары", styles["subsection_header"]))
        PPC = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
        PP2 = lambda t: Paragraph(str(t) if t else '—', styles['body_text'])
        pillar_data = [[PPC("Пиллар"), PPC("Описание"), PPC("Доля")]]
        for p in pillars:
            pillar_data.append([PP2(p.get("name", "")), PP2(p.get("description", "")), PP2(p.get("percentage", ""))])

        pillar_table = Table(pillar_data, colWidths=[4 * cm, width - 4 * cm - 6.5 * cm, 2.5 * cm])
        pillar_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COFFEE_MEDIUM),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, COFFEE_CREAM]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTNAME", (0, 1), (0, -1), "NotoSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(pillar_table)
        story.append(Spacer(1, 0.5 * cm))

    # Monthly calendar
    calendar = content_plan.get("monthly_calendar", [])
    if calendar:
        story.append(Paragraph("Календарь публикаций", styles["subsection_header"]))

        week_colors = [COFFEE_BROWN, COFFEE_MEDIUM, COFFEE_LIGHT, COFFEE_GOLD]
        week_text_colors = [WHITE, WHITE, COFFEE_BROWN, COFFEE_BROWN]

        for week_data in calendar:
            week_num = week_data.get("week", 1)
            theme = week_data.get("theme", "")
            posts = week_data.get("posts", [])
            wc = week_colors[(week_num - 1) % 4]
            wtc = week_text_colors[(week_num - 1) % 4]

            # Week header
            week_header_data = [[
                Paragraph(f"<b>Неделя {week_num}</b>", ParagraphStyle("wh", fontName="NotoSans-Bold",
                          fontSize=11, textColor=wtc, alignment=TA_LEFT)),
                Paragraph(f"Тема: {theme}", ParagraphStyle("wt", fontName="NotoSans",
                          fontSize=10, textColor=wtc, alignment=TA_RIGHT)),
            ]]
            wh_table = Table(week_header_data, colWidths=[(width - 4 * cm) / 2] * 2)
            wh_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), wc),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]))
            story.append(wh_table)

            # Posts
            PPD = lambda t: Paragraph(str(t) if t else '—', styles['body_text'])
            post_data = [[PPD("День"), PPD("Платформа"), PPD("Тип"), PPD("Идея и хук")]]
            for post in posts:
                idea_text = post.get("idea", "")
                hook_text = post.get("caption_hook", "")
                combined = f"{idea_text}"
                if hook_text:
                    combined += f"<br/><i>Хук: «{hook_text}»</i>"
                post_data.append([
                    PPD(post.get("day", "")),
                    PPD(post.get("platform", "")),
                    PPD(post.get("type", "")),
                    Paragraph(combined, styles["post_idea"]),
                ])

            post_table = Table(post_data, colWidths=[2.5 * cm, 2.5 * cm, 2.5 * cm, width - 4 * cm - 7.5 * cm])
            post_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
                ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#FAFAFA")]),
                ("GRID", (0, 0), (-1, -1), 0.3, COFFEE_LIGHT),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(post_table)
            story.append(Spacer(1, 0.4 * cm))

    # Hashtag strategy
    hashtags = content_plan.get("hashtag_strategy", {})
    if hashtags:
        story.append(Paragraph("Хэштег-стратегия", styles["subsection_header"]))
        hash_categories = [
            ("Брендовые", "branded", COFFEE_BROWN),
            ("Нишевые", "niche", COFFEE_MEDIUM),
            ("Локальные", "local", ACCENT_GREEN),
            ("Трендовые", "trending", COFFEE_GOLD),
        ]
        hash_data = []
        PHB = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
        PH = lambda t: Paragraph(str(t) if t else '—', styles['body_text'])
        for cat_name, cat_key, cat_color in hash_categories:
            tags = hashtags.get(cat_key, [])
            tags_str = "  ".join([f"#{t.lstrip('#')}" for t in tags])
            hash_data.append([PHB(cat_name), PH(tags_str)])

        hash_table = Table(hash_data, colWidths=[3 * cm, width - 4 * cm - 3 * cm])
        hash_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COFFEE_CREAM, WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTNAME", (0, 0), (0, -1), "NotoSans-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(hash_table)
        story.append(Spacer(1, 0.5 * cm))

    # Engagement tactics
    tactics = content_plan.get("engagement_tactics", [])
    if tactics:
        story.append(Paragraph("Тактики вовлечения", styles["subsection_header"]))
        for t in tactics:
            story.append(Paragraph(f"• {t}", styles["bullet_item"]))

    story.append(PageBreak())


def build_kpi_section(story, strategy, styles):
    """Build KPI and quick wins section."""
    width, height = A4
    story.append(Paragraph("04 — KPI и быстрые победы", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=2, color=COFFEE_BROWN, spaceAfter=15))

    # KPIs
    kpis = strategy.get("kpis", [])
    if kpis:
        story.append(Paragraph("Ключевые показатели эффективности", styles["subsection_header"]))
        PKB = lambda t: Paragraph(f'<b>{t}</b>', styles['body_text'])
        PK = lambda t: Paragraph(str(t) if t else '—', styles['body_text'])
        kpi_data = [[PKB("Метрика"), PKB("Цель"), PKB("Срок")]]
        for kpi in kpis:
            kpi_data.append([PK(kpi.get("metric", "")), PK(kpi.get("target", "")), PK(kpi.get("timeframe", ""))])

        kpi_table = Table(kpi_data, colWidths=[6 * cm, 5 * cm, width - 4 * cm - 11 * cm])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COFFEE_BROWN),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "NotoSans-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, COFFEE_CREAM]),
            ("GRID", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.8 * cm))

    # Quick wins
    quick_wins = strategy.get("quick_wins", [])
    if quick_wins:
        story.append(Paragraph("Быстрые победы (первые 30 дней)", styles["subsection_header"]))
        for i, win in enumerate(quick_wins, 1):
            win_data = [[
                Paragraph(f"<b>{i}</b>", ParagraphStyle("n", fontName="NotoSans-Bold",
                          fontSize=14, textColor=WHITE, alignment=TA_CENTER)),
                Paragraph(win, styles["body_text"]),
            ]]
            win_table = Table(win_data, colWidths=[1 * cm, width - 4 * cm - 1 * cm])
            win_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), COFFEE_GOLD),
                ("BACKGROUND", (1, 0), (1, 0), COFFEE_CREAM),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, COFFEE_LIGHT),
            ]))
            story.append(win_table)

    story.append(Spacer(1, 1 * cm))

    # Final note
    final_data = [[
        Paragraph(
            "<b>Следующие шаги</b><br/>"
            "1. Изучите анализ аудитории и определите приоритетный сегмент<br/>"
            "2. Согласуйте цветовую палитру с дизайнером<br/>"
            "3. Запланируйте первые посты по контент-плану<br/>"
            "4. Настройте аналитику для отслеживания KPI<br/>"
            "5. Вернитесь к стратегии через 30 дней для корректировки",
            styles["body_text"]
        )
    ]]
    final_table = Table(final_data, colWidths=[width - 4 * cm])
    final_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COFFEE_CREAM),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("LINELEFT", (0, 0), (0, -1), 5, COFFEE_GOLD),
    ]))
    story.append(final_table)


def generate_pdf_report(brief_data: dict, strategy: dict, output_path: str, report_id: str):
    """Generate the full PDF report."""
    register_fonts()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Маркетинговая стратегия — {brief_data.get('coffee_name', '')}",
        author="CoffeeStrategy.ru",
    )

    styles = get_styles()
    story = []

    # Cover page
    build_cover_page(story, brief_data, report_id, styles)

    # Audience analysis
    audience = strategy.get("audience_analysis", {})
    if audience:
        build_audience_section(story, audience, styles)

    # Branding
    branding = strategy.get("branding", {})
    if branding:
        build_branding_section(story, branding, styles)

    # Content plan
    content_plan = strategy.get("content_plan", {})
    if content_plan:
        build_content_plan_section(story, content_plan, styles)

    # KPIs
    build_kpi_section(story, strategy, styles)

    # Build PDF
    doc.build(story, onFirstPage=add_page_background, onLaterPages=add_page_background)
