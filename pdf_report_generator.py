#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Report Generator for Website Diagnosis Tool (English Only)
英語のみのPDFレポート生成モジュール - フォント問題完全解決版
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors

class EnglishPDFReportGenerator:
    """英語のみのPDFレポート生成クラス（フォント問題解決版）"""
    
    def __init__(self, diagnosis_data):
        """
        Initialize PDF Report Generator
        
        Args:
            diagnosis_data: Diagnosis results data (dictionary format)
        """
        self.data = diagnosis_data
        self.elements = []
        
        # Style sheet
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles"""
        
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Heading 1 style
        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=15,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        # Heading 2 style
        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            leading=16,
            fontName='Helvetica'
        )
        
        # Score display style
        self.score_style = ParagraphStyle(
            'ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 80:
            return colors.HexColor('#27ae60')  # Green
        elif score >= 60:
            return colors.HexColor('#f39c12')  # Orange
        elif score >= 40:
            return colors.HexColor('#e67e22')  # Dark orange
        else:
            return colors.HexColor('#e74c3c')  # Red
    
    def _create_cover_page(self):
        """Create cover page"""
        
        # Title（ビーズクリエイト追加）
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=self.body_style,
            alignment=TA_CENTER,
            fontSize=14,
            textColor=colors.HexColor('#667eea'),
            fontName='Helvetica-Bold'
        )
        company = Paragraph("B's Cre8 (Beads Create)", company_style)
        self.elements.append(company)
        self.elements.append(Spacer(1, 0.2*inch))
        
        title = Paragraph("Website Diagnosis Report", self.title_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.5*inch))
        
        # URL
        url_text = f"<b>Target URL:</b><br/>{self.data.get('url', 'N/A')}"
        url_para = Paragraph(url_text, self.body_style)
        self.elements.append(url_para)
        self.elements.append(Spacer(1, 0.3*inch))
        
        # Diagnosis date
        timestamp = self.data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date_text = f"<b>Diagnosis Date:</b> {timestamp}"
        date_para = Paragraph(date_text, self.body_style)
        self.elements.append(date_para)
        self.elements.append(Spacer(1, 0.5*inch))
        
        # Overall score
        overall_score = self.data.get('overall_score', 0)
        score_color = self._get_score_color(overall_score)
        score_text = f"<font color='{score_color.hexval()}'><b>{overall_score:.1f}</b></font> / 100"
        score_para = Paragraph(score_text, self.score_style)
        self.elements.append(score_para)
        
        self.elements.append(Spacer(1, 0.2*inch))
        overall_label = Paragraph(
            "<b>Overall Score</b>",
            ParagraphStyle('CenterLabel', parent=self.body_style, alignment=TA_CENTER, fontSize=16, fontName='Helvetica-Bold')
        )
        self.elements.append(overall_label)
        
        self.elements.append(Spacer(1, 1*inch))
        
        # Footer（ビーズクリエイト追加）
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.body_style,
            alignment=TA_CENTER,
            fontSize=11,
            textColor=colors.HexColor('#7f8c8d')
        )
        footer = Paragraph(
            "<b>Generated by B's Cre8 (Beads Create)</b><br/>Website Diagnosis Tool<br/>https://www.bscre8.com/",
            footer_style
        )
        self.elements.append(footer)
        
        # Page break
        self.elements.append(PageBreak())
    
    def _create_summary_section(self):
        """Create summary section"""
        
        # Section title
        title = Paragraph("Diagnosis Summary", self.heading1_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.2*inch))
        
        # Score table
        scores = self.data.get('scores', {})
        
        score_data = [
            ['Category', 'Score', 'Status']
        ]
        
        categories = {
            'seo': 'SEO',
            'security': 'Security',
            'performance': 'Performance',
            'accessibility': 'Accessibility'
        }
        
        for key, label in categories.items():
            score = scores.get(key, 0)
            status = self._get_status_label(score)
            score_data.append([label, f"{score:.1f}", status])
        
        # Create table
        score_table = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        score_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 13),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10)
        ]))
        
        self.elements.append(score_table)
        self.elements.append(Spacer(1, 0.5*inch))
    
    def _get_status_label(self, score):
        """Get status label based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        else:
            return "Poor"
    
    def _create_detail_section(self, category_key, category_title):
        """Create detail section"""
        
        # Section title
        title = Paragraph(category_title, self.heading1_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.2*inch))
        
        # Score display
        score = self.data.get('scores', {}).get(category_key, 0)
        score_color = self._get_score_color(score)
        
        score_text = f"<font color='{score_color.hexval()}'><b>{score:.1f}</b></font> / 100"
        score_para = Paragraph(score_text, 
            ParagraphStyle('DetailScore', parent=self.score_style, fontSize=36)
        )
        self.elements.append(score_para)
        self.elements.append(Spacer(1, 0.3*inch))
        
        # Detail data
        details = self.data.get(category_key, {})
        
        # Issues
        issues = details.get('issues', [])
        if issues:
            issues_title = Paragraph("<b>Issues to Improve:</b>", self.heading2_style)
            self.elements.append(issues_title)
            
            for issue in issues:
                issue_text = self._translate_to_english(issue)
                issue_bullet = f"<bullet>&bull;</bullet> {issue_text}"
                issue_para = Paragraph(issue_bullet, self.body_style)
                self.elements.append(issue_para)
            
            self.elements.append(Spacer(1, 0.2*inch))
        
        # Success items
        success = details.get('success', [])
        if success:
            success_title = Paragraph("<b>Passed Items:</b>", self.heading2_style)
            self.elements.append(success_title)
            
            for item in success:
                item_text = self._translate_to_english(item)
                success_bullet = f"<bullet>&bull;</bullet> {item_text}"
                success_para = Paragraph(success_bullet, self.body_style)
                self.elements.append(success_para)
            
            self.elements.append(Spacer(1, 0.2*inch))
        
        # Page break
        self.elements.append(PageBreak())
    
    def _translate_to_english(self, text):
        """Translate Japanese text to English"""
        translations = {
            # SEO
            'titleタグが見つかりません': 'Title tag not found',
            'タイトルの長さが最適ではありません': 'Title length is not optimal',
            'meta descriptionが見つかりません': 'Meta description not found',
            'メタディスクリプションの長さが最適ではありません': 'Meta description length is not optimal',
            'H1タグが複数あります': 'Multiple H1 tags found',
            'H1タグが見つかりません': 'H1 tag not found',
            'H2タグがありません': 'H2 tag not found',
            'alt属性のない画像があります': 'Images without alt attributes found',
            '一部の画像にalt属性がありません': 'Some images missing alt attributes',
            '多くの画像にalt属性がありません': 'Many images missing alt attributes',
            'Open Graphタグが設定されていません': 'Open Graph tags not configured',
            'Twitter Cardタグが設定されていません': 'Twitter Card tags not configured',
            'canonicalタグが設定されていません': 'Canonical tag not configured',
            '構造化データが見つかりません': 'Structured data not found',
            'titleタグが設定されています': 'Title tag is configured',
            'meta descriptionが設定されています': 'Meta description is configured',
            'H1タグが1つだけあります': 'Single H1 tag found',
            
            # Security
            'HTTPSを使用していません': 'HTTPS not enabled (security risk)',
            'Strict-Transport-Securityヘッダーが設定されていません': 'Strict-Transport-Security header not set',
            'X-Frame-Optionsヘッダーが設定されていません': 'X-Frame-Options header not set',
            'X-Content-Type-Optionsヘッダーが設定されていません': 'X-Content-Type-Options header not set',
            'X-XSS-Protectionヘッダーが設定されていません': 'X-XSS-Protection header not set',
            'Content-Security-Policyヘッダーが設定されていません': 'Content-Security-Policy header not set',
            'Referrer-Policyヘッダーが設定されていません': 'Referrer-Policy header not set',
            'Permissions-Policyヘッダーが設定されていません': 'Permissions-Policy header not set',
            'HTTPSが使用されています': 'HTTPS enabled',
            'SSL証明書が有効です': 'Valid SSL certificate',
            
            # Performance
            'ページ読み込み時間がやや遅いです': 'Page load time is slightly slow',
            'ページ読み込み時間が遅いです': 'Page load time is slow',
            'ページ読み込み時間が非常に遅いです': 'Page load time is very slow',
            'ページサイズがやや大きいです': 'Page size is slightly large',
            'ページサイズが大きいです': 'Page size is large',
            'ページサイズが非常に大きいです': 'Page size is very large',
            'リソース数が多すぎます': 'Too many resources',
            'コンテンツ圧縮が使用されていません': 'Content compression not enabled',
            'Cache-Controlヘッダーが設定されていません': 'Cache-Control header not set',
            'インラインスタイルが多用されています': 'Excessive use of inline styles',
            'ページの読み込みが高速です': 'Fast page load time',
            'ページサイズが適切です': 'Appropriate page size',
            'Gzip圧縮が有効です': 'Gzip compression enabled',
            'Cache-Controlが設定されています': 'Cache-Control header configured',
            
            # Accessibility
            'HTML要素にlang属性がありません': 'HTML element missing lang attribute',
            '個の画像にalt属性がありません': 'images missing alt attributes',
            '一部のフォーム要素にラベルがありません': 'Some form elements missing labels',
            '多くのフォーム要素にラベルがありません': 'Many form elements missing labels',
            'mainランドマークがありません': 'Main landmark not found',
            '見出しレベルが飛ばされています': 'Heading hierarchy issues',
            'リンクにテキストがありません': 'Links without text',
            '個のリンクにテキストがありません': 'links without text',
            '負のtabindex値が使用されています': 'Negative tabindex values used',
            'HTML要素にlang属性があります': 'HTML lang attribute present'
        }
        
        # Try exact match first
        if text in translations:
            return translations[text]
        
        # Try partial match
        for jp, en in translations.items():
            if jp in text:
                # Replace Japanese part with English
                return text.replace(jp, en)
        
        # If no match, return original (might be already in English or a number)
        return text
    
    def _create_recommendations(self):
        """Create priority improvements section"""
        
        # Section title
        title = Paragraph("Priority Improvements", self.heading1_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.2*inch))
        
        # Collect all issues
        all_issues = []
        
        categories = {
            'seo': 'SEO',
            'security': 'Security',
            'performance': 'Performance',
            'accessibility': 'Accessibility'
        }
        
        for key, cat_name in categories.items():
            details = self.data.get(key, {})
            issues = details.get('issues', [])
            score = self.data.get('scores', {}).get(key, 0)
            
            for issue in issues:
                priority = self._calculate_priority(key, score)
                all_issues.append({
                    'category': cat_name,
                    'issue': issue,
                    'priority': priority
                })
        
        # Sort by priority
        all_issues.sort(key=lambda x: x['priority'], reverse=True)
        
        # Show top 10
        top_issues = all_issues[:10]
        
        if top_issues:
            for idx, item in enumerate(top_issues, 1):
                issue_text = self._translate_to_english(item['issue'])
                issue_str = f"<b>{idx}. [{item['category']}]</b> {issue_text}"
                issue_para = Paragraph(issue_str, self.body_style)
                self.elements.append(issue_para)
                self.elements.append(Spacer(1, 0.15*inch))
        else:
            no_issues = Paragraph("No critical issues found", self.body_style)
            self.elements.append(no_issues)
    
    def _calculate_priority(self, category, score):
        """Calculate priority"""
        # Lower score = higher priority
        base_priority = 100 - score
        
        # Category weights
        weights = {
            'security': 1.5,
            'accessibility': 1.3,
            'seo': 1.2,
            'performance': 1.0
        }
        
        weight = weights.get(category, 1.0)
        return base_priority * weight
    
    def generate_pdf(self, output_path):
        """Generate PDF"""
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Create sections
        self._create_cover_page()
        self._create_summary_section()
        
        # Category details
        self._create_detail_section('seo', 'SEO Analysis')
        self._create_detail_section('security', 'Security Check')
        self._create_detail_section('performance', 'Performance Metrics')
        self._create_detail_section('accessibility', 'Accessibility Check')
        
        # Recommendations
        self._create_recommendations()
        
        # Build PDF
        doc.build(self.elements)
        
        return output_path


def create_english_pdf_report(diagnosis_data, output_dir='./'):
    """
    Generate English-only PDF report
    
    Args:
        diagnosis_data: Diagnosis results data
        output_dir: Output directory
    
    Returns:
        Generated PDF file path
    """
    
    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"diagnosis_report_{timestamp}.pdf"
    output_path = os.path.join(output_dir, output_filename)
    
    # Create PDF generator
    generator = EnglishPDFReportGenerator(diagnosis_data)
    
    # Generate PDF
    generator.generate_pdf(output_path)
    
    print(f"✅ English PDF report generated: {output_path}")
    
    return output_path


if __name__ == '__main__':
    # Test data
    test_data = {
        'url': 'https://www.bscre8.com/',
        'timestamp': '2025-12-04 09:12:47',
        'overall_score': 46.5,
        'scores': {
            'seo': 55.0,
            'security': 30.0,
            'performance': 75.0,
            'accessibility': 30.0
        },
        'seo': {
            'issues': [
                'H1タグが複数あります: 2個',
                'alt属性のない画像があります: 68/118'
            ],
            'success': [
                'titleタグが設定されています',
                'meta descriptionが設定されています'
            ]
        },
        'security': {
            'issues': [
                'Strict-Transport-Securityヘッダーが設定されていません',
                'X-Frame-Optionsヘッダーが設定されていません'
            ],
            'success': [
                'HTTPSが使用されています'
            ]
        },
        'performance': {
            'issues': [
                'リソース数が多すぎます: 151個'
            ],
            'success': [
                'ページの読み込みが高速です: 0.72秒'
            ]
        },
        'accessibility': {
            'issues': [
                'HTML要素にlang属性がありません',
                'mainランドマークがありません'
            ],
            'success': []
        }
    }
    
    # Generate PDF
    create_english_pdf_report(test_data, './')
