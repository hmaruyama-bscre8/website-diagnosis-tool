#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウェブサイト診断ツール - Streamlit UI版
"""

import streamlit as st
import sys
from website_diagnosis_tool import WebsiteDiagnosisTool
import json
from datetime import datetime
import plotly.graph_objects as go

# ページ設定
st.set_page_config(
    page_title="ウェブサイト診断ツール",
    page_icon="🔍",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .score-card {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
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
        background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%);
        color: #333;
    }
    .score-poor {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
    }
    .issue-box {
        padding: 1rem;
        border-left: 4px solid #ff6b6b;
        background-color: #ffe0e0;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .success-box {
        padding: 1rem;
        border-left: 4px solid #51cf66;
        background-color: #d3f9d8;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def get_score_class(score):
    """スコアに応じたCSSクラスを返す"""
    if score >= 80:
        return "score-excellent"
    elif score >= 60:
        return "score-good"
    elif score >= 40:
        return "score-average"
    else:
        return "score-poor"

def get_score_emoji(score):
    """スコアに応じた絵文字を返す"""
    if score >= 80:
        return "🌟"
    elif score >= 60:
        return "👍"
    elif score >= 40:
        return "⚠️"
    else:
        return "❌"

def create_radar_chart(results):
    """レーダーチャートの作成"""
    categories = ['SEO', 'セキュリティ', 'パフォーマンス', 'アクセシビリティ']
    values = [
        results['seo']['score'],
        results['security']['score'],
        results['performance']['score'],
        results['accessibility']['score']
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line=dict(color='#1f77b4', width=2)
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
    
    return fig

def create_gauge_chart(score, title):
    """ゲージチャートの作成"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 60], 'color': "gray"},
                {'range': [60, 80], 'color': "lightblue"},
                {'range': [80, 100], 'color': "royalblue"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

# メインUI
st.markdown('<div class="main-header">🔍 ウェブサイト診断ツール</div>', unsafe_allow_html=True)

st.markdown("""
このツールは、ウェブサイトの以下の項目を包括的に診断します：
- 📊 **SEO**: メタタグ、見出し構造、画像最適化など
- 🔒 **セキュリティ**: HTTPS、セキュリティヘッダー、SSL証明書など
- ⚡ **パフォーマンス**: 読み込み速度、ページサイズ、リソース数など
- ♿ **アクセシビリティ**: alt属性、フォームラベル、ARIA属性など
""")

# URL入力
url = st.text_input("診断するURLを入力してください", placeholder="https://example.com")

# 診断ボタン
if st.button("🚀 診断を開始", type="primary"):
    if not url:
        st.error("❌ URLを入力してください")
    else:
        # URLの整形
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # プログレスバーの表示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 診断の実行
            status_text.text("🔍 ページを取得中...")
            progress_bar.progress(10)
            
            tool = WebsiteDiagnosisTool(url)
            
            status_text.text("📊 SEO診断中...")
            progress_bar.progress(30)
            
            status_text.text("🔒 セキュリティ診断中...")
            progress_bar.progress(50)
            
            status_text.text("⚡ パフォーマンス診断中...")
            progress_bar.progress(70)
            
            status_text.text("♿ アクセシビリティ診断中...")
            progress_bar.progress(90)
            
            results = tool.run_diagnosis()
            
            progress_bar.progress(100)
            status_text.text("✅ 診断完了！")
            
            if results:
                st.success("🎉 診断が完了しました！")
                
                # 総合スコアの表示
                st.markdown("---")
                st.markdown("## 📈 総合診断結果")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    overall_score = results['overall_score']
                    score_class = get_score_class(overall_score)
                    score_emoji = get_score_emoji(overall_score)
                    
                    st.markdown(f"""
                    <div class="score-card {score_class}">
                        <h1>{score_emoji}</h1>
                        <h1>{overall_score}/100</h1>
                        <p>総合スコア</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.plotly_chart(create_radar_chart(results), use_container_width=True)
                
                # 各カテゴリの詳細
                st.markdown("---")
                st.markdown("## 📊 詳細診断結果")
                
                tabs = st.tabs(["📊 SEO", "🔒 セキュリティ", "⚡ パフォーマンス", "♿ アクセシビリティ"])
                
                # SEOタブ
                with tabs[0]:
                    seo = results['seo']
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.plotly_chart(create_gauge_chart(seo['score'], "SEOスコア"), use_container_width=True)
                    
                    with col2:
                        st.markdown("### 主要な指標")
                        st.write(f"**タイトル:** {seo.get('title', 'なし')}")
                        st.write(f"**タイトル長:** {seo.get('title_length', 0)}文字")
                        st.write(f"**メタディスクリプション長:** {seo.get('meta_description_length', 0)}文字")
                        st.write(f"**H1タグ数:** {len(seo['headings']['h1'])}個")
                        st.write(f"**画像のalt属性率:** {seo['images_with_alt']}/{seo['total_images']}")
                        st.write(f"**内部リンク数:** {seo['internal_links_count']}個")
                        st.write(f"**外部リンク数:** {seo['external_links_count']}個")
                    
                    if seo['issues']:
                        st.markdown("### ⚠️ 改善が必要な項目")
                        for issue in seo['issues']:
                            st.markdown(f'<div class="issue-box">• {issue}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ 問題は見つかりませんでした</div>', unsafe_allow_html=True)
                    
                    with st.expander("📋 見出し構造の詳細"):
                        for level, headings in seo['headings'].items():
                            if headings:
                                st.write(f"**{level.upper()}:** {len(headings)}個")
                                for heading in headings[:5]:  # 最初の5個のみ表示
                                    st.write(f"  - {heading}")
                
                # セキュリティタブ
                with tabs[1]:
                    security = results['security']
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.plotly_chart(create_gauge_chart(security['score'], "セキュリティスコア"), use_container_width=True)
                    
                    with col2:
                        st.markdown("### セキュリティ状況")
                        st.write(f"**HTTPS使用:** {'✅ はい' if security['https'] else '❌ いいえ'}")
                        st.write(f"**Cookie数:** {security['cookies_count']}個")
                        
                        st.markdown("#### セキュリティヘッダー")
                        for header, value in security['security_headers'].items():
                            status = "✅" if value else "❌"
                            st.write(f"{status} {header}")
                    
                    if security['issues']:
                        st.markdown("### ⚠️ 改善が必要な項目")
                        for issue in security['issues']:
                            st.markdown(f'<div class="issue-box">• {issue}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ 問題は見つかりませんでした</div>', unsafe_allow_html=True)
                
                # パフォーマンスタブ
                with tabs[3]:
                    performance = results['performance']
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.plotly_chart(create_gauge_chart(performance['score'], "パフォーマンススコア"), use_container_width=True)
                    
                    with col2:
                        st.markdown("### パフォーマンス指標")
                        st.write(f"**読み込み時間:** {performance['load_time']}秒")
                        st.write(f"**ページサイズ:** {performance['page_size_kb']}KB")
                        st.write(f"**圧縮:** {performance['compression'] or 'なし'}")
                        
                        st.markdown("#### リソース数")
                        resources = performance['resources']
                        st.write(f"- スクリプト: {resources['scripts']}個")
                        st.write(f"- スタイルシート: {resources['stylesheets']}個")
                        st.write(f"- 画像: {resources['images']}個")
                        st.write(f"- iframe: {resources['iframes']}個")
                    
                    if performance['issues']:
                        st.markdown("### ⚠️ 改善が必要な項目")
                        for issue in performance['issues']:
                            st.markdown(f'<div class="issue-box">• {issue}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ 問題は見つかりませんでした</div>', unsafe_allow_html=True)
                
                # アクセシビリティタブ
                with tabs[3]:
                    accessibility = results['accessibility']
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.plotly_chart(create_gauge_chart(accessibility['score'], "アクセシビリティスコア"), use_container_width=True)
                    
                    with col2:
                        st.markdown("### アクセシビリティ指標")
                        st.write(f"**言語属性:** {accessibility['lang_attribute'] or 'なし'}")
                        st.write(f"**alt属性なしの画像:** {accessibility['images_without_alt_count']}個")
                        st.write(f"**フォーム要素:** {accessibility['form_inputs_count']}個")
                        st.write(f"**ラベル付きフォーム要素:** {accessibility['inputs_with_labels']}個")
                        st.write(f"**ARIA role使用:** {accessibility['aria_roles_count']}個")
                        st.write(f"**空リンク:** {accessibility['empty_links_count']}個")
                    
                    if accessibility['issues']:
                        st.markdown("### ⚠️ 改善が必要な項目")
                        for issue in accessibility['issues']:
                            st.markdown(f'<div class="issue-box">• {issue}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">✅ 問題は見つかりませんでした</div>', unsafe_allow_html=True)
                    
                    with st.expander("🏛️ ランドマーク要素の使用状況"):
                        for landmark, count in accessibility['landmarks'].items():
                            st.write(f"**{landmark}:** {count}個")
                
                # JSONダウンロード
                st.markdown("---")
                st.markdown("## 💾 診断結果のダウンロード")
                
                json_str = json.dumps(results, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 JSON形式でダウンロード",
                    data=json_str,
                    file_name=f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🔍 ウェブサイト診断ツール v1.0</p>
    <p>SEO、セキュリティ、パフォーマンス、アクセシビリティを包括的に診断</p>
</div>
""", unsafe_allow_html=True)
