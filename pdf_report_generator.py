#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Report Generator for Website Diagnosis Tool (Bilingual Version)
英語と日本語を併記したPDFレポート生成モジュール
フォント問題を解決し、どの環境でも正しく表示されます
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO

class BilingualPDFReportGenerator:
    """英語・日本語併記のPDFレポート生成クラス（フォント問題解決版）"""
    
    def __init__(self, diagnosis_data):
        """
        初期化
        
        Args:
            diagnosis_data: 診断結果データ（辞書形式）
        """
        self.data = diagnosis_data
        self.elements = []
        
        # フォント設定は不要（英語のみで読みやすく）
        
        # スタイルシート
        self.styles = getSampleStyleSheet()
        
        # カスタムスタイル定義
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """カスタムスタイルの設定"""
        
        # タイトルスタイル
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # 見出しスタイル（大）
        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # 見出しスタイル（中）
        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # 本文スタイル
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # スコア表示スタイル
        self.score_style = ParagraphStyle(
            'ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
    
    def _get_score_color(self, score):
        """スコアに応じた色を取得"""
        if score >= 80:
            return colors.HexColor('#27ae60')  # 緑
        elif score >= 60:
            return colors.HexColor('#f39c12')  # オレンジ
        elif score >= 40:
            return colors.HexColor('#e67e22')  # 濃いオレンジ
        else:
            return colors.HexColor('#e74c3c')  # 赤
    
    def _create_cover_page(self):
        """表紙ページを作成"""
        
        # タイトル
        title = Paragraph(
            "Website Diagnosis Report<br/>ウェブサイト診断レポート",
            self.title_style
        )
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.5*inch))
        
        # URL
        url_text = f"<b>Target URL / 診断対象URL:</b><br/>{self.data.get('url', 'N/A')}"
        url_para = Paragraph(url_text, self.body_style)
        self.elements.append(url_para)
        self.elements.append(Spacer(1, 0.3*inch))
        
        # 診断日時
        timestamp = self.data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date_text = f"<b>Diagnosis Date / 診断日時:</b> {timestamp}"
        date_para = Paragraph(date_text, self.body_style)
        self.elements.append(date_para)
        self.elements.append(Spacer(1, 0.5*inch))
        
        # 総合スコア
        overall_score = self.data.get('overall_score', 0)
        score_text = f"<font color='#2c3e50'><b>{overall_score:.1f}</b></font> / 100"
        score_para = Paragraph(score_text, self.score_style)
        self.elements.append(score_para)
        
        self.elements.append(Spacer(1, 0.2*inch))
        overall_label = Paragraph(
            "<b>Overall Score / 総合スコア</b>",
            ParagraphStyle('CenterLabel', parent=self.body_style, alignment=TA_CENTER, fontSize=14)
        )
        self.elements.append(overall_label)
        
        self.elements.append(Spacer(1, 1*inch))
        
        # フッター（ビーズクリエイト）
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.body_style,
            alignment=TA_CENTER,
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d')
        )
        footer = Paragraph(
            "Generated by B's Cre8 Website Diagnosis Tool<br/>ビーズクリエイト ウェブサイト診断ツール",
            footer_style
        )
        self.elements.append(footer)
        
        # 改ページ
        self.elements.append(PageBreak())
    
    def _create_summary_section(self):
        """サマリーセクションを作成"""
        
        # セクションタイトル
        title = Paragraph("Diagnosis Summary / 診断サマリー", self.heading1_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.2*inch))
        
        # スコア表
        scores = self.data.get('scores', {})
        
        score_data = [
            ['Category / カテゴリ', 'Score / スコア', 'Status / 状態']
        ]
        
        categories = {
            'seo': 'SEO',
            'security': 'Security / セキュリティ',
            'performance': 'Performance / パフォーマンス',
            'accessibility': 'Accessibility / アクセシビリティ'
        }
        
        for key, label in categories.items():
            score = scores.get(key, 0)
            status = self._get_status_label(score)
            score_data.append([label, f"{score:.1f}", status])
        
        # テーブル作成
        score_table = Table(score_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        score_table.setStyle(TableStyle([
            # ヘッダー行
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # データ行
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        
        self.elements.append(score_table)
        self.elements.append(Spacer(1, 0.5*inch))
    
    def _get_status_label(self, score):
        """スコアに応じたステータスラベルを取得"""
        if score >= 80:
            return "Excellent / 優秀"
        elif score >= 60:
            return "Good / 良好"
        elif score >= 40:
            return "Average / 平均"
        else:
            return "Poor / 要改善"
    
    def _create_detail_section(self, category_key, category_title_en, category_title_ja):
        """詳細セクションを作成"""
        
        # セクションタイトル
        title = Paragraph(f"{category_title_en} / {category_title_ja}", self.heading1_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.2*inch))
        
        # スコア表示
        score = self.data.get('scores', {}).get(category_key, 0)
        score_color = self._get_score_color(score)
        
        score_text = f"<font color='{score_color.hexval()}'><b>{score:.1f}</b></font> / 100"
        score_para = Paragraph(score_text, self.score_style)
        self.elements.append(score_para)
        self.elements.append(Spacer(1, 0.3*inch))
        
        # 詳細データ
        details = self.data.get(category_key, {})
        
        # 改善点（Issues）
        issues = details.get('issues', [])
        if issues:
            issues_title = Paragraph("<b>Issues to Improve / 改善が必要な項目:</b>", self.heading2_style)
            self.elements.append(issues_title)
            
            for issue in issues:
                # 英語の説明を取得
                issue_text_en = self._translate_issue_to_english(issue)
                issue_bullet = f"<bullet>&bull;</bullet> {issue} / {issue_text_en}"
                issue_para = Paragraph(issue_bullet, self.body_style)
                self.elements.append(issue_para)
            
            self.elements.append(Spacer(1, 0.2*inch))
        
        # 正常項目（Success）
        success = details.get('success', [])
        if success:
            success_title = Paragraph("<b>Passed Items / 正常な項目:</b>", self.heading2_style)
            self.elements.append(success_title)
            
            for item in success:
                # 英語の説明を取得
                item_text_en = self._translate_success_to_english(item)
                success_bullet = f"<bullet>&bull;</bullet> {item} / {item_text_en}"
                success_para = Paragraph(success_bullet, self.body_style)
                self.elements.append(success_para)
            
            self.elements.append(Spacer(1, 0.2*inch))
        
        # 改ページ
        self.elements.append(PageBreak())
    
    def _translate_issue_to_english(self, issue_text):
        """日本語の問題点を英語に翻訳"""
        translations = {
            'titleタグが見つかりません': 'Title tag not found',
            'meta descriptionが見つかりません': 'Meta description not found',
            'H1タグが複数あります': 'Multiple H1 tags found',
            'H1タグが見つかりません': 'H1 tag not found',
            'alt属性のない画像があります': 'Images without alt attributes',
            'Open Graphタグが設定されていません': 'Open Graph tags not configured',
            'Twitter Cardタグが設定されていません': 'Twitter Card tags not configured',
            'canonicalタグが設定されていません': 'Canonical tag not configured',
            '構造化データが見つかりません': 'Structured data not found',
            'Strict-Transport-Securityヘッダーが設定されていません': 'Strict-Transport-Security header missing',
            'X-Frame-Optionsヘッダーが設定されていません': 'X-Frame-Options header missing',
            'X-Content-Type-Optionsヘッダーが設定されていません': 'X-Content-Type-Options header missing',
            'X-XSS-Protectionヘッダーが設定されていません': 'X-XSS-Protection header missing',
            'Content-Security-Policyヘッダーが設定されていません': 'Content-Security-Policy header missing',
            'Referrer-Policyヘッダーが設定されていません': 'Referrer-Policy header missing',
            'Permissions-Policyヘッダーが設定されていません': 'Permissions-Policy header missing',
            'ページの読み込みが遅い': 'Slow page load time',
            'ページサイズが大きい': 'Large page size',
            'リソース数が多すぎます': 'Too many resources',
            'Gzip圧縮が有効になっていません': 'Gzip compression not enabled',
            'Cache-Controlヘッダーが設定されていません': 'Cache-Control header missing',
            'HTML要素にlang属性がありません': 'HTML element missing lang attribute',
            'alt属性のない画像があります': 'Images without alt attributes',
            'labelがないフォーム要素があります': 'Form elements without labels',
            'ARIA属性が使用されていません': 'ARIA attributes not used',
            'mainランドマークがありません': 'Main landmark missing',
            '見出しの階層構造に問題があります': 'Heading hierarchy issues',
            'テキストのないリンクがあります': 'Links without text'
        }
        
        # 部分一致で翻訳を探す
        for jp, en in translations.items():
            if jp in issue_text:
                return en
        
        return 'Issue detected'
    
    def _translate_success_to_english(self, success_text):
        """日本語の正常項目を英語に翻訳"""
        translations = {
            'titleタグが設定されています': 'Title tag configured',
            'meta descriptionが設定されています': 'Meta description configured',
            'H1タグが1つだけあります': 'Single H1 tag found',
            'HTTPSが使用されています': 'HTTPS enabled',
            'SSL証明書が有効です': 'Valid SSL certificate',
            'ページの読み込みが高速です': 'Fast page load time',
            'ページサイズが適切です': 'Appropriate page size',
            'Gzip圧縮が有効です': 'Gzip compression enabled',
            'Cache-Controlが設定されています': 'Cache-Control configured',
            'HTML要素にlang属性があります': 'HTML lang attribute present'
        }
        
        # 部分一致で翻訳を探す
        for jp, en in translations.items():
            if jp in success_text:
                return en
        
        return 'Item passed'
    
    def _create_recommendations(self):
        """推奨改善項目セクションを作成"""
        
        # セクションタイトル
        title = Paragraph("Priority Improvements / 優先改善項目", self.heading1_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 0.2*inch))
        
        # 全カテゴリの問題点を収集
        all_issues = []
        
        categories = {
            'seo': ('SEO', 55),
            'security': ('Security', 30),
            'performance': ('Performance', 75),
            'accessibility': ('Accessibility', 30)
        }
        
        for key, (cat_name, score) in categories.items():
            details = self.data.get(key, {})
            issues = details.get('issues', [])
            
            for issue in issues:
                priority = self._calculate_priority(key, score)
                all_issues.append({
                    'category': cat_name,
                    'issue': issue,
                    'priority': priority
                })
        
        # 優先度順にソート
        all_issues.sort(key=lambda x: x['priority'], reverse=True)
        
        # Top 10を表示
        top_issues = all_issues[:10]
        
        if top_issues:
            for idx, item in enumerate(top_issues, 1):
                issue_text_en = self._translate_issue_to_english(item['issue'])
                issue_str = f"<b>{idx}. [{item['category']}]</b> {item['issue']}<br/><i>{issue_text_en}</i>"
                issue_para = Paragraph(issue_str, self.body_style)
                self.elements.append(issue_para)
                self.elements.append(Spacer(1, 0.1*inch))
        else:
            no_issues = Paragraph(
                "No critical issues found / 重大な問題は見つかりませんでした",
                self.body_style
            )
            self.elements.append(no_issues)
    
    def _calculate_priority(self, category, score):
        """優先度を計算"""
        # スコアが低いほど優先度が高い
        base_priority = 100 - score
        
        # カテゴリ別の重み付け
        weights = {
            'security': 1.5,  # セキュリティは重要
            'accessibility': 1.3,  # アクセシビリティも重要
            'seo': 1.2,
            'performance': 1.0
        }
        
        weight = weights.get(category, 1.0)
        return base_priority * weight
    
    def generate_pdf(self, output_path):
        """PDFを生成"""
        
        # ドキュメント作成
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # 各セクションを作成
        self._create_cover_page()
        self._create_summary_section()
        
        # 各カテゴリの詳細
        self._create_detail_section('seo', 'SEO Analysis', 'SEO分析')
        self._create_detail_section('security', 'Security Check', 'セキュリティチェック')
        self._create_detail_section('performance', 'Performance Metrics', 'パフォーマンス測定')
        self._create_detail_section('accessibility', 'Accessibility Check', 'アクセシビリティチェック')
        
        # 推奨改善項目
        self._create_recommendations()
        
        # PDFビルド
        doc.build(self.elements)
        
        return output_path


def create_bilingual_pdf_report(diagnosis_data, output_dir='./'):
    """
    バイリンガル（英語・日本語併記）PDFレポートを生成
    
    Args:
        diagnosis_data: 診断結果データ
        output_dir: 出力ディレクトリ
    
    Returns:
        生成されたPDFファイルのパス
    """
    
    # タイムスタンプ
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"diagnosis_report_{timestamp}.pdf"
    output_path = os.path.join(output_dir, output_filename)
    
    # PDFジェネレーター作成
    generator = BilingualPDFReportGenerator(diagnosis_data)
    
    # PDF生成
    generator.generate_pdf(output_path)
    
    print(f"✅ Bilingual PDF report generated: {output_path}")
    
    return output_path


if __name__ == '__main__':
    # テスト用のダミーデータ
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
                'X-Frame-Optionsヘッダーが設定されていません',
                'Content-Security-Policyヘッダーが設定されていません'
            ],
            'success': [
                'HTTPSが使用されています',
                'SSL証明書が有効です'
            ]
        },
        'performance': {
            'issues': [
                'リソース数が多すぎます: 151個'
            ],
            'success': [
                'ページの読み込みが高速です: 0.72秒',
                'ページサイズが適切です: 68.27 KB'
            ]
        },
        'accessibility': {
            'issues': [
                'HTML要素にlang属性がありません',
                'alt属性のない画像があります: 50/118',
                'mainランドマークがありません',
                'テキストのないリンクがあります: 8個'
            ],
            'success': []
        }
    }
    
    # PDFレポート生成
    create_bilingual_pdf_report(test_data, './')
