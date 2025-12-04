#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF診断レポート生成モジュール（日本語フォント対応版）
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

class PDFReportGenerator:
    def __init__(self, results, output_filename=None):
        self.results = results
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"website_diagnosis_report_{timestamp}.pdf"
        
        self.output_filename = output_filename
        self.doc = SimpleDocTemplate(output_filename, pagesize=A4)
        self.story = []
        self.styles = getSampleStyleSheet()
        
        # 日本語フォントの設定
        self._setup_fonts()
        
        # カスタムスタイルの作成
        self._setup_styles()
    
    def _setup_fonts(self):
        """日本語フォントのセットアップ"""
        # Windowsの場合、システムフォントを探す
        font_paths = [
            # Windows標準フォント
            'C:/Windows/Fonts/msgothic.ttc',  # MSゴシック
            'C:/Windows/Fonts/meiryo.ttc',    # メイリオ
            'C:/Windows/Fonts/msmincho.ttc',  # MS明朝
            'C:/Windows/Fonts/YuGothM.ttc',   # 游ゴシック Medium
            # Linux標準フォント
            '/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
        ]
        
        self.japanese_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # TrueTypeフォントの登録
                    pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                    self.japanese_font = 'JapaneseFont'
                    print(f"✅ 日本語フォントを登録しました: {font_path}")
                    break
                except Exception as e:
                    print(f"フォント登録エラー ({font_path}): {e}")
                    continue
        
        if not self.japanese_font:
            print("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します。")
            # フォールバック: Helveticaを使用（日本語は表示できない）
            self.japanese_font = 'Helvetica'
    
    def _setup_styles(self):
        """カスタムスタイルのセットアップ"""
        # タイトルスタイル
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.japanese_font,
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # 見出しスタイル
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName=self.japanese_font,
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # サブ見出しスタイル
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontName=self.japanese_font,
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6,
            spaceBefore=6
        ))
        
        # 本文スタイル
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontName=self.japanese_font,
            fontSize=10,
            leading=14
        ))
    
    def _get_score_color(self, score):
        """スコアに応じた色を返す"""
        if score >= 80:
            return colors.HexColor('#27ae60')  # 緑
        elif score >= 60:
            return colors.HexColor('#f39c12')  # オレンジ
        elif score >= 40:
            return colors.HexColor('#e67e22')  # 濃いオレンジ
        else:
            return colors.HexColor('#e74c3c')  # 赤
    
    def _get_score_label(self, score):
        """スコアに応じたラベルを返す"""
        if score >= 80:
            return "優秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "要改善"
        else:
            return "改善必須"
    
    def _create_score_chart(self):
        """スコアチャートの作成（matplotlib使用）"""
        # 日本語フォント設定
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        categories = ['SEO', 'Security', 'Performance', 'Accessibility']
        scores = [
            self.results['seo']['score'],
            self.results['security']['score'],
            self.results['performance']['score'],
            self.results['accessibility']['score']
        ]
        
        colors_list = []
        for score in scores:
            color = self._get_score_color(score)
            if hasattr(color, 'hexval'):
                colors_list.append(color.hexval())
            else:
                colors_list.append('#3498db')
        
        bars = ax.bar(categories, scores, color=colors_list, alpha=0.8)
        ax.set_ylim(0, 100)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Category Scores', fontsize=14, fontweight='bold')
        ax.axhline(y=80, color='green', linestyle='--', alpha=0.3, label='Excellent')
        ax.axhline(y=60, color='orange', linestyle='--', alpha=0.3, label='Good')
        ax.grid(axis='y', alpha=0.3)
        
        # 値を表示
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        
        # 画像として保存
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def generate(self):
        """PDFレポートの生成"""
        # タイトルページ
        self._add_title_page()
        
        # サマリーページ
        self._add_summary_page()
        
        # 各カテゴリの詳細
        self._add_seo_detail()
        self._add_security_detail()
        self._add_performance_detail()
        self._add_accessibility_detail()
        
        # 推奨アクション
        self._add_recommendations()
        
        # PDFの生成
        self.doc.build(self.story)
        return self.output_filename
    
    def _add_title_page(self):
        """タイトルページの追加"""
        # タイトル
        title = Paragraph("Website Diagnosis Report<br/>ウェブサイト診断レポート", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 20*mm))
        
        # URL情報
        url_info = [
            ['URL:', self.results['url']],
            ['Date:', self.results['timestamp'][:19].replace('T', ' ')],
            ['Overall Score:', f"{self.results['overall_score']}/100"]
        ]
        
        url_table = Table(url_info, colWidths=[40*mm, 130*mm])
        url_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.japanese_font, 11),
            ('FONT', (0, 2), (0, 2), self.japanese_font, 11),
            ('FONT', (1, 2), (1, 2), self.japanese_font, 14),
            ('TEXTCOLOR', (1, 2), (1, 2), self._get_score_color(self.results['overall_score'])),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(url_table)
        self.story.append(Spacer(1, 30*mm))
        
        # スコア評価
        score_label = self._get_score_label(self.results['overall_score'])
        evaluation = Paragraph(
            f"<b>Evaluation: {score_label}</b>",
            self.styles['CustomHeading']
        )
        self.story.append(evaluation)
        
        self.story.append(PageBreak())
    
    def _add_summary_page(self):
        """サマリーページの追加"""
        # セクションタイトル
        title = Paragraph("Diagnosis Summary / 診断サマリー", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        # スコアテーブル
        score_data = [
            ['Category', 'Score', 'Rating', 'Issues'],
            [
                'SEO',
                f"{self.results['seo']['score']}/100",
                self._get_score_label(self.results['seo']['score']),
                str(len(self.results['seo']['issues']))
            ],
            [
                'Security',
                f"{self.results['security']['score']}/100",
                self._get_score_label(self.results['security']['score']),
                str(len(self.results['security']['issues']))
            ],
            [
                'Performance',
                f"{self.results['performance']['score']}/100",
                self._get_score_label(self.results['performance']['score']),
                str(len(self.results['performance']['issues']))
            ],
            [
                'Accessibility',
                f"{self.results['accessibility']['score']}/100",
                self._get_score_label(self.results['accessibility']['score']),
                str(len(self.results['accessibility']['issues']))
            ]
        ]
        
        score_table = Table(score_data, colWidths=[45*mm, 30*mm, 30*mm, 30*mm])
        score_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), self.japanese_font, 11),
            ('FONT', (0, 1), (-1, -1), self.japanese_font, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(score_table)
        self.story.append(Spacer(1, 10*mm))
        
        # グラフの追加
        try:
            chart_buffer = self._create_score_chart()
            img = Image(chart_buffer, width=160*mm, height=80*mm)
            self.story.append(img)
        except Exception as e:
            print(f"Chart generation error: {e}")
        
        self.story.append(PageBreak())
    
    def _add_seo_detail(self):
        """SEO詳細ページの追加"""
        seo = self.results['seo']
        
        # タイトル
        title = Paragraph("SEO Diagnosis Details / SEO診断詳細", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 3*mm))
        
        # スコア
        score_text = f"<b>Score: {seo['score']}/100</b> ({self._get_score_label(seo['score'])})"
        score_para = Paragraph(score_text, self.styles['CustomBody'])
        self.story.append(score_para)
        self.story.append(Spacer(1, 5*mm))
        
        # 主要指標
        subtitle = Paragraph("Key Metrics / 主要指標", self.styles['CustomSubHeading'])
        self.story.append(subtitle)
        
        title_text = seo.get('title', 'None')
        if len(title_text) > 60:
            title_text = title_text[:60] + '...'
        
        seo_data = [
            ['Item', 'Value'],
            ['Title', title_text],
            ['Title Length', f"{seo.get('title_length', 0)} chars"],
            ['Meta Description Length', f"{seo.get('meta_description_length', 0)} chars"],
            ['H1 Tags', f"{len(seo['headings']['h1'])} tags"],
            ['Images with alt', f"{seo['images_with_alt']}/{seo['total_images']}"],
            ['Internal Links', f"{seo['internal_links_count']} links"],
            ['External Links', f"{seo['external_links_count']} links"]
        ]
        
        seo_table = Table(seo_data, colWidths=[60*mm, 100*mm])
        seo_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), self.japanese_font, 10),
            ('FONT', (0, 1), (-1, -1), self.japanese_font, 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(seo_table)
        self.story.append(Spacer(1, 5*mm))
        
        # 問題点
        if seo['issues']:
            issues_title = Paragraph("Issues / 改善が必要な項目", self.styles['CustomSubHeading'])
            self.story.append(issues_title)
            
            for issue in seo['issues']:
                issue_text = f"• {issue}"
                issue_para = Paragraph(issue_text, self.styles['CustomBody'])
                self.story.append(issue_para)
                self.story.append(Spacer(1, 2*mm))
        else:
            no_issues = Paragraph("No issues found / 問題なし", self.styles['CustomBody'])
            self.story.append(no_issues)
        
        self.story.append(PageBreak())
    
    def _add_security_detail(self):
        """セキュリティ詳細ページの追加"""
        security = self.results['security']
        
        title = Paragraph("Security Diagnosis / セキュリティ診断詳細", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 3*mm))
        
        score_text = f"<b>Score: {security['score']}/100</b> ({self._get_score_label(security['score'])})"
        score_para = Paragraph(score_text, self.styles['CustomBody'])
        self.story.append(score_para)
        self.story.append(Spacer(1, 5*mm))
        
        subtitle = Paragraph("Security Status / セキュリティ状況", self.styles['CustomSubHeading'])
        self.story.append(subtitle)
        
        https_status = "Yes" if security['https'] else "No"
        security_data = [
            ['Item', 'Status'],
            ['HTTPS', https_status],
            ['Cookies', f"{security['cookies_count']} cookies"]
        ]
        
        security_table = Table(security_data, colWidths=[60*mm, 100*mm])
        security_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.japanese_font, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(security_table)
        self.story.append(Spacer(1, 5*mm))
        
        headers_title = Paragraph("Security Headers / セキュリティヘッダー", self.styles['CustomSubHeading'])
        self.story.append(headers_title)
        
        header_data = [['Header', 'Status']]
        for header, value in security['security_headers'].items():
            status = "Set" if value else "Not Set"
            header_data.append([header, status])
        
        header_table = Table(header_data, colWidths=[90*mm, 70*mm])
        header_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.japanese_font, 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(header_table)
        self.story.append(PageBreak())
    
    def _add_performance_detail(self):
        """パフォーマンス詳細ページの追加"""
        performance = self.results['performance']
        
        title = Paragraph("Performance Diagnosis / パフォーマンス診断詳細", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 3*mm))
        
        score_text = f"<b>Score: {performance['score']}/100</b> ({self._get_score_label(performance['score'])})"
        score_para = Paragraph(score_text, self.styles['CustomBody'])
        self.story.append(score_para)
        self.story.append(Spacer(1, 5*mm))
        
        subtitle = Paragraph("Performance Metrics / パフォーマンス指標", self.styles['CustomSubHeading'])
        self.story.append(subtitle)
        
        perf_data = [
            ['Item', 'Value'],
            ['Load Time', f"{performance['load_time']}s"],
            ['Page Size', f"{performance['page_size_kb']}KB"],
            ['Compression', performance['compression'] or 'None'],
            ['Cache Control', 'Yes' if performance['cache_control'] else 'No']
        ]
        
        perf_table = Table(perf_data, colWidths=[60*mm, 100*mm])
        perf_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.japanese_font, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(perf_table)
        self.story.append(Spacer(1, 5*mm))
        
        resources_title = Paragraph("Resources / リソース数", self.styles['CustomSubHeading'])
        self.story.append(resources_title)
        
        resources = performance['resources']
        resource_data = [
            ['Resource Type', 'Count'],
            ['Scripts', f"{resources['scripts']}"],
            ['Stylesheets', f"{resources['stylesheets']}"],
            ['Images', f"{resources['images']}"],
            ['Iframes', f"{resources['iframes']}"],
            ['Total', f"{sum(resources.values())}"]
        ]
        
        resource_table = Table(resource_data, colWidths=[60*mm, 100*mm])
        resource_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.japanese_font, 10),
            ('FONT', (0, -1), (-1, -1), self.japanese_font, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d5dbdb')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(resource_table)
        self.story.append(PageBreak())
    
    def _add_accessibility_detail(self):
        """アクセシビリティ詳細ページの追加"""
        accessibility = self.results['accessibility']
        
        title = Paragraph("Accessibility Diagnosis / アクセシビリティ診断詳細", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 3*mm))
        
        score_text = f"<b>Score: {accessibility['score']}/100</b> ({self._get_score_label(accessibility['score'])})"
        score_para = Paragraph(score_text, self.styles['CustomBody'])
        self.story.append(score_para)
        self.story.append(Spacer(1, 5*mm))
        
        subtitle = Paragraph("Accessibility Metrics / アクセシビリティ指標", self.styles['CustomSubHeading'])
        self.story.append(subtitle)
        
        access_data = [
            ['Item', 'Value'],
            ['Lang Attribute', accessibility['lang_attribute'] or 'None'],
            ['Images without alt', f"{accessibility['images_without_alt_count']}"],
            ['Form Elements', f"{accessibility['form_inputs_count']}"],
            ['Labeled Forms', f"{accessibility['inputs_with_labels']}"],
            ['ARIA Roles', f"{accessibility['aria_roles_count']}"],
            ['Empty Links', f"{accessibility['empty_links_count']}"]
        ]
        
        access_table = Table(access_data, colWidths=[60*mm, 100*mm])
        access_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.japanese_font, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(access_table)
        self.story.append(PageBreak())
    
    def _add_recommendations(self):
        """推奨アクションページの追加"""
        title = Paragraph("Priority Action Items / 優先改善項目", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 5*mm))
        
        # すべての問題を収集
        all_issues = []
        
        categories = [
            ('security', 'Security', self.results['security']),
            ('accessibility', 'Accessibility', self.results['accessibility']),
            ('seo', 'SEO', self.results['seo']),
            ('performance', 'Performance', self.results['performance'])
        ]
        
        categories_sorted = sorted(categories, key=lambda x: x[2]['score'])
        
        priority = 1
        for cat_key, cat_name, cat_data in categories_sorted:
            if cat_data['issues']:
                for issue in cat_data['issues'][:3]:
                    all_issues.append((priority, cat_name, issue))
                    priority += 1
        
        rec_data = [['Priority', 'Category', 'Issue']]
        
        for priority, category, issue in all_issues[:10]:
            priority_symbol = "HIGH" if priority <= 3 else ("MED" if priority <= 6 else "LOW")
            issue_short = issue[:60] + ('...' if len(issue) > 60 else '')
            rec_data.append([
                f"{priority_symbol} {priority}",
                category,
                issue_short
            ])
        
        rec_table = Table(rec_data, colWidths=[25*mm, 35*mm, 100*mm])
        rec_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), self.japanese_font, 10),
            ('FONT', (0, 1), (-1, -1), self.japanese_font, 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        self.story.append(rec_table)


def generate_pdf_report(results, output_filename=None):
    """
    診断結果からPDFレポートを生成
    
    Args:
        results: 診断結果の辞書
        output_filename: 出力ファイル名（オプション）
    
    Returns:
        生成されたPDFファイルのパス
    """
    generator = PDFReportGenerator(results, output_filename)
    return generator.generate()
