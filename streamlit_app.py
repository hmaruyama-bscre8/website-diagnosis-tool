#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウェブサイト診断ツール - Streamlit WebUI版（初心者向け説明付き）
Website Diagnosis Tool - Streamlit WebUI with Beginner-Friendly Explanations
"""

import streamlit as st
import json
from datetime import datetime
import plotly.graph_objects as go
from website_diagnosis_tool import WebsiteDiagnosisTool
from pdf_report_generator import create_english_pdf_report
from help_content import get_help_content
import os

# ページ設定
st.set_page_config(
    page_title="ビーズクリエイト ウェブサイト診断ツール | B's Cre8 Website Diagnosis Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ヘルプコンテンツを取得
help_content = get_help_content()

# カスタムCSS（ヘッダー・フッター追加、改善項目の表示改善）
st.markdown("""
<style>
    /* ヘッダースタイル */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 36px;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        font-size: 18px;
        margin-top: 10px;
        opacity: 0.95;
    }
    
    /* フッタースタイル */
    .footer-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin-top: 50px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .footer-text {
        font-size: 14px;
        margin: 5px 0;
    }
    
    /* ダウンロードヘッダースタイル */
    .download-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* スコアカードのスタイル */
    .score-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .score-excellent {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .score-good {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .score-average {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    .score-poor {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    
    /* 改善項目のスタイル（修正版：白背景・濃い文字・赤い左ボーダー） */
    .issue-box {
        background-color: white;
        border-left: 4px solid #e74c3c;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 5px;
        color: #2c3e50;
        font-weight: 500;
    }
    
    /* 正常項目のスタイル */
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 5px;
        color: #155724;
    }
    
    /* ヘルプボックスのスタイル */
    .help-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .help-title {
        font-size: 18px;
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 10px;
    }
    
    .help-icon {
        font-size: 24px;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー（ビーズクリエイト追加）
st.markdown("""
<div class="header-container">
    <div class="header-title">🔍 ビーズクリエイト ウェブサイト診断ツール</div>
    <div class="header-subtitle">B's Cre8 (ビーズクリエイト) Website Diagnosis Tool</div>
</div>
""", unsafe_allow_html=True)

# サイドバー（ビーズクリエイト追加）
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                color: white;
                margin-bottom: 20px;">
        <h3 style="margin: 0; font-size: 20px;">ビーズクリエイト</h3>
        <p style="margin: 5px 0 0 0; font-size: 14px;">B's Cre8</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # 診断項目の説明
    st.markdown("### 📋 診断項目")
    
    with st.expander("🔍 SEO（検索エンジン最適化）"):
        st.write(help_content['seo']['description'])
    
    with st.expander("🔒 セキュリティ（安全性）"):
        st.write(help_content['security']['description'])
    
    with st.expander("⚡ パフォーマンス（表示速度）"):
        st.write(help_content['performance']['description'])
    
    with st.expander("♿ アクセシビリティ（利用しやすさ)"):
        st.write(help_content['accessibility']['description'])
    
    st.markdown("---")
    st.markdown("### 📚 使い方")
    st.markdown("""
    1. URLを入力
    2. 「診断開始」をクリック
    3. 結果を確認
    4. PDFまたはJSONでダウンロード
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ ヘルプ")
    if st.checkbox("初心者向け詳細説明を表示"):
        st.session_state['show_help'] = True
    else:
        st.session_state['show_help'] = False

# メインコンテンツ
st.markdown("## 🌐 ウェブサイトを診断")

# URL入力
url = st.text_input(
    "診断したいウェブサイトのURLを入力してください",
    placeholder="https://example.com",
    help="診断したいウェブサイトの完全なURLを入力してください（例: https://www.example.com）"
)

# 診断ボタン
if st.button("🚀 診断開始", type="primary", use_container_width=True):
    if not url:
        st.error("❌ URLを入力してください")
    else:
        # 診断実行
        with st.spinner("🔄 診断中... しばらくお待ちください"):
            try:
                # 診断ツール実行
                tool = WebsiteDiagnosisTool(url)
                result = tool.diagnose()
                
                # セッションステートに保存
                st.session_state['diagnosis_result'] = result
                st.session_state['diagnosis_url'] = url
                
                st.success("✅ 診断が完了しました！")
                
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")

# 診断結果の表示
if 'diagnosis_result' in st.session_state:
    result = st.session_state['diagnosis_result']
    
    st.markdown("---")
    st.markdown("## 📊 診断結果")
    
    # 総合スコア表示
    overall_score = result.get('overall_score', 0)
    
    # スコアに応じたクラスとラベル
    if overall_score >= 80:
        score_class = "score-excellent"
        score_label = "優秀 (Excellent)"
        score_emoji = "🌟"
    elif overall_score >= 60:
        score_class = "score-good"
        score_label = "良好 (Good)"
        score_emoji = "👍"
    elif overall_score >= 40:
        score_class = "score-average"
        score_label = "平均 (Average)"
        score_emoji = "📊"
    else:
        score_class = "score-poor"
        score_label = "要改善 (Poor)"
        score_emoji = "⚠️"
    
    st.markdown(f"""
    <div class="score-card {score_class}">
        <h1>{score_emoji} {overall_score:.1f} / 100</h1>
        <h3>{score_label}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # カテゴリ別スコア
    st.markdown("### 📈 カテゴリ別スコア")
    
    scores = result.get('scores', {})
    
    # レーダーチャート作成
    categories = ['SEO', 'セキュリティ', 'パフォーマンス', 'アクセシビリティ']
    score_values = [
        scores.get('seo', 0),
        scores.get('security', 0),
        scores.get('performance', 0),
        scores.get('accessibility', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=score_values,
        theta=categories,
        fill='toself',
        name='スコア',
        line_color='rgb(102, 126, 234)',
        fillcolor='rgba(102, 126, 234, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 4カラムでスコア表示
    col1, col2, col3, col4 = st.columns(4)
    
    def get_score_class_name(score):
        if score >= 80:
            return "score-excellent"
        elif score >= 60:
            return "score-good"
        elif score >= 40:
            return "score-average"
        else:
            return "score-poor"
    
    def get_score_emoji(score):
        if score >= 80:
            return "🌟"
        elif score >= 60:
            return "👍"
        elif score >= 40:
            return "📊"
        else:
            return "⚠️"
    
    with col1:
        seo_score = scores.get('seo', 0)
        st.markdown(f"""
        <div class="score-card {get_score_class_name(seo_score)}">
            <h3>{get_score_emoji(seo_score)} SEO</h3>
            <h2>{seo_score:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        security_score = scores.get('security', 0)
        st.markdown(f"""
        <div class="score-card {get_score_class_name(security_score)}">
            <h3>{get_score_emoji(security_score)} セキュリティ</h3>
            <h2>{security_score:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        performance_score = scores.get('performance', 0)
        st.markdown(f"""
        <div class="score-card {get_score_class_name(performance_score)}">
            <h3>{get_score_emoji(performance_score)} パフォーマンス</h3>
            <h2>{performance_score:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        accessibility_score = scores.get('accessibility', 0)
        st.markdown(f"""
        <div class="score-card {get_score_class_name(accessibility_score)}">
            <h3>{get_score_emoji(accessibility_score)} アクセシビリティ</h3>
            <h2>{accessibility_score:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # 詳細結果
    st.markdown("---")
    st.markdown("## 📋 詳細診断結果")
    
    # タブで各カテゴリを表示
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 SEO", "🔒 セキュリティ", "⚡ パフォーマンス", "♿ アクセシビリティ"])
    
    with tab1:
        st.markdown("### SEO診断結果")
        seo_data = result.get('seo', {})
        
        # 改善が必要な項目
        issues = seo_data.get('issues', [])
        explanations = seo_data.get('explanations', [])
        
        if issues:
            st.markdown("#### ⚠️ 改善が必要な項目")
            for idx, issue in enumerate(issues):
                st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
                
                # 説明を表示（初心者モードの場合）
                if st.session_state.get('show_help', False) and idx < len(explanations):
                    exp = explanations[idx]
                    with st.expander(f"💡 「{exp['issue']}」について詳しく"):
                        st.markdown(f"**📝 これは何？**\n{exp['explanation']['what']}")
                        st.markdown(f"**💡 なぜ重要？**\n{exp['explanation']['why']}")
                        st.markdown(f"**🔧 どうすればいい？**\n{exp['explanation']['how']}")
        
        # 正常な項目
        success = seo_data.get('success', [])
        if success:
            st.markdown("#### ✅ 正常な項目")
            for item in success:
                st.markdown(f'<div class="success-box">✅ {item}</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### セキュリティ診断結果")
        security_data = result.get('security', {})
        
        # 改善が必要な項目
        issues = security_data.get('issues', [])
        explanations = security_data.get('explanations', [])
        
        if issues:
            st.markdown("#### ⚠️ 改善が必要な項目")
            for idx, issue in enumerate(issues):
                st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
                
                # 説明を表示（初心者モードの場合）
                if st.session_state.get('show_help', False) and idx < len(explanations):
                    exp = explanations[idx]
                    with st.expander(f"💡 「{exp['issue']}」について詳しく"):
                        if 'risk' in exp['explanation']:
                            st.error(exp['explanation']['risk'])
                        st.markdown(f"**📝 これは何？**\n{exp['explanation']['what']}")
                        st.markdown(f"**💡 なぜ重要？**\n{exp['explanation']['why']}")
                        st.markdown(f"**🔧 どうすればいい？**\n{exp['explanation']['how']}")
        
        # 正常な項目
        success = security_data.get('success', [])
        if success:
            st.markdown("#### ✅ 正常な項目")
            for item in success:
                st.markdown(f'<div class="success-box">✅ {item}</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### パフォーマンス診断結果")
        performance_data = result.get('performance', {})
        
        # 改善が必要な項目
        issues = performance_data.get('issues', [])
        explanations = performance_data.get('explanations', [])
        
        if issues:
            st.markdown("#### ⚠️ 改善が必要な項目")
            for idx, issue in enumerate(issues):
                st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
                
                # 説明を表示（初心者モードの場合）
                if st.session_state.get('show_help', False) and idx < len(explanations):
                    exp = explanations[idx]
                    with st.expander(f"💡 「{exp['issue']}」について詳しく"):
                        st.markdown(f"**📝 これは何？**\n{exp['explanation']['what']}")
                        st.markdown(f"**💡 なぜ重要？**\n{exp['explanation']['why']}")
                        st.markdown(f"**🔧 どうすればいい？**\n{exp['explanation']['how']}")
        
        # 正常な項目
        success = performance_data.get('success', [])
        if success:
            st.markdown("#### ✅ 正常な項目")
            for item in success:
                st.markdown(f'<div class="success-box">✅ {item}</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### アクセシビリティ診断結果")
        accessibility_data = result.get('accessibility', {})
        
        # 改善が必要な項目
        issues = accessibility_data.get('issues', [])
        explanations = accessibility_data.get('explanations', [])
        
        if issues:
            st.markdown("#### ⚠️ 改善が必要な項目")
            for idx, issue in enumerate(issues):
                st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
                
                # 説明を表示（初心者モードの場合）
                if st.session_state.get('show_help', False) and idx < len(explanations):
                    exp = explanations[idx]
                    with st.expander(f"💡 「{exp['issue']}」について詳しく"):
                        st.markdown(f"**📝 これは何？**\n{exp['explanation']['what']}")
                        st.markdown(f"**💡 なぜ重要？**\n{exp['explanation']['why']}")
                        st.markdown(f"**🔧 どうすればいい？**\n{exp['explanation']['how']}")
        
        # 正常な項目
        success = accessibility_data.get('success', [])
        if success:
            st.markdown("#### ✅ 正常な項目")
            for item in success:
                st.markdown(f'<div class="success-box">✅ {item}</div>', unsafe_allow_html=True)
    
    # ダウンロードセクション（目立つデザイン）
    st.markdown("---")
    st.markdown("""
    <div class="download-header">
        <h2 style="margin: 0;">💾 レポートダウンロード</h2>
        <p style="margin: 10px 0 0 0; font-size: 14px;">診断結果を保存して活用しましょう!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_json, col_pdf = st.columns(2)
    
    with col_json:
        # JSON形式でダウンロード
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 JSON形式でダウンロード",
            data=json_str,
            file_name=f"diagnosis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            help="開発者向け:詳細な診断データをJSON形式でダウンロードします"
        )
    
    with col_pdf:
        # PDFレポート生成
        if st.button("📊 PDFレポートを生成 (English)", type="primary", use_container_width=True):
            try:
                with st.spinner("📄 PDFレポートを生成中..."):
                    # PDFファイル生成
                    pdf_path = create_english_pdf_report(result, output_dir='/tmp')
                    
                    # PDFファイルを読み込み
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    # ダウンロードボタン
                    st.download_button(
                        label="📥 PDFをダウンロード",
                        data=pdf_data,
                        file_name=f"bscre8_diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.success("✅ PDFレポートが生成されました！")
                    
            except Exception as e:
                st.error(f"❌ PDFの生成に失敗しました: {str(e)}")

# フッター（ビーズクリエイト追加）
st.markdown("""
<div class="footer-container">
    <div class="footer-text"><strong>ビーズクリエイト | B's Cre8</strong></div>
    <div class="footer-text">Website Diagnosis Tool | ウェブサイト診断ツール</div>
    <div class="footer-text">📧 お問い合わせ: info@bscre8.com | 🌐 https://www.bscre8.com/</div>
    <div class="footer-text" style="margin-top: 10px; font-size: 12px; opacity: 0.8;">
        &copy; 2024 B's Cre8 (ビーズクリエイト). All rights reserved.
    </div>
</div>
""", unsafe_allow_html=True)
